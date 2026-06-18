from models.lease import Clause, Lease, Meta, Parties, Party, Property, Term

MISSING_RENT = Lease(
    meta=Meta(
        id="syn-missing-rent",
        title="Residential Lease Agreement",
        tags=["missing_info"],
        eval_targets=["refusal_when_clause_absent"],
    ),
    parties=Parties(
        landlord=Party(
            name="Oak Street Rentals",
            address="100 Oak Street, Dallas, TX 75201",
        ),
        tenants=[Party(name="Alex Rivera")],
    ),
    property=Property(
        address="100 Oak Street, Unit 2A, Dallas, TX 75201",
        type="condominium",
    ),
    term=Term(start="March 1, 2026", end="February 28, 2027"),
    clauses=[
        Clause(
            id="5",
            heading="UTILITIES",
            body=(
                "Tenant is responsible for electricity and internet. Landlord "
                "provides water and trash."
            ),
        ),
    ],
)
