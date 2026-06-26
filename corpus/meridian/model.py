from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


def _money(x: float | None) -> str | None:
    return f"${x:,.2f}" if x is not None else None


def _ordinal(n: int | None) -> str | None:
    if n is None:
        return None
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _join_names(names: list[str]) -> str:
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def _initials(name: str) -> str:
    parts = [p for p in name.replace(".", " ").split() if p]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


@dataclass
class Landlord:
    name: str
    address: str = ""
    phone: str = ""
    initials: str = ""


@dataclass
class Tenant:
    name: str
    initials: str = ""


@dataclass
class Property:
    address: str
    type: str = ""
    bedrooms: int = 0
    bathrooms: int = 0
    included_personal_property: list[str] = field(default_factory=list)
    included_addendum_attached: bool = False


@dataclass
class Term:
    type: Literal["fixed", "month_to_month"]
    start: str
    end: str = ""
    notice_days: int = 30


@dataclass
class Rent:
    amount: float
    due_day: int = 1
    methods: list[str] = field(default_factory=lambda: ["transfer"])
    payee: str = ""
    other_method_desc: str = ""


@dataclass
class Deposit:
    required: bool = True
    amount: float = 0.0
    return_days: int = 21


@dataclass
class NsfFee:
    enabled: bool = True
    amount: float = 0.0


@dataclass
class Landscaping:
    watering_by: Literal["landlord", "tenant"] = "tenant"
    maintenance_by: Literal["landlord", "tenant"] = "landlord"
    exceptions: str = ""


@dataclass
class Entry:
    keysafe_authorized: bool = False


@dataclass
class Subletting:
    short_term_prohibited: bool = True


@dataclass
class Disclosures:
    lead_paint: bool = False
    pest_control: bool = False
    flood_hazard: bool = False
    mold: bool = False


@dataclass
class Insurance:
    required: bool = False
    amount: float = 0.0


@dataclass
class ConditionRow:
    area: str
    condition: str = ""
    comments: str = ""


@dataclass
class PetPolicy:
    allowed: bool = False
    permitted_description: str = ""
    deposit: float = 0.0
    rent: float = 0.0
    revoke_days: int = 10
    insurance_required: bool = False


@dataclass
class Lease:
    filename: str
    agreement_date: str
    landlord: Landlord
    tenants: list[Tenant]
    occupants: list[str]
    property: Property
    term: Term
    rent: Rent
    deposit: Deposit
    nsf_fee: NsfFee
    landscaping: Landscaping
    entry: Entry
    subletting: Subletting
    disclosures: Disclosures
    insurance: Insurance
    condition_rows: list[ConditionRow]
    pets: PetPolicy
    sign_date: str = ""

    def to_context(self) -> dict:
        methods = {m.lower() for m in self.rent.methods}
        first_tenant = self.tenants[0] if self.tenants else None

        return {
            "date_made": self.agreement_date,
            "sign_date": self.sign_date or self.agreement_date,
            "landlord_name": self.landlord.name,
            "landlord_initials": self.landlord.initials
            or _initials(self.landlord.name),
            "tenant_name": _join_names([t.name for t in self.tenants]),
            "tenant_initials": (
                first_tenant.initials or _initials(first_tenant.name)
                if first_tenant
                else ""
            ),
            "occupants": ", ".join(self.occupants),
            "property_address": self.property.address,
            "included_property": ", ".join(self.property.included_personal_property),
            "property_addendum_attached": self.property.included_addendum_attached,
            "term_is_fixed": self.term.type == "fixed",
            "term_is_month_to_month": self.term.type == "month_to_month",
            "start_date": self.term.start,
            "end_date": self.term.end,
            "rent_amount": _money(self.rent.amount),
            "rent_due_day": _ordinal(self.rent.due_day),
            "pay_check": "check" in methods,
            "pay_transfer": bool(methods & {"transfer", "electronic", "ach"}),
            "pay_other": "other" in methods,
            "pay_other_desc": self.rent.other_method_desc,
            "payee": self.rent.payee or self.landlord.name,
            "nsf_fee": _money(self.nsf_fee.amount) if self.nsf_fee.enabled else None,
            "deposit_amount": _money(self.deposit.amount)
            if self.deposit.required
            else None,
            "water_landlord": self.landscaping.watering_by == "landlord",
            "water_tenant": self.landscaping.watering_by == "tenant",
            "maint_landlord": self.landscaping.maintenance_by == "landlord",
            "maint_tenant": self.landscaping.maintenance_by == "tenant",
            "landscaping_except": self.landscaping.exceptions,
            "keysafe_authorized": self.entry.keysafe_authorized,
            "sublet_short_term_applies": self.subletting.short_term_prohibited,
            "sublet_short_term_excluded": not self.subletting.short_term_prohibited,
            "disc_lead_paint": self.disclosures.lead_paint,
            "disc_pest": self.disclosures.pest_control,
            "disc_flood": self.disclosures.flood_hazard,
            "disc_mold": self.disclosures.mold,
            "insurance_required": self.insurance.required,
            "insurance_amount": (
                _money(self.insurance.amount) if self.insurance.required else None
            ),
            "condition_rows": [
                {"area": r.area, "condition": r.condition, "comments": r.comments}
                for r in self.condition_rows
            ],
            "pets_permitted": self.pets.permitted_description
            if self.pets.allowed
            else "",
            "pet_deposit": _money(self.pets.deposit) if self.pets.allowed else None,
            "pet_rent": _money(self.pets.rent) if self.pets.allowed else None,
            "pet_revoke_days": str(self.pets.revoke_days) if self.pets.allowed else "",
            "pet_insurance_required": (
                self.pets.insurance_required if self.pets.allowed else False
            ),
        }
