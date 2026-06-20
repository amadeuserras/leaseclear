from doc_meta import DocMeta
from families.complex.data._common import make_lease
from families.complex.model import Edges

LEASE = make_lease(
    doc=DocMeta(
        name="oak_street_2a",
        title="Residential Lease Agreement",
        tags=["complex"],
        eval_targets=["refusal_when_clause_absent"],
    ),
    landlord_name="Oak Street Rentals",
    landlord_address="100 Oak Street, Dallas, TX 75201",
    tenant_names=["Alex Rivera"],
    property_address="118 Oak Street, Unit 2A, Dallas, TX 75201",
    legal_description="Unit 2A, Oak Street Condominiums, Dallas County, Texas",
    property_type="condominium",
    edges=Edges(
        omit_pet_section=True,
        conflicting_late_fee=False,
        cross_ref_sublet=False,
    ),
)
