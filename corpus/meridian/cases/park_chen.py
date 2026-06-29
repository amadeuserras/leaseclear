from meridian.model import (
    ConditionRow,
    Deposit,
    Disclosures,
    Entry,
    Insurance,
    Landlord,
    Landscaping,
    Lease,
    NsfFee,
    PetPolicy,
    Property,
    Rent,
    Subletting,
    Tenant,
    Term,
)

LEASE = Lease(
    filename="meridian-park_chen",
    agreement_date="March 3, 2025",
    landlord=Landlord(
        name="Ridgeline Property Group",
        address="14 Summit Drive, Unit 1, Ashford Heights, OR 97201",
        phone="(503) 555-0247",
    ),
    tenants=[
        Tenant(name="Soo-Jin Park"),
        Tenant(name="Kevin Chen"),
    ],
    occupants=["Soo-Jin Park", "Kevin Chen"],
    property=Property(
        address="302 Fern Valley Road, Apt 8B, Ashford Heights, OR 97201",
        type="apartment",
        bedrooms=1,
        bathrooms=1,
        included_personal_property=[
            "refrigerator",
            "electric range",
            "microwave",
        ],
        included_addendum_attached=False,
    ),
    term=Term(
        type="month_to_month",
        start="April 1, 2025",
        end="",
        notice_days=30,
    ),
    rent=Rent(
        amount=1650.00,
        due_day=1,
        methods=["transfer"],
        payee="Ridgeline Property Group",
    ),
    deposit=Deposit(required=True, amount=1650.00, return_days=21),
    nsf_fee=NsfFee(enabled=True, amount=25.00),
    landscaping=Landscaping(
        watering_by="landlord",
        maintenance_by="landlord",
        exceptions="",
    ),
    entry=Entry(keysafe_authorized=True),
    subletting=Subletting(short_term_prohibited=True),
    disclosures=Disclosures(
        lead_paint=False,
        pest_control=True,
        flood_hazard=False,
        mold=False,
    ),
    insurance=Insurance(required=False, amount=0.0),
    condition_rows=[
        ConditionRow("Living area", "Satisfactory", ""),
        ConditionRow(
            "Kitchen / appliances", "Satisfactory", "microwave door latch stiff"
        ),
        ConditionRow("Bathroom(s)", "Satisfactory", ""),
        ConditionRow("Flooring / walls", "Satisfactory", ""),
    ],
    pets=PetPolicy(
        allowed=False,
    ),
    sign_date="March 3, 2025",
)
