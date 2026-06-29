from __future__ import annotations

from dataclasses import dataclass


def _money(x: float | None) -> str | None:
    return f"${x:,.2f}" if x is not None else None


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


def _date_parts(date_str: str) -> tuple[str, str, str]:
    """Split 'Month DD, YYYY' into (day, month, year) for the signature block."""
    try:
        parts = date_str.replace(",", "").split()
        return parts[1], parts[0], parts[2]
    except (IndexError, AttributeError):
        return ("", "", "")


@dataclass
class Landlord:
    name: str
    address: str = ""
    phone: str = ""


@dataclass
class Tenant:
    name: str


@dataclass
class Property:
    address: str


@dataclass
class Term:
    start: str
    end: str


@dataclass
class Rent:
    amount: float
    late_charge_per_day: float = 0.0
    nsf_fee: float = 0.0
    holdover_amount: float | None = None


@dataclass
class Animals:
    permitted: bool = False
    unauthorized_fee_per_day: float = 0.0


@dataclass
class Lease:
    filename: str
    agreement_day: str
    agreement_month: str
    agreement_year: str
    landlord: Landlord
    tenants: list[Tenant]
    occupants: str
    property: Property
    term: Term
    rent: Rent
    deposit_amount: float
    animals: Animals
    lead_paint: bool = False
    sign_date: str = ""

    def to_context(self) -> dict:
        tenant_name = _join_names([t.name for t in self.tenants])

        sign_day, sign_month, sign_year = _date_parts(self.sign_date or "")
        landlord_sign_day, landlord_sign_month, landlord_sign_year = _date_parts(
            self.sign_date or ""
        )

        return {
            "agreement_day": self.agreement_day,
            "agreement_month": self.agreement_month,
            "agreement_year": self.agreement_year,
            "landlord_name": self.landlord.name,
            "landlord_address": self.landlord.address,
            "tenant_name": tenant_name,
            "tenants": [{"name": t.name} for t in self.tenants],
            "occupants": self.occupants,
            "property_address": self.property.address,
            "term_start": self.term.start,
            "term_end": self.term.end,
            "rent_amount": _money(self.rent.amount),
            "late_charge_per_day": _money(self.rent.late_charge_per_day)
            if self.rent.late_charge_per_day
            else None,
            "nsf_fee": _money(self.rent.nsf_fee) if self.rent.nsf_fee else None,
            "holdover_amount": _money(self.rent.holdover_amount)
            if self.rent.holdover_amount is not None
            else None,
            "deposit_amount": _money(self.deposit_amount),
            "animals_permitted": self.animals.permitted,
            "unauthorized_animal_fee": _money(self.animals.unauthorized_fee_per_day)
            if self.animals.unauthorized_fee_per_day
            else None,
            "lead_paint": self.lead_paint,
            "sign_day": sign_day,
            "sign_month": sign_month,
            "sign_year": sign_year,
            "landlord_sign_day": landlord_sign_day,
            "landlord_sign_month": landlord_sign_month,
            "landlord_sign_year": landlord_sign_year,
        }
