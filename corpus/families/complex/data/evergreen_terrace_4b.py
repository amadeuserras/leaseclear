from doc_meta import DocMeta
from families.complex.data._common import make_lease
from families.complex.model import Edges

LEASE = make_lease(
    doc=DocMeta(
        name="evergreen_terrace_4b",
        title="Residential Lease Agreement",
        tags=["complex"],
    ),
    landlord_name="River Oaks Properties LLC",
    landlord_address="500 Main Street, Austin, TX 78701",
    tenant_names=["Jane Doe"],
    property_address="742 Evergreen Terrace, Unit 4B, Austin, TX 78704",
    legal_description="Lot 12, Block 3, Riverside Addition, Travis County, Texas",
    property_type="apartment",
    edges=Edges(
        omit_pet_section=False,
        conflicting_late_fee=False,
        cross_ref_sublet=False,
    ),
)
