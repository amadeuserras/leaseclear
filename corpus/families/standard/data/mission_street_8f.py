from doc_meta import DocMeta
from families.standard.model import (
    Deposit,
    DueAtSigningRow,
    Landlord,
    LateFee,
    NsfFee,
    Parking,
    Pet,
    Pets,
    Property,
    Rent,
    Smoking,
    StandardLease,
    Tenant,
    Term,
    Utilities,
)

LEASE = StandardLease(
    doc=DocMeta(
        name="mission_street_8f",
        title="Standard Residential Lease Agreement",
        tags=["standard"],
    ),
    agreement_date="June 18, 2026",
    landlord=Landlord(
        name="Mission Street Holdings LLC",
        address="1800 Mission Street, San Francisco, CA 94103",
        phone="(415) 555-0198",
    ),
    tenants=[Tenant(name="Jordan Lee")],
    occupants=["Taylor Lee"],
    property=Property(
        address="1800 Mission Street, Unit 8F, San Francisco, CA 94103",
        type="apartment",
        bedrooms=2,
        bathrooms=2,
    ),
    term=Term(
        type="fixed",
        start="April 1, 2026",
        end="March 31, 2027",
        notice_days=30,
    ),
    rent=Rent(
        amount=3200.00,
        due_day=1,
        methods=["ACH transfer", "check"],
    ),
    deposit=Deposit(required=True, amount=3200.00, return_days=21),
    late_fee=LateFee(enabled=True, amount=100.00, grace_days=5, per="occurrence"),
    nsf_fee=NsfFee(enabled=True, amount=35.00),
    pets=Pets(
        allowed=True,
        list=[Pet(type="domestic cat", max_weight=15)],
        fee=500.00,
        refundable=False,
    ),
    smoking=Smoking(allowed=False),
    utilities=Utilities(landlord_pays=["water", "garbage"]),
    parking=Parking(provided=True, spaces=1, fee=150.00),
    due_at_signing=[
        DueAtSigningRow(label="First month's rent", amount=3200.00),
        DueAtSigningRow(label="Security deposit", amount=3200.00),
        DueAtSigningRow(label="Pet fee", amount=500.00),
    ],
)
