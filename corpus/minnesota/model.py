from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


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


def _date_parts(date_str: str) -> tuple[str, str, str]:
    """Split 'Month DD, YYYY' into (month, day, year)."""
    try:
        parts = date_str.replace(",", "").split()
        return parts[0], parts[1], parts[2]
    except (IndexError, AttributeError):
        return ("", "", "")


@dataclass
class Owner:
    name: str
    address: str = ""
    phone: str = ""


@dataclass
class Tenant:
    name: str


@dataclass
class Term:
    is_month_to_month: bool = False
    months: int | None = None
    start: str = ""
    end: str = ""


@dataclass
class Utilities:
    paid_by_tenant: bool = False
    paid_by_owner: bool = False
    split: bool = False
    tenant_pays: str = ""
    owner_pays: str = ""


@dataclass
class Pets:
    allowed: bool = False
    cat_count: int | None = None
    dog_count: int | None = None
    max_weight_lbs: int | None = None
    description: str = ""


@dataclass
class Notices:
    owner_address: str = ""
    owner_phone: str = ""
    tenant_address: str = ""
    tenant_phone: str = ""


@dataclass
class Lease:
    filename: str
    date: str
    total_pages: int
    owner: Owner
    tenants: list[Tenant]
    property_address: str
    property_city: str
    property_county: str
    term: Term
    rent_amount: float
    utilities: Utilities
    deposit_amount: float
    late_fee_amount: float
    pets: Pets
    occupants: str
    notices: Notices
    is_cic: bool = False
    lead_paint: bool = False
    tenant_initials: str = ""
    has_garage: bool = False
    has_storage_unit: bool = False
    has_parking_stall: bool = False
    garage_stall_number: str = ""
    additional_terms: str = ""
    sign_date: str = ""

    def to_context(self) -> dict:
        tenant_name = _join_names([t.name for t in self.tenants])
        date_month, date_day, date_year = _date_parts(self.date)
        sign_month, sign_day, sign_year = _date_parts(self.sign_date or self.date)

        return {
            "date": self.date,
            "date_month": date_month,
            "date_day": date_day,
            "date_year": date_year,
            "total_pages": str(self.total_pages),
            "owner_name": self.owner.name,
            "owner_address": self.owner.address,
            "owner_phone": self.owner.phone,
            "tenant_name": tenant_name,
            "tenants": [{"name": t.name} for t in self.tenants],
            "property_address": self.property_address,
            "property_city": self.property_city,
            "property_county": self.property_county,
            "has_garage": self.has_garage,
            "has_storage_unit": self.has_storage_unit,
            "has_parking_stall": self.has_parking_stall,
            "garage_stall_number": self.garage_stall_number or None,
            # term
            "term_is_fixed": not self.term.is_month_to_month,
            "term_is_month_to_month": self.term.is_month_to_month,
            "term_months": str(self.term.months) if self.term.months else None,
            "term_start": self.term.start,
            "term_end": self.term.end if not self.term.is_month_to_month else None,
            # rent
            "rent_amount": _money(self.rent_amount),
            # utilities
            "utilities_by_tenant": self.utilities.paid_by_tenant,
            "utilities_by_owner": self.utilities.paid_by_owner,
            "utilities_split": self.utilities.split,
            "utilities_tenant_pays": self.utilities.tenant_pays or None,
            "utilities_owner_pays": self.utilities.owner_pays or None,
            # deposit & fees
            "deposit_amount": _money(self.deposit_amount),
            "late_fee_amount": _money(self.late_fee_amount),
            # pets
            "pets_allowed": self.pets.allowed,
            "pets_not_allowed": not self.pets.allowed,
            "pets_cat_count": str(self.pets.cat_count) if self.pets.cat_count is not None else None,
            "pets_dog_count": str(self.pets.dog_count) if self.pets.dog_count is not None else None,
            "pets_max_weight": str(self.pets.max_weight_lbs) if self.pets.max_weight_lbs is not None else None,
            "pets_description": self.pets.description or None,
            # occupants
            "occupants": self.occupants,
            # CIC
            "is_cic": self.is_cic,
            # notices
            "owner_notice_address": self.notices.owner_address or self.owner.address,
            "owner_notice_phone": self.notices.owner_phone or self.owner.phone,
            "tenant_notice_address": self.notices.tenant_address or None,
            "tenant_notice_phone": self.notices.tenant_phone or None,
            # lead paint
            "lead_paint": self.lead_paint,
            "tenant_initials": self.tenant_initials or None,
            # misc
            "additional_terms": self.additional_terms or None,
            "sign_date": self.sign_date or self.date,
            "sign_month": sign_month,
            "sign_day": sign_day,
            "sign_year": sign_year,
        }
