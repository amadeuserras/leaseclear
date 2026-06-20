from pathlib import Path

import leaseclear.ingestion.chunk as chunk_mod
import pytest
from leaseclear.ingestion.chunk import Chunk, chunk_document
from leaseclear.ingestion.parse import PageText, ParsedDocument, parse_pdf
from leaseclear.utils.pretty_print import pretty_print


def test_chunk_document_splits_top_level_clauses() -> None:
    document = ParsedDocument(
        source=Path("lease.pdf"),
        pages=[
            PageText(
                page_number=1,
                text=(
                    "RESIDENTIAL LEASE AGREEMENT\n"
                    "1. PARTIES. Landlord and Tenant agree.\n"
                    "2. RENT. Tenant pays monthly.\n"
                ),
            )
        ],
    )

    expected = [
        Chunk(
            text="RESIDENTIAL LEASE AGREEMENT",
            clause_label="",
            page_number=1,
        ),
        Chunk(
            text="1. PARTIES. Landlord and Tenant agree.",
            clause_label="1. PARTIES",
            page_number=1,
        ),
        Chunk(
            text="2. RENT. Tenant pays monthly.",
            clause_label="2. RENT",
            page_number=1,
        ),
    ]

    assert chunk_document(document) == expected


def test_chunk_document_splits_sub_clauses() -> None:
    document = ParsedDocument(
        source=Path("lease.pdf"),
        pages=[
            PageText(
                page_number=1,
                text=("1. PARTIES.\n1.1 Landlord: Acme LLC.\n1.2 Tenant: Jane Doe.\n"),
            )
        ],
    )

    expected = [
        Chunk(
            text="1. PARTIES.",
            clause_label="1. PARTIES",
            page_number=1,
        ),
        Chunk(
            text="1.1 Landlord: Acme LLC.",
            clause_label="1.1",
            page_number=1,
        ),
        Chunk(
            text="1.2 Tenant: Jane Doe.",
            clause_label="1.2",
            page_number=1,
        ),
    ]

    assert chunk_document(document) == expected


def test_chunk_document_tracks_page_number_across_pages() -> None:
    document = ParsedDocument(
        source=Path("lease.pdf"),
        pages=[
            PageText(
                page_number=1,
                text="7. SECURITY DEPOSIT.\n7.1 Amount: $500.\n",
            ),
            PageText(
                page_number=2,
                text="7.2 Return: within 30 days.\n",
            ),
        ],
    )

    expected = [
        Chunk(
            text="7. SECURITY DEPOSIT.",
            clause_label="7. SECURITY DEPOSIT",
            page_number=1,
        ),
        Chunk(
            text="7.1 Amount: $500.",
            clause_label="7.1",
            page_number=1,
        ),
        Chunk(
            text="7.2 Return: within 30 days.",
            clause_label="7.2",
            page_number=2,
        ),
    ]

    assert chunk_document(document) == expected


def test_chunk_document_splits_long_clause_and_prepends_label(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(chunk_mod, "MAX_CHUNK_CHARS", 40)
    document = ParsedDocument(
        source=Path("lease.pdf"),
        pages=[
            PageText(
                page_number=1,
                text="3. TERM. " + "The lease runs for one year. " * 5,
            )
        ],
    )

    expected = [
        Chunk(
            text="3. TERM. The lease runs for one year",
            clause_label="3. TERM",
            page_number=1,
        ),
        Chunk(
            text="3. TERM\n\nThe lease runs for one year",
            clause_label="3. TERM",
            page_number=1,
        ),
        Chunk(
            text="3. TERM\n\nThe lease runs for one year",
            clause_label="3. TERM",
            page_number=1,
        ),
        Chunk(
            text="3. TERM\n\nThe lease runs for one year",
            clause_label="3. TERM",
            page_number=1,
        ),
        Chunk(
            text="3. TERM\n\nThe lease runs for one year.",
            clause_label="3. TERM",
            page_number=1,
        ),
    ]

    assert chunk_document(document) == expected


def test_chunk_document_corpus_simple_walnut_street_2() -> None:
    pdf_file = (
        Path(__file__).resolve().parents[2]
        / "corpus"
        / "generated"
        / "simple-walnut_street_2.pdf"
    )
    parsed = parse_pdf(pdf_file)

    expected = [
        Chunk(
            text="RESIDENTIAL LEASE AGREEMENT",
            clause_label="",
            page_number=1,
        ),
        Chunk(
            text='1. PARTIES. This Residential Lease Agreement ("Agreement") is made on June 18, 2026 between Walnut Street\nProperties LLC, with a mailing address of 410 Walnut Street, San Marcos, TX 78666 ("Landlord"), and Chris\nNguyen ("Tenant").',
            clause_label="1. PARTIES",
            page_number=1,
        ),
        Chunk(
            text='2. PROPERTY. The Landlord agrees to lease to the Tenant the property located at 410 Walnut Street, Unit 2,\nSan Marcos, TX 78666, a duplex with 1 bedroom(s) and 1 bathroom(s) (the "Premises").',
            clause_label="2. PROPERTY",
            page_number=1,
        ),
        Chunk(
            text="3. TERM. This Agreement begins on March 1, 2026 and ends on February 28, 2027.",
            clause_label="3. TERM",
            page_number=1,
        ),
        Chunk(
            text="4. RENT. The Tenant shall pay $950.00 per month, due on the 1 day of each month.",
            clause_label="4. RENT",
            page_number=1,
        ),
        Chunk(
            text="5. SECURITY DEPOSIT. The Tenant shall pay a security deposit of $950.00. The deposit, less any itemized\ndeductions, shall be returned within 30 days after the end of the Term.\nSIGNATURES\nLandlord: _________________________\xa0\xa0Date: __________\nWalnut Street Properties LLC\nTenant: ___________________________\xa0\xa0Date: __________\nChris Nguyen",
            clause_label="5. SECURITY DEPOSIT",
            page_number=1,
        ),
    ]

    assert chunk_document(parsed) == expected


def test_chunk_document_corpus_complex_evergreen_terrace_4b() -> None:
    pdf_file = (
        Path(__file__).resolve().parents[2]
        / "corpus"
        / "generated"
        / "complex-evergreen_terrace_4b.pdf"
    )
    parsed = parse_pdf(pdf_file)

    expected = [
        Chunk(
            text="Meridian Legal Forms\nMulti-State Residential Agreement\nRESIDENTIAL LEASE AGREEMENT\nThis Agreement is made on June 18, 2026 and governed by the laws of Texas.",
            clause_label="",
            page_number=1,
        ),
        Chunk(
            text="1. PARTIES.",
            clause_label="1. PARTIES",
            page_number=1,
        ),
        Chunk(
            text="1.1 Landlord: River Oaks Properties LLC, mailing address 500 Main Street, Austin, TX 78701.",
            clause_label="1.1",
            page_number=1,
        ),
        Chunk(
            text="1.2 Tenant(s): Jane Doe. Each individual named as a Tenant is jointly and severally liable for all obligations under\nthis Agreement.",
            clause_label="1.2",
            page_number=1,
        ),
        Chunk(
            text="2. PREMISES.",
            clause_label="2. PREMISES",
            page_number=1,
        ),
        Chunk(
            text="2.1 Address: 742 Evergreen Terrace, Unit 4B, Austin, TX 78704.",
            clause_label="2.1",
            page_number=1,
        ),
        Chunk(
            text="2.2 Legal description: Lot 12, Block 3, Riverside Addition, Travis County, Texas.",
            clause_label="2.2",
            page_number=1,
        ),
        Chunk(
            text='2.3 Residence type: apartment. The foregoing is the "Premises".',
            clause_label="2.3",
            page_number=1,
        ),
        Chunk(
            text="3. TERM.",
            clause_label="3. TERM",
            page_number=1,
        ),
        Chunk(
            text="3.1 Commencement: February 1, 2026. Expiration: January 31, 2027.",
            clause_label="3.1",
            page_number=1,
        ),
        Chunk(
            text="3.2 Renewal: Upon expiration and absent renewal, the Tenant may continue on a month-to-month basis terminable\non 30 days' written notice by either Party.",
            clause_label="3.2",
            page_number=1,
        ),
        Chunk(
            text="4. DEFINITIONS. The following terms have the meanings assigned below and are capitalized throughout this\nAgreement:",
            clause_label="4. DEFINITIONS",
            page_number=1,
        ),
        Chunk(
            text='4.1 "Rent" means the monthly sum payable under Section 5.',
            clause_label="4.1",
            page_number=1,
        ),
        Chunk(
            text='4.2 "Security Deposit" means the sum held under Section 7 as security for the Tenant\'s performance.',
            clause_label="4.2",
            page_number=1,
        ),
        Chunk(
            text='4.3 "Due Date" means the 1 day of each calendar month.',
            clause_label="4.3",
            page_number=1,
        ),
        Chunk(
            text='4.4 "Default" has the meaning assigned in Section 10.',
            clause_label="4.4",
            page_number=1,
        ),
        Chunk(
            text="5. RENT. The Tenant shall pay Rent of $1850.00 per month, payable in advance on each Due Date (as deﬁned in\nSection 4.3).",
            clause_label="5. RENT",
            page_number=1,
        ),
        Chunk(
            text="6. LATE CHARGE. If Rent is not received within 3 day(s) after the Due Date, the Tenant shall pay a late charge of\n$75.00. Assessment of late charges is subject to Texas Property Code § 92.019.",
            clause_label="6. LATE CHARGE",
            page_number=1,
        ),
        Chunk(
            text="7. SECURITY DEPOSIT.",
            clause_label="7. SECURITY DEPOSIT",
            page_number=1,
        ),
        Chunk(
            text="7.1 Amount: $1850.00, due on execution.",
            clause_label="7.1",
            page_number=1,
        ),
        Chunk(
            text="7.2 Return: The Security Deposit (as deﬁned in Section 4.2), less itemized deductions, shall be returned within 30\ndays after surrender, in accordance with Texas Property Code § 92.108.",
            clause_label="7.2",
            page_number=1,
        ),
        Chunk(
            text="7.3 The Security Deposit shall not be applied to Rent (Section 5) without the Landlord's written consent.",
            clause_label="7.3",
            page_number=2,
        ),
        Chunk(
            text="8. PETS. The Tenant may keep pets not exceeding 25 lbs, subject to a fee of $300.00. The Tenant is liable for all pet-\nrelated damage and shall restore the Premises at the Tenant's expense.",
            clause_label="8. PETS",
            page_number=2,
        ),
        Chunk(
            text="9. RIGHT OF ENTRY. The Landlord may enter the Premises upon at least 24 hours' written notice for inspection,\nrepairs, or showings, except that no notice is required in an emergency.",
            clause_label="9. RIGHT OF ENTRY",
            page_number=2,
        ),
        Chunk(
            text="10. DEFAULT. The Tenant is in Default if the Tenant (a) fails to pay Rent or other amounts when due; (b) violates any\nterm of this Agreement; or (c) abandons the Premises. Upon Default the Landlord may exercise all remedies available\nunder this Agreement and applicable law.",
            clause_label="10. DEFAULT",
            page_number=2,
        ),
        Chunk(
            text="11. SUBLETTING. The Tenant may sublet only with the Landlord's prior written consent.",
            clause_label="11. SUBLETTING",
            page_number=2,
        ),
        Chunk(
            text="12. MAINTENANCE. The Tenant shall maintain the Premises in clean and sanitary condition and surrender it as\nreceived, normal wear and tear excepted.",
            clause_label="12. MAINTENANCE",
            page_number=2,
        ),
        Chunk(
            text="13. SMOKE ALARMS & SECURITY DEVICES. The Premises is equipped with smoke alarms and exterior-door\nsecurity devices as required by applicable law. Requests for repair must be in writing.",
            clause_label="13. SMOKE ALARMS & SECURITY DEVICES",
            page_number=2,
        ),
        Chunk(
            text="14. SEVERABILITY. If any provision of this Agreement is held unenforceable, the remainder shall remain in full\nforce and eﬀect.",
            clause_label="14. SEVERABILITY",
            page_number=2,
        ),
        Chunk(
            text="15. ENTIRE AGREEMENT. This Agreement, together with any addenda, constitutes the entire agreement between\nthe Parties and supersedes all prior negotiations, understandings, and oral agreements.\nSIGNATURES\nLandlord: _________________________\xa0\xa0Date: __________\nRiver Oaks Properties LLC\nTenant: ___________________________\xa0\xa0Date: __________\nJane Doe",
            clause_label="15. ENTIRE AGREEMENT",
            page_number=2,
        ),
    ]

    assert chunk_document(parsed) == expected


@pytest.mark.only
def test_chunk_document_real_pdf() -> None:
    pdf_file = (
        Path(__file__).resolve().parents[2] / "corpus" / "generated" / "PDFS-Forms.pdf"
    )
    parsed = parse_pdf(pdf_file)
    chunks = chunk_document(parsed)
    pretty_print(chunks)
