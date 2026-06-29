from texas.model import Animals, Landlord, Lease, Property, Rent, Tenant, Term

LEASE = Lease(
    filename="texas-morales_reyes",
    agreement_day="5",
    agreement_month="August",
    agreement_year="2025",
    landlord=Landlord(
        name="Lone Star Property Management LLC",
        address="4800 N. Lamar Blvd, Suite 310, Austin, TX 78756",
        phone="(512) 555-0193",
    ),
    tenants=[
        Tenant(name="Carlos Morales"),
        Tenant(name="Isabel Reyes"),
    ],
    occupants="Carlos Morales, Isabel Reyes, and one minor child",
    property=Property(
        address="2214 Brentwood Street, Austin, TX 78757",
    ),
    term=Term(
        start="September 1, 2025",
        end="August 31, 2026",
    ),
    rent=Rent(
        amount=2100.00,
        late_charge_per_day=75.00,
        nsf_fee=50.00,
        holdover_amount=2625.00,
    ),
    deposit_amount=2100.00,
    animals=Animals(
        permitted=False,
        unauthorized_fee_per_day=100.00,
    ),
    lead_paint=False,
    sign_date="August 5, 2025",
)
