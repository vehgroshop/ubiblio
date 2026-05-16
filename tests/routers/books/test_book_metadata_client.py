from urllib.parse import urlencode

from pytest import MonkeyPatch
import responses
import pytest

from ubiblio.routers.books.book_metadata_client import BookMetadataClient


class TestBookMetadataClientGoogleBooksByIsbn:
    @responses.activate
    def test_google_books_by_isbn_should_return_book_metadata(self, monkeypatch: MonkeyPatch) -> None:
        # Arrange
        isbn = "9780123456789"
        api_key = "test-api-key"
        monkeypatch.setattr(
            "ubiblio.routers.books.book_metadata_client.GOOGLE_BOOKS_API_KEY", api_key
        )
        query = urlencode({"q": f"+isbn:{isbn}", "key": api_key})
        url = f"{BookMetadataClient.GOOGLE_BOOKS_API}?{query}"
        responses.add(
            responses.GET,
            url,
            json={
                "items": [
                    {
                        "volumeInfo": {
                            "title": "Test Title",
                            "authors": ["A. Reader"],
                            "description": "A fine book.",
                        }
                    }
                ]
            },
            status=200,
        )

        client = BookMetadataClient()

        # Act
        book, status = client.google_books_by_isbn(isbn)

        # Assert
        assert status == 200
        assert book == {
            "Title": "Test Title",
            "Author": "A. Reader",
            "Summary": "A fine book.",
            "Publisher": "",
            "PublishedDate": "",
            "PageCount": "",
            "Categories": "",
            "AverageRating": "",
            "RatingsCount": "",
            "Language": "",
        }
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == url

    @responses.activate
    def test_google_books_by_isbn_should_return_error_when_api_key_is_missing(self, monkeypatch: MonkeyPatch) -> None:
        # Arrange
        isbn = "9780123456789"
        monkeypatch.setattr(
            "ubiblio.routers.books.book_metadata_client.GOOGLE_BOOKS_API_KEY", None
        )
        client = BookMetadataClient()

        # Act
        book, status = client.google_books_by_isbn(isbn)

        # Assert
        assert status is None
        assert book == {}

    @responses.activate
    def test_google_books_by_isbn_should_return_error_when_response_is_not_ok(self, monkeypatch: MonkeyPatch) -> None:
        # Arrange
        isbn = "9780123456789"
        api_key = "test-api-key"
        monkeypatch.setattr(
            "ubiblio.routers.books.book_metadata_client.GOOGLE_BOOKS_API_KEY", api_key
        )
        query = urlencode({"q": f"+isbn:{isbn}", "key": api_key})
        url = f"{BookMetadataClient.GOOGLE_BOOKS_API}?{query}"
        responses.add(
            responses.GET,
            url,
            json={"error": "notfound", "key": "/isbn/invalid"},
            status=404,
        )

        client = BookMetadataClient()

        # Act
        book, status = client.google_books_by_isbn(isbn)

        # Assert
        assert status == 404
        assert book == {}


class TestBookMetadataClientOpenLibraryByIsbn:
    @responses.activate
    def test_open_library_by_isbn_should_return_book_metadata(self, monkeypatch: MonkeyPatch) -> None:
        # Arrange
        isbn = "9780123456789"

        responses.add(
            responses.GET,
            f"{BookMetadataClient.OPEN_LIBRARY_API}/api/books?bibkeys=9780123456789&format=json&jscmd=details",
            json={
                f"{isbn}": {
                    "details": {
                        "title": "Test Title",
                        "authors": [
                            {
                                "key": "/authors/OL1607920A",
                                "name": "A. Reader"
                            }
                        ],
                        "description": {
                            "value": "A fine book.",
                        }
                    }
                }
            },
            status=200,
        )

        client = BookMetadataClient()

        # Act
        book, status = client.open_library_by_isbn(isbn)
        # Assert
        assert status == 200
        assert book == {
            "Title": "Test Title",
            "Author": "A. Reader",
            "Summary": "A fine book.",
        }
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == f"{BookMetadataClient.OPEN_LIBRARY_API}/api/books?bibkeys={isbn}&format=json&jscmd=details"

    @responses.activate
    @pytest.mark.parametrize("arthur_value", [[], [{}], [{"key": "/authors/OL1607920A"}]])
    def test_open_library_by_isbn_should_return_book_metadata_even_if_no_author_is_found(self, arthur_value: list[dict[str, str]]) -> None:
        # Arrange
        isbn = "9780123456789"

        responses.add(
            responses.GET,
            f"{BookMetadataClient.OPEN_LIBRARY_API}/api/books?bibkeys={isbn}&format=json&jscmd=details",
            json={
                f"{isbn}": {
                    "details": {
                        "title": "Test Title",
                        "authors": arthur_value,
                        "description": {
                            "value": "A fine book.",
                        }
                    }
                }
            },
            status=200,
        )

        client = BookMetadataClient()

        # Act
        book, status = client.open_library_by_isbn(isbn)

        # Assert
        assert status == 200
        assert book == {
            "Title": "Test Title",
            "Summary": "A fine book.",
            "Author": "",
        }
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == f"{BookMetadataClient.OPEN_LIBRARY_API}/api/books?bibkeys={isbn}&format=json&jscmd=details"

    @responses.activate
    def test_open_library_by_isbn_should_return_book_metadata_even_if_no_description_is_found(self, monkeypatch: MonkeyPatch) -> None:
        # Arrange
        isbn = "9780123456789"

        responses.add(
            responses.GET,
            f"{BookMetadataClient.OPEN_LIBRARY_API}/api/books?bibkeys={isbn}&format=json&jscmd=details",
            json={
                f"{isbn}": {
                    "details": {
                        "title": "Test Title",
                    }
                }
            },
            status=200,
        )

        client = BookMetadataClient()

        # Act
        book, status = client.open_library_by_isbn(isbn)

        # Assert
        assert status == 200
        assert book == {
            "Title": "Test Title",
            "Summary": "",
            "Author": "",
        }
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == f"{BookMetadataClient.OPEN_LIBRARY_API}/api/books?bibkeys={isbn}&format=json&jscmd=details"

    @responses.activate
    def test_open_library_by_isbn_should_return_error_when_response_is_not_ok(self) -> None:
        # Arrange
        isbn = "9780123456789"
        responses.add(
            responses.GET,
            f"{BookMetadataClient.OPEN_LIBRARY_API}/api/books?bibkeys={isbn}&format=json&jscmd=details",
            json={},
            status=404,
        )
        client = BookMetadataClient()

        # Act
        book, status = client.open_library_by_isbn(isbn)

        # Assert
        assert status == 404
        assert book == {}


class TestBookMetadataClientEasyCbByIsbn:
    SAMPLE_BODY = (
        "isbn:9789083316642\n"
        "title:Het generatiepact\n"
        "author:B. Huygebaert\n"
        "mutationlog:\n"
        "DescriptiveDetail.Extent.ExtentUnit:03\n"
        "DescriptiveDetail.Extent.ExtentValue:168\n"
        "DescriptiveDetail.Language.LanguageCode:dut\n"
        "DescriptiveDetail.Subject.SubjectHeadingText:Roman\n"
        "DescriptiveDetail.Subject.SubjectHeadingText:Familie\n"
        "PublishingDetail.Imprint.ImprintName:TestImprint\n"
        "PublishingDetail.PublishingDate.Date:20240101\n"
        "CollateralDetail.TextContent.TextType:03\n"
        "CollateralDetail.TextContent.Text:Korte beschrijving.\n"
        "CollateralDetail.SupportingResource.1.ResourceVersion.ResourceLink:9789083316642_ATK.jpg\n"
        "CollateralDetail.SupportingResource.0.ResourceVersion.ResourceLink:9789083316642_VRK.jpg\n"
    )

    @responses.activate
    def test_easycb_by_isbn_should_return_book_metadata(self) -> None:
        isbn = "9789083316642"
        responses.add(
            responses.GET,
            f"{BookMetadataClient.EASYCB_API}/isbn/{isbn}",
            body=self.SAMPLE_BODY,
            status=200,
            content_type="text/plain",
        )

        book, status = BookMetadataClient().easycb_by_isbn(isbn)

        assert status == 200
        assert book["Title"] == "Het generatiepact"
        assert book["Author"] == "B. Huygebaert"
        assert book["Summary"] == "Korte beschrijving."
        assert book["Publisher"] == "TestImprint"
        assert book["PublishedDate"] == "20240101"
        assert book["PageCount"] == "168"
        assert book["Language"] == "nl"
        assert book["Categories"] == "Roman, Familie"
        # Cover preference: VRK over ATK
        assert book["CoverFilename"] == "9789083316642_VRK.jpg"

    @responses.activate
    def test_easycb_by_isbn_falls_back_to_atk_when_no_vrk(self) -> None:
        isbn = "9789083316642"
        body = (
            "title:X\nauthor:Y\n"
            "CollateralDetail.SupportingResource.1.ResourceVersion.ResourceLink:foo_ATK.jpg\n"
        )
        responses.add(
            responses.GET,
            f"{BookMetadataClient.EASYCB_API}/isbn/{isbn}",
            body=body,
            status=200,
        )

        book, status = BookMetadataClient().easycb_by_isbn(isbn)

        assert status == 200
        assert book["CoverFilename"] == "foo_ATK.jpg"

    @responses.activate
    def test_easycb_by_isbn_returns_empty_when_title_missing(self) -> None:
        isbn = "9789083316642"
        responses.add(
            responses.GET,
            f"{BookMetadataClient.EASYCB_API}/isbn/{isbn}",
            body="isbn:9789083316642\nauthor:Anon\n",
            status=200,
        )

        book, status = BookMetadataClient().easycb_by_isbn(isbn)

        assert status == 200
        assert book == {}

    @responses.activate
    def test_easycb_by_isbn_returns_empty_on_404(self) -> None:
        isbn = "0000000000000"
        responses.add(
            responses.GET,
            f"{BookMetadataClient.EASYCB_API}/isbn/{isbn}",
            body="not found",
            status=404,
        )

        book, status = BookMetadataClient().easycb_by_isbn(isbn)

        assert status == 404
        assert book == {}

    @responses.activate
    def test_easycb_by_isbn_sends_contact_header(self, monkeypatch: MonkeyPatch) -> None:
        isbn = "9789083316642"
        monkeypatch.setenv("EASYCB_CONTACT", "tester@example.org")
        responses.add(
            responses.GET,
            f"{BookMetadataClient.EASYCB_API}/isbn/{isbn}",
            body="title:T\nauthor:A\n",
            status=200,
        )

        BookMetadataClient().easycb_by_isbn(isbn)

        assert responses.calls[0].request.headers.get("contact") == "tester@example.org"


class TestBookMetadataClientOpenWikiByIsbn:
    @responses.activate
    def test_open_wiki_by_isbn_should_return_book_metadata(self) -> None:
        # Arrange
        isbn = "9780123456789"
        responses.add(
            responses.GET,
            f"{BookMetadataClient.OPEN_WIKI_API}isbn/{isbn}.json",
            json=[
                {
                    "key": "F5GJ7RVZ",
                    "title": "Effective Book",
                    "author": [
                        [
                            "First",
                            "Last"
                        ]
                    ]
                }
            ]

        )
        client = BookMetadataClient()

        # Act
        book, status = client.open_wiki_by_isbn(isbn)

        # Assert
        assert status == 200
        assert book == {
            "Title": "Effective Book",
            "Author": "First Last",
            "Summary": "",
        }
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == f"{BookMetadataClient.OPEN_WIKI_API}isbn/{isbn}.json"

    @responses.activate
    def test_open_wiki_by_isbn_should_return_error_when_response_is_not_ok(self) -> None:
        # Arrange
        isbn = "9780123456789"
        responses.add(
            responses.GET,
            f"{BookMetadataClient.OPEN_WIKI_API}isbn/{isbn}.json",
            json={},
            status=404,
        )
        client = BookMetadataClient()

        # Act
        book, status = client.open_wiki_by_isbn(isbn)
        # Assert
        assert status == 404
        assert book == {}
