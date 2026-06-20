from dataclasses import dataclass

from doc_meta import DocMeta


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
    type: str
    bedrooms: int
    bathrooms: int


@dataclass
class Term:
    start: str
    end: str


@dataclass
class Rent:
    amount: float
    due_day: int


@dataclass
class Deposit:
    required: bool
    amount: float
    return_days: int


@dataclass
class SimpleLease:
    doc: DocMeta
    agreement_date: str
    landlord: Landlord
    tenants: list[Tenant]
    property: Property
    term: Term
    rent: Rent
    deposit: Deposit
