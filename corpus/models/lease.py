from dataclasses import dataclass, field


@dataclass
class Meta:
    id: str
    title: str
    tags: list[str]
    eval_targets: list[str] = field(default_factory=list)


@dataclass
class Party:
    name: str
    address: str | None = None


@dataclass
class Parties:
    landlord: Party
    tenants: list[Party]


@dataclass
class Property:
    address: str
    type: str


@dataclass
class Term:
    start: str
    end: str


@dataclass
class Rent:
    amount: str
    due_day: str
    payment_instructions: str


@dataclass
class Clause:
    id: str
    heading: str
    body: str


@dataclass
class Lease:
    meta: Meta
    parties: Parties
    property: Property
    term: Term
    rent: Rent | None = None
    clauses: list[Clause] = field(default_factory=list)
