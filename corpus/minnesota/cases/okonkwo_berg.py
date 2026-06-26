from minnesota.model import Lease, Notices, Owner, Pets, Tenant, Term, Utilities

LEASE = Lease(
    filename="minnesota-okonkwo_berg",
    date="July 1, 2025",
    total_pages=6,
    owner=Owner(
        name="Riverside Property Management Inc.",
        address="2200 University Avenue W, Saint Paul, MN 55114",
        phone="(651) 555-0087",
    ),
    tenants=[
        Tenant(name="Chukwuemeka Okonkwo"),
        Tenant(name="Sara Berg"),
    ],
    property_address="1845 Selby Avenue",
    property_city="Saint Paul",
    property_county="Ramsey",
    has_garage=False,
    has_storage_unit=True,
    has_parking_stall=True,
    garage_stall_number="S-12",
    term=Term(
        is_month_to_month=True,
        start="August 1, 2025",
    ),
    rent_amount=1575.00,
    utilities=Utilities(
        paid_by_tenant=True,
        paid_by_owner=False,
        split=False,
    ),
    deposit_amount=1575.00,
    late_fee_amount=80.00,
    pets=Pets(allowed=False),
    occupants="Chukwuemeka Okonkwo and Sara Berg",
    is_cic=False,
    notices=Notices(
        owner_address="2200 University Avenue W, Saint Paul, MN 55114",
        owner_phone="(651) 555-0087",
        tenant_address="1845 Selby Avenue, Saint Paul, MN 55104",
        tenant_phone="(612) 555-0341",
    ),
    lead_paint=True,
    tenant_initials="CO/SB",
    sign_date="July 1, 2025",
)
