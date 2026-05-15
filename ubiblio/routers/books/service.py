import json
from typing import Any

from sqlalchemy.orm import Session

from ... import crud, schemas
from .book_metadata_client import BookMetadataClient


# --------------------------------------------------------------------------
# External metadata (ISBN / title lookup)
# --------------------------------------------------------------------------
def lookup_book_metadata_by_isbn(isbn: str) -> dict[str, Any]:
    """
    Resolve ISBN to Title/Author/Summary via Google Books, then Open Library, then Wikipedia.
    Raises LookupError if no source returns data.
    """
    book: dict[str, Any] = {}
    isbn = isbn.strip()
    response = 0
    client = BookMetadataClient()

    try:
        book, response = client.google_books_by_isbn(isbn)
        if response is not None and response != 200:
            print("Google Books API failed with response: ")
            print(response)
    except Exception:
        print("Google Books API failed with response: ")
        print(response)

    try:
        if len(book) == 0:
            book, response = client.open_library_by_isbn(isbn)
            if response is not None and response != 200:
                print("Open Library API failed with response: ")
                print(response)
    except Exception as e:
        print("Open Library API failed with response: ")
        print(e)

    try:
        if len(book) == 0:
            book, response = client.open_wiki_by_isbn(isbn)
            if response != 200:
                print("Wikipedia API failed with response: ")
                print(response)
    except Exception as e:
        print("Wikipedia API failed with response: ")
        print(e)

    if len(book) == 0:
        raise LookupError(f"Book with isbn {isbn} not found!")
    return book


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
        # owned, withdrawn, ebook, library, shelf, collection left as defaults (False/None)
    )
