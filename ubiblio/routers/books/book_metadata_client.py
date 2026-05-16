import json
import os
import time

import requests

from ...vars import GOOGLE_BOOKS_API_KEY


class BookMetadataClient:
    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
    OPEN_LIBRARY_API = "https://openlibrary.org"
    OPEN_WIKI_API = "https://en.wikipedia.org/api/rest_v1/data/citation/mediawiki/"
    EASYCB_API = "https://easycbapi.nl"
    USER_AGENT = "ubiblio_bot/1.0 (https://github.com/seanboyce/ubiblio;)"
    EASYCB_CONTACT_DEFAULT = "joost.betten@gmail.com"

    @classmethod
    def easycb_contact(cls) -> str:
        return os.environ.get("EASYCB_CONTACT", cls.EASYCB_CONTACT_DEFAULT)

    def easycb_by_isbn(self, isbn: str) -> tuple[dict[str, str], int | None]:
        """
        Fetch metadata from easycbapi.nl (Centraal Boekhuis / TitelBank).
        Response body is plain text, one ``key:value`` per line.
        """
        url = f"{self.EASYCB_API}/isbn/{isbn}"
        headers = {
            "contact": self.easycb_contact(),
            "User-Agent": self.USER_AGENT,
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
        except requests.RequestException as e:
            print(f"EasyCB API request failed: {e}")
            return {}, None
        if not response.ok:
            return {}, response.status_code

        raw: dict[str, list[str]] = {}
        for line in response.text.splitlines():
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if not key:
                continue
            raw.setdefault(key, []).append(value)

        def first(key: str) -> str:
            values = raw.get(key, [])
            return values[0] if values else ""

        title = first("title")
        if not title:
            return {}, response.status_code

        # Summary: prefer flap/synopsis-style TextType (03 = description, 02 = short description, 05 = jacket).
        summary = ""
        text_types = raw.get("CollateralDetail.TextContent.TextType", [])
        text_values = raw.get("CollateralDetail.TextContent.Text", [])
        if text_values:
            preferred = {"03": None, "02": None, "05": None}
            for idx, tt in enumerate(text_types):
                if tt in preferred and preferred[tt] is None and idx < len(text_values):
                    preferred[tt] = text_values[idx]
            for tt in ("03", "02", "05"):
                if preferred.get(tt):
                    summary = preferred[tt]
                    break
            if not summary:
                summary = text_values[0]

        # PageCount: ExtentValue where matching ExtentUnit == 03 (pages).
        page_count = ""
        extent_units = raw.get("DescriptiveDetail.Extent.ExtentUnit", [])
        extent_values = raw.get("DescriptiveDetail.Extent.ExtentValue", [])
        for idx, unit in enumerate(extent_units):
            if unit == "03" and idx < len(extent_values):
                page_count = extent_values[idx]
                break
        if not page_count and extent_values:
            page_count = extent_values[0]

        language_code = first("DescriptiveDetail.Language.LanguageCode")
        language = {"dut": "nl", "eng": "en", "ger": "de", "fre": "fr"}.get(
            language_code, language_code)

        publisher = (
            first("PublishingDetail.Imprint.ImprintName")
            or first("PublishingDetail.Publisher.PublisherName")
        )
        published_date = first("PublishingDetail.PublishingDate.Date")

        # Categories: collect subject headings (BISAC, Thema, NUR codes may also exist; prefer text)
        subjects = raw.get("DescriptiveDetail.Subject.SubjectHeadingText", [])
        categories = ", ".join(s for s in subjects if s)

        # Cover: prefer _VRK (voorkant), fall back to _ATK (achterkant/cover).
        cover_filename = ""
        resource_keys = [k for k in raw if k.endswith("ResourceVersion.ResourceLink")]
        candidates: list[str] = []
        for k in resource_keys:
            candidates.extend(raw[k])
        vrk = next((c for c in candidates if c.endswith("_VRK.jpg")), "")
        atk = next((c for c in candidates if c.endswith("_ATK.jpg")), "")
        cover_filename = vrk or atk

        book: dict[str, str] = {
            "Title": title,
            "Author": first("author"),
            "Summary": summary,
            "Publisher": publisher,
            "PublishedDate": published_date,
            "PageCount": page_count,
            "Categories": categories,
            "AverageRating": "",
            "RatingsCount": "",
            "Language": language,
            "CoverFilename": cover_filename,
        }
        return book, 200

    def fetch_easycb_cover(self, cover_filename: str) -> tuple[bytes | None, int | None]:
        """Download a cover JPG from EasyCB. Returns (bytes, status_code)."""
        url = f"{self.EASYCB_API}/resources/jpg/{cover_filename}"
        headers = {
            "contact": self.easycb_contact(),
            "User-Agent": self.USER_AGENT,
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            print(f"EasyCB cover request failed: {e}")
            return None, None
        if not response.ok:
            return None, response.status_code
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type.lower():
            return None, response.status_code
        # Cap at 5 MB
        if len(response.content) > 5 * 1024 * 1024:
            return None, response.status_code
        return response.content, 200

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