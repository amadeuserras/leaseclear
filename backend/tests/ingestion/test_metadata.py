import pytest

from leaseclear.ingestion.assign import assign_document
from leaseclear.ingestion.metadata import extract_metadata
from leaseclear.ingestion.parse import parse_document
from leaseclear.types import UploadDocument
from tests.data.corpus import CORPUS_LEASE_PDF


@pytest.mark.real_api
async def test_extract_metadata_corpus_lease() -> None:
    upload = UploadDocument(
        path=str(CORPUS_LEASE_PDF),
        filename=CORPUS_LEASE_PDF.name,
    )
    parsed = parse_document(upload)
    assigned = assign_document(parsed, set())

    [enriched] = await extract_metadata([assigned])

    assert enriched.id == assigned.id
    assert enriched.slug == assigned.slug
    assert enriched.pages == assigned.pages
    assert enriched.landlord_name is not None
    assert "Cedar Grove" in enriched.landlord_name
    assert enriched.tenant_names
    assert any("Nadkarni" in name for name in enriched.tenant_names)
    assert any("Osei" in name for name in enriched.tenant_names)
    assert enriched.property_address is not None
    assert "Larkspur Lane" in enriched.property_address
