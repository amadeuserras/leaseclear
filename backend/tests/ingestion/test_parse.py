from leaseclear.ingestion.parse import parse_document
from leaseclear.types import UploadDocument
from tests.data.corpus import CORPUS_LEASE_PDF


def test_parse_pdf_corpus_lease() -> None:
    upload = UploadDocument(
        path=str(CORPUS_LEASE_PDF),
        filename=CORPUS_LEASE_PDF.name,
    )
    parsed = parse_document(upload)

    assert parsed.filename == CORPUS_LEASE_PDF.name
    assert len(parsed.pages) == 3
    assert [page.page_number for page in parsed.pages] == [1, 2, 3]
    assert all(page.text.strip() for page in parsed.pages)

    assert "RESIDENTIAL LEASE AGREEMENT" in parsed.pages[0].text
    assert "3. Rent" in parsed.pages[0].text
    assert "SCHEDULE A" in parsed.pages[2].text
