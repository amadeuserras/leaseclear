from dataclasses import dataclass
from typing import Literal

from doc_meta import DocMeta


@dataclass
class Landlord:
    name: str
    address: str
    phone: str


@dataclass
class Tenant:
    name: str


@dataclass
class Property:
    address: str
    type: str
    bedrooms: int
    bathrooms: int


@dataclass
class Term:
    type: Literal["fixed", "month_to_month"]
    start: str
    end: str
    notice_days: int


@dataclass
class Rent:
    amount: float
    due_day: int
    methods: list[str]


@dataclass
class Deposit:
    required: bool
    amount: float
    return_days: int


@dataclass
class LateFee:
    enabled: bool
    amount: float
    grace_days: int
    per: Literal["occurrence", "day"]


@dataclass
class NsfFee:
    enabled: bool
    amount: float


@dataclass
class Pet:
    type: str
    max_weight: int


@dataclass
class Pets:
    allowed: bool
    list: list[Pet]
    fee: float
    refundable: bool


@dataclass
class Smoking:
    allowed: bool


@dataclass
class Utilities:
    landlord_pays: list[str]


@dataclass
class Parking:
    provided: bool
    spaces: int
    fee: float


@dataclass
class DueAtSigningRow:
    label: str
    amount: float


@dataclass
class StandardLease:
    doc: DocMeta
    agreement_date: str
    landlord: Landlord
    tenants: list[Tenant]
    occupants: list[str]
    property: Property
    term: Term
    rent: Rent
    deposit: Deposit
    late_fee: LateFee
    nsf_fee: NsfFee
    pets: Pets
    smoking: Smoking
    utilities: Utilities
    parking: Parking
    due_at_signing: list[DueAtSigningRow]
