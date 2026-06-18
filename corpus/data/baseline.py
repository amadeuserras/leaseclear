from models.lease import Clause, Lease, Meta, Parties, Party, Property, Rent, Term

BASELINE = Lease(
    meta=Meta(
        id="syn-baseline",
        title="Residential Lease Agreement",
        tags=["baseline"],
    ),
    parties=Parties(
        landlord=Party(
            name="Rivers Oaks Properties LLC",
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
        payment_instructions=(
            "ACH transfer via the landlord portal (account ending 4521)"
        ),
    ),
    clauses=[
        Clause(
            id="5",
            heading="SECURITY DEPOSIT",
            body=(
                "Tenant shall deposit $1,850 as security. Landlord shall return "
                "the deposit, less itemized deductions, within 30 days after "
                "lease termination."
            ),
        ),
        Clause(
            id="6",
            heading="MAINTENANCE",
            body=(
                "Tenant shall promptly notify Landlord of needed repairs. "
                "Landlord shall respond within 48 hours for urgent issues."
            ),
        ),
    ],
)
