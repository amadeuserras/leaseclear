from doc_meta import DocMeta
from families.simple.model import (
    Deposit,
    Landlord,
    Property,
    Rent,
    SimpleLease,
    Tenant,
    Term,
)

LEASE = SimpleLease(
    doc=DocMeta(
        name="walnut_street_2",
        title="Residential Lease Agreement",
        tags=["simple"],
    ),
    agreement_date="June 18, 2026",
    landlord=Landlord(
        name="Walnut Street Properties LLC",
        address="410 Walnut Street, San Marcos, TX 78666",
    ),
    tenants=[Tenant(name="Chris Nguyen")],
    property=Property(
        address="410 Walnut Street, Unit 2, San Marcos, TX 78666",
        type="duplex",
        bedrooms=1,
        bathrooms=1,
    ),
    term=Term(start="March 1, 2026", end="February 28, 2027"),
    rent=Rent(amount=950.00, due_day=1),
    deposit=Deposit(required=True, amount=950.00, return_days=30),
)
