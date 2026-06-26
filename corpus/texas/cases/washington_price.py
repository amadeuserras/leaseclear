from texas.model import Animals, Landlord, Lease, Property, Rent, Tenant, Term

LEASE = Lease(
    filename="texas-washington_price",
    agreement_day="14",
    agreement_month="February",
    agreement_year="2025",
    landlord=Landlord(
        name="Magnolia Heights Properties",
        address="1001 Texas Ave, Suite 200, Houston, TX 77002",
        phone="(713) 555-0311",
    ),
    tenants=[
        Tenant(name="Darnell Washington"),
        Tenant(name="Keisha Price"),
    ],
    occupants="Darnell Washington and Keisha Price",
    property=Property(
        address="5522 Westheimer Road, Apt 14C, Houston, TX 77056",
    ),
    term=Term(
        start="March 1, 2025",
        end="February 28, 2026",
    ),
    rent=Rent(
        amount=1875.00,
        late_charge_per_day=50.00,
        nsf_fee=35.00,
        holdover_amount=2350.00,
    ),
    deposit_amount=3750.00,
    animals=Animals(
        permitted=False,
        unauthorized_fee_per_day=75.00,
    ),
    lead_paint=True,
    sign_date="February 14, 2025",
)
