import json
import os
import uuid
from typing import Any

from PIL import Image
from sqlalchemy.orm import Session

from ... import crud, schemas
from .book_metadata_client import BookMetadataClient


def _merge_metadata(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    """Fill empty/missing fields in primary with values from secondary."""
    merged = dict(primary)
    for key, value in secondary.items():
        if value and not merged.get(key):
            merged[key] = value
    return merged


# --------------------------------------------------------------------------
# External metadata (ISBN / title lookup)
# --------------------------------------------------------------------------
def lookup_book_metadata_by_isbn(isbn: str) -> dict[str, Any]:
    """
    Resolve ISBN via EasyCB (NL), then Google Books, then Open Library, then Wikipedia.
    EasyCB values win on conflict; Google Books fills in missing fields.
    Raises LookupError if no source returns a title.
    """
    book: dict[str, Any] = {}
    isbn = isbn.strip()
    client = BookMetadataClient()

    try:
        easycb_book, response = client.easycb_by_isbn(isbn)
        if response is not None and response != 200:
            print(f"EasyCB API non-200 response: {response}")
        book = easycb_book
    except Exception as e:
        print(f"EasyCB API exception: {e}")

    try:
        google_book, response = client.google_books_by_isbn(isbn)
        if response is not None and response != 200:
            print(f"Google Books API non-200 response: {response}")
        if google_book:
            book = _merge_metadata(book, google_book)
    except Exception as e:
        print(f"Google Books API exception: {e}")

    try:
        if not book.get("Title"):
            ol_book, response = client.open_library_by_isbn(isbn)
            if response is not None and response != 200:
                print(f"Open Library API non-200 response: {response}")
            if ol_book:
                book = _merge_metadata(book, ol_book)
    except Exception as e:
        print(f"Open Library API exception: {e}")

    try:
        if not book.get("Title"):
            wiki_book, response = client.open_wiki_by_isbn(isbn)
            if response != 200:
                print(f"Wikipedia API non-200 response: {response}")
            if wiki_book:
                book = _merge_metadata(book, wiki_book)
    except Exception as e:
        print(f"Wikipedia API exception: {e}")

    if not book.get("Title"):
        raise LookupError(f"Book with isbn {isbn} not found!")
    return book


# --------------------------------------------------------------------------
# Cover download (EasyCB)
# --------------------------------------------------------------------------
BOOK_IMAGES_DIR = "./static/bookImages/"


def download_easycb_cover(db: Session, book_id: int, cover_filename: str) -> bool:
    """
    Download a cover JPG from EasyCB, save it + thumbnail, register in DB.
    Mirrors the manual upload flow in routers/files.py. Failures are logged
    and never propagated — adding a book must succeed even if cover fetch fails.
    """
    if not cover_filename:
        return False
    try:
        client = BookMetadataClient()
        content, status_code = client.fetch_easycb_cover(cover_filename)
        if not content:
            print(f"EasyCB cover {cover_filename} not retrieved (status {status_code})")
            return False
        dbpath = f"{book_id}_{uuid.uuid4()}"
        basepath = os.path.join(BOOK_IMAGES_DIR, dbpath)
        filepath = basepath + ".jpg"
        thumbpath = basepath + "_thumbnail.jpg"
        os.makedirs(BOOK_IMAGES_DIR, exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(content)
        im = Image.open(filepath)
        im.thumbnail((300, 300), resample=Image.BOX)
        im.save(thumbpath, format="JPEG", quality=65)
        crud.addImage(db, schemas.bookImageBase(bookId=book_id, filename=dbpath))
        return True
    except Exception as e:
        print(f"EasyCB cover download failed for book {book_id}: {e}")
        return False


# --------------------------------------------------------------------------
# Form → schema (book fields)
# --------------------------------------------------------------------------
def book_create_from_form(form) -> schemas.BookCreate:
    return schemas.BookCreate(
        title=form.title,
        author=form.author,
        summary=form.summary,
        genre=form.genre,
        library=form.library,
        shelf=form.shelf,
        collection=form.collection,
        notes=form.notes,
        ISBN=form.ISBN,
        owned=form.owned,
        ebook=form.ebook,
        customField1=form.customField1,
        customField2=form.customField2,
        withdrawn=form.withdrawn,
        coverFilename=getattr(form, "coverFilename", None),
    )


def book_update_from_form(book_id, form) -> schemas.Book:
    return schemas.Book(
        id=book_id,
        title=form.title,
        author=form.author,
        summary=form.summary,
        genre=form.genre,
        library=form.library,
        shelf=form.shelf,
        collection=form.collection,
        notes=form.notes,
        ISBN=form.ISBN,
        owned=form.owned,
        ebook=form.ebook,
        customField1=form.customField1,
        customField2=form.customField2,
        withdrawn=form.withdrawn,
    )


# --------------------------------------------------------------------------
# Search serialization
# --------------------------------------------------------------------------
def search_books_json(db: Session, title: str, author: str, skip: int, only_ebooks: bool, no_ebooks: bool) -> str | None:
    from fastapi.encoders import jsonable_encoder

    try:
        books = crud.searchBooks(db, str(title), str(author), int(
            skip), bool(only_ebooks), bool(no_ebooks))
        result = json.dumps(jsonable_encoder(books[0]))
        data: dict[str, Any] = {"result": result, "count": books[1]}
        return json.dumps(jsonable_encoder(data))
    except Exception as e:
        print(e)
        return None


def search_books_by_author_json(
    db: Session, author: str, skip: int, only_ebooks: bool, no_ebooks: bool
) -> str | None:
    from fastapi.encoders import jsonable_encoder

    try:
        books = jsonable_encoder(crud.searchBooksbyAuthor(
            db, str(author), int(skip), bool(only_ebooks), bool(no_ebooks)))
        result = json.dumps(jsonable_encoder(books[0]))
        data: dict[str, Any] = {"result": result, "count": books[1]}
        return json.dumps(jsonable_encoder(data))
    except Exception as e:
        print(e)
        return None


def search_books_by_title_json(
    db: Session, title: str, skip: int, only_ebooks: bool, no_ebooks: bool
) -> str | None:
    from fastapi.encoders import jsonable_encoder

    try:
        books = jsonable_encoder(crud.searchBooksbyTitle(
            db, str(title), int(skip), bool(only_ebooks), bool(no_ebooks)))
        result = json.dumps(jsonable_encoder(books[0]))
        data: dict[str, Any] = {"result": result, "count": books[1]}
        return json.dumps(jsonable_encoder(data))
    except Exception as e:
        print(e)
        return None


def book_create_from_isbn_metadata(book: dict[str, Any], isbn: str) -> schemas.BookCreate:
    # Map fields from metadata client to BookCreate schema
    title = book.get("Title", "")
    author = book.get("Author", "")
    summary = book.get("Summary", "")
    # Genre from categories
    genre = book.get("Categories", "")
    # Notes: we can include page count, average rating, ratings count, language
    notes_parts = []
    if book.get("PageCount") and book["PageCount"] not in ("0", "", None):
        notes_parts.append(f"Pages: {book['PageCount']}")
    if book.get("AverageRating"):
        notes_parts.append(f"Avg rating: {book['AverageRating']}")
    if book.get("RatingsCount"):
        notes_parts.append(f"Ratings: {book['RatingsCount']}")
    if book.get("Language"):
        notes_parts.append(f"Language: {book['Language']}")
    notes = " | ".join(notes_parts) if notes_parts else ""
    # Custom fields: Publisher -> customField1, PublishedDate -> customField2
    customField1 = book.get("Publisher", "")
    customField2 = book.get("PublishedDate", "")
    return schemas.BookCreate(
        title=title,
        author=author,
        summary=summary,
        genre=genre,
        ISBN=isbn,
        notes=notes,
        customField1=customField1,
        customField2=customField2,
        coverFilename=book.get("CoverFilename") or None,
        # owned, withdrawn, ebook, library, shelf, collection left as defaults (False/None)
    )
