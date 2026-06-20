from doc_meta import DocMeta
from families.complex.data._common import make_lease
from families.complex.model import Edges

LEASE = make_lease(
    doc=DocMeta(
        name="lakeview_drive_12c",
        title="Residential Lease Agreement",
        tags=["complex"],
        eval_targets=["cite_both_sections", "do_not_resolve_conflict"],
    ),
    landlord_name="Lakeview Residential Partners LP",
    landlord_address="2200 Lakeview Drive, Suite 100, Austin, TX 78703",
    tenant_names=["Maria Chen", "David Chen"],
    property_address="2200 Lakeview Drive, Unit 12C, Austin, TX 78703",
    legal_description="Unit 12C, Lakeview Towers, Travis County, Texas",
    property_type="apartment",
    edges=Edges(
        omit_pet_section=False,
        conflicting_late_fee=True,
        cross_ref_sublet=True,
    ),
)
