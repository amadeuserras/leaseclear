from models.lease import Clause, Lease, Meta, Parties, Party, Property, Rent, Term

CONFLICTING_PETS = Lease(
    meta=Meta(
        id="syn-conflicting-pets",
        title="Residential Lease Agreement",
        tags=["conflicting_clauses", "pets"],
        eval_targets=["cite_both_sections", "do_not_resolve_conflict"],
    ),
    parties=Parties(
        landlord=Party(
            name="River Oaks Properties LLC",
            address="500 Main Street, Austin, TX 78701",
        ),
        tenants=[Party(name="Jane Doe")],
    ),
    property=Property(
        address="742 Evergreen Terrace, Unit 4B, Austin, TX 78704",
        type="apartment",
    ),
    term=Term(start="February 1, 2026", end="January 31, 2027"),
    rent=Rent(
        amount="$1,850",
        due_day="1st",
        payment_instructions="ACH transfer via the landlord portal",
    ),
    clauses=[
        Clause(
            id="12",
            heading="PETS",
            body=(
                "Tenant may keep up to two (2) domestic cats with prior written "
                "approval from Landlord."
            ),
        ),
        Clause(
            id="22",
            heading="ANIMALS",
            body=(
                "No pets, animals, or aquariums of any kind are permitted on the "
                "Premises at any time."
            ),
        ),
    ],
)
