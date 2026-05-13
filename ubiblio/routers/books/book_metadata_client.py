import json
import time

import requests

from ...vars import GOOGLE_BOOKS_API_KEY


class BookMetadataClient:
    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
    OPEN_LIBRARY_API = "https://openlibrary.org"
    OPEN_WIKI_API = "https://en.wikipedia.org/api/rest_v1/data/citation/mediawiki/"
    USER_AGENT = "ubiblio_bot/1.0 (https://github.com/seanboyce/ubiblio;)"

    def google_books_by_isbn(self, isbn: str) -> tuple[dict[str, str], int | None]:
        if not GOOGLE_BOOKS_API_KEY:
            return {}, None
        response = requests.get(
            self.GOOGLE_BOOKS_API,
            params={"q": f"+isbn:{isbn}", "key": GOOGLE_BOOKS_API_KEY})
        if response.ok:
            raw_book = json.loads(response.text)["items"][0]["volumeInfo"]
            book = {}
            book["Title"] = raw_book.get("title", "")
            # Author: join if multiple
            authors = raw_book.get("authors", [])
            book["Author"] = ", ".join(authors) if authors else ""
            book["Summary"] = raw_book.get("description", "")
            # Publisher -> customField1
            book["Publisher"] = raw_book.get("publisher", "")
            # Published date -> customField2
            book["PublishedDate"] = raw_book.get("publishedDate", "")
            # Page count -> notes (or we could add a field, but notes is flexible)
            book["PageCount"] = str(raw_book.get("pageCount", ""))
            # Categories -> genre (join)
            categories = raw_book.get("categories", [])
            book["Categories"] = ", ".join(categories) if categories else ""
            # Average rating -> we can store in notes as well, or custom field if needed
            book["AverageRating"] = str(raw_book.get("averageRating", ""))
            # Ratings count
            book["RatingsCount"] = str(raw_book.get("ratingsCount", ""))
            # Language
            book["Language"] = raw_book.get("language", "")
            # Image links (thumbnail) maybe not needed now
            return book, 200
        return {}, response.status_code

    def open_library_by_isbn(self, isbn: str) -> tuple[dict[str, str], int]:
        url = self.OPEN_LIBRARY_API + f"/api/books?bibkeys={isbn}&format=json&jscmd=details"
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept-Encoding": "gzip",
        }
        response = requests.get(url, headers=headers)
        if response.ok:
            data = response.json()
            entry = data.get(isbn, {})
            book_details = entry.get("details", {})
            book = {
                "Title": book_details.get("title", ""),
                "Summary": book_details.get("description", {}).get("value", ""),
            }
            authors = book_details.get("authors", [])
            if len(authors) > 0 and "name" in authors[0]:
                book["Author"] = authors[0]["name"]
            else:
                book["Author"] = ""
            # Only return the book if it has a title — otherwise treat as not found
            # so the fallback chain (e.g. Wikipedia) can still run.
            if not book.get("Title"):
                return {}, response.status_code
            return book, 200
        else:
            return {}, response.status_code

    def open_wiki_by_isbn(self, isbn: str) -> tuple[dict[str, str], int]:
        url = self.OPEN_WIKI_API + "isbn/" + str(isbn) + ".json"
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept-Encoding": "gzip",
        }
        response = requests.get(url, headers=headers)
        if response.ok:
            raw = json.loads(response.text)
            if not raw:
                return {}, response.status_code
            raw_book = raw[0]
            if not raw_book.get("title"):
                return {}, response.status_code
            book = {}
            book["Title"] = raw_book["title"]
            raw_author = raw_book.get("author", [[]])
            author = " ".join(raw_author[0]).strip()
            book["Author"] = author
            book["Summary"] = ""
            return book, 200
        else:
            return {}, response.status_code