from unittest.mock import patch

import pytest

from ubiblio.routers.books import service


class TestLookupBookMetadataByIsbn:
    def test_easycb_wins_on_conflict_and_google_fills_gaps(self) -> None:
        easycb = {
            "Title": "EasyCB Titel",
            "Author": "Auteur",
            "Summary": "",
            "CoverFilename": "abc_VRK.jpg",
        }
        google = {
            "Title": "Other",
            "Author": "Other Author",
            "Summary": "Filled by Google",
            "Publisher": "Pub",
        }
        with patch("ubiblio.routers.books.service.BookMetadataClient") as Client:
            instance = Client.return_value
            instance.easycb_by_isbn.return_value = (easycb, 200)
            instance.google_books_by_isbn.return_value = (google, 200)
            book = service.lookup_book_metadata_by_isbn("123")
        assert book["Title"] == "EasyCB Titel"
        assert book["Author"] == "Auteur"
        assert book["Summary"] == "Filled by Google"
        assert book["Publisher"] == "Pub"
        assert book["CoverFilename"] == "abc_VRK.jpg"

    def test_falls_back_to_open_library_when_easycb_and_google_empty(self) -> None:
        with patch("ubiblio.routers.books.service.BookMetadataClient") as Client:
            instance = Client.return_value
            instance.easycb_by_isbn.return_value = ({}, 404)
            instance.google_books_by_isbn.return_value = ({}, 404)
            instance.open_library_by_isbn.return_value = (
                {"Title": "OL Title", "Author": "OL Auth", "Summary": ""}, 200)
            book = service.lookup_book_metadata_by_isbn("123")
        assert book["Title"] == "OL Title"
        assert book["Author"] == "OL Auth"

    def test_raises_lookuperror_when_all_sources_empty(self) -> None:
        with patch("ubiblio.routers.books.service.BookMetadataClient") as Client:
            instance = Client.return_value
            instance.easycb_by_isbn.return_value = ({}, 404)
            instance.google_books_by_isbn.return_value = ({}, 404)
            instance.open_library_by_isbn.return_value = ({}, 404)
            instance.open_wiki_by_isbn.return_value = ({}, 404)
            with pytest.raises(LookupError):
                service.lookup_book_metadata_by_isbn("123")
