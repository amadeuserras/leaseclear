from dataclasses import dataclass
from typing import Literal

from doc_meta import DocMeta


@dataclass
class AgreementMeta:
    agreement_date: str
    jurisdiction: str
    deposit_statute: str
    late_fee_statute: str


@dataclass
class Landlord:
    name: str
    address: str


@dataclass
class Tenant:
    name: str


@dataclass
class Property:
    address: str
    legal_description: str
    type: str


@dataclass
class Term:
    start: str
    end: str
    renewal: Literal["month_to_month", "vacate"]
    notice_days: int


@dataclass
class Rent:
    amount: float
    due_day: int


@dataclass
class Deposit:
    amount: float
    return_days: int


@dataclass
class LateFee:
    amount: float
    grace_days: int


@dataclass
class Pets:
    allowed: bool
    max_weight: int
    fee: float


@dataclass
class Sublet:
    allowed: bool


@dataclass
class Edges:
    omit_pet_section: bool
    conflicting_late_fee: bool
    cross_ref_sublet: bool


@dataclass
class ComplexLease:
    doc: DocMeta
    agreement: AgreementMeta
    landlord: Landlord
    tenants: list[Tenant]
    property: Property
    term: Term
    rent: Rent
    deposit: Deposit
    late_fee: LateFee
    late_fee_conflict_amount: float
    pets: Pets
    sublet: Sublet
    edges: Edges
