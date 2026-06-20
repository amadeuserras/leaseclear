from doc_meta import DocMeta
from families.complex.model import (
    AgreementMeta,
    ComplexLease,
    Deposit,
    Edges,
    Landlord,
    LateFee,
    Pets,
    Property,
    Rent,
    Sublet,
    Tenant,
    Term,
)


def make_lease(
    *,
    doc: DocMeta,
    landlord_name: str,
    landlord_address: str,
    tenant_names: list[str],
    property_address: str,
    legal_description: str,
    property_type: str,
    edges: Edges,
) -> ComplexLease:
    return ComplexLease(
        doc=doc,
        agreement=AgreementMeta(
            agreement_date="June 18, 2026",
            jurisdiction="Texas",
            deposit_statute="Texas Property Code § 92.108",
            late_fee_statute="Texas Property Code § 92.019",
        ),
        landlord=Landlord(name=landlord_name, address=landlord_address),
        tenants=[Tenant(name=name) for name in tenant_names],
        property=Property(
            address=property_address,
            legal_description=legal_description,
            type=property_type,
        ),
        term=Term(
            start="February 1, 2026",
            end="January 31, 2027",
            renewal="month_to_month",
            notice_days=30,
        ),
        rent=Rent(amount=1850.00, due_day=1),
        deposit=Deposit(amount=1850.00, return_days=30),
        late_fee=LateFee(amount=75.00, grace_days=3),
        late_fee_conflict_amount=150.00,
        pets=Pets(allowed=True, max_weight=25, fee=300.00),
        sublet=Sublet(allowed=True),
        edges=edges,
    )
