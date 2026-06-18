from data.baseline import BASELINE
from data.conflicting_pet_policy import CONFLICTING_PETS
from data.missing_rent import MISSING_RENT
from models.lease import Lease

ALL: list[Lease] = [BASELINE, CONFLICTING_PETS, MISSING_RENT]

BY_ID: dict[str, Lease] = {lease.meta.id: lease for lease in ALL}
