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
    included_personal_property: list[str] = field(default_factory=list)
    furnished: bool = False


@dataclass
class Term:
    type: Literal["fixed", "month_to_month"]
    start: str
    end: str = ""
    end_time: Literal["AM", "PM"] = "PM"


@dataclass
class Rent:
    amount: float
    due_day: int = 1
    methods: list[str] = field(default_factory=lambda: ["personal check"])
    payee_name: str = ""
    payee_phone: str = ""
    payee_address: str = ""
    payment_hours_start: str = ""
    payment_hours_end: str = ""
    payment_days: str = ""
    other_method_desc: str = ""


@dataclass
class Deposit:
    amount: float
    held_by: Literal["owner", "broker"] = "owner"


@dataclass
class MoveInCost:
    category: str
    total_due: float | None = None
    payment_received: float | None = None
    balance_due: float | None = None
    date_due: str = ""


@dataclass
class Parking:
    permitted: bool = True
    description: str = ""
    included_in_rent: bool = True
    monthly_fee: float | None = None


@dataclass
class Storage:
    permitted: bool = True
    description: str = ""
    included_in_rent: bool = True
    monthly_fee: float | None = None


@dataclass
class LateCharge:
    grace_days: int = 5
    amount: float = 0.0
    nsf_fee: float = 25.0


@dataclass
class ConditionOfPremises:
    option: Literal["A", "B", "C", "D"] = "A"
    exceptions: str = ""
    inspection_days: int = 3
    other_desc: str = ""


@dataclass
class Utilities:
    tenant_pays_all: bool = True
    landlord_pays: list[str] = field(default_factory=list)
    additional_charges: str = ""


@dataclass
class HOA:
    applicable: bool = False
    name: str = ""


@dataclass
class Maintenance:
    watering_by: Literal["landlord", "tenant"] = "tenant"
    maintenance_by: Literal["landlord", "tenant"] = "landlord"
    watering_exceptions: str = ""
    maintenance_exceptions: str = ""


@dataclass
class Keys:
    premises_keys: int = 1
    mailbox_keys: int = 0
    common_area_keys: int = 0
    garage_remotes: int = 0
    rekeyed: bool = False


@dataclass
class PetPolicy:
    allowed: bool = False
    permitted_description: str = ""


@dataclass
class MilitaryOrdinance:
    applicable: bool = False


@dataclass
class Agency:
    listing_firm: str = ""
    listing_agent_represents: Literal["landlord_only", "both"] = "landlord_only"
    leasing_firm: str = ""
    leasing_agent_represents: Literal["tenant_only", "landlord_only", "both"] = (
        "tenant_only"
    )
    lease_exceeds_one_year: bool = False


@dataclass
class Broker:
    leasing_firm: str = ""
    leasing_agent: str = ""
    leasing_address: str = ""
    leasing_phone: str = ""
    leasing_fax: str = ""
    listing_firm: str = ""
    listing_agent: str = ""
    listing_address: str = ""
    listing_phone: str = ""
    listing_fax: str = ""


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
    move_in_costs: list[MoveInCost]
    parking: Parking
    storage: Storage
    late_charge: LateCharge
    condition: ConditionOfPremises
    utilities: Utilities
    hoa: HOA
    maintenance: Maintenance
    keys: Keys
    pets: PetPolicy
    lead_paint: bool
    military_ordinance: MilitaryOrdinance
    agency: Agency
    broker: Broker
    sign_date: str = ""
    other_terms: str = ""
    attached_supplements: str = ""

    def to_context(self) -> dict:
        methods = {m.lower() for m in self.rent.methods}
        first_tenant = self.tenants[0] if self.tenants else None
        rent_start = self.term.start

        # Move-in costs table rows
        move_in_rows = []
        for c in self.move_in_costs:
            move_in_rows.append(
                {
                    "category": c.category,
                    "total_due": _money(c.total_due) if c.total_due is not None else "",
                    "payment_received": _money(c.payment_received)
                    if c.payment_received is not None
                    else "",
                    "balance_due": _money(c.balance_due)
                    if c.balance_due is not None
                    else "",
                    "date_due": c.date_due,
                }
            )

        return {
            "agreement_date": self.agreement_date,
            "sign_date": self.sign_date or self.agreement_date,
            "landlord_name": self.landlord.name,
            "landlord_address": self.landlord.address,
            "landlord_phone": self.landlord.phone,
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
            "furnished": self.property.furnished,
            # Term
            "term_is_fixed": self.term.type == "fixed",
            "term_is_month_to_month": self.term.type == "month_to_month",
            "start_date": self.term.start,
            "end_date": self.term.end,
            "end_time_am": self.term.end_time == "AM",
            "end_time_pm": self.term.end_time == "PM",
            # Rent
            "rent_amount": _money(self.rent.amount),
            "rent_due_day": _ordinal(self.rent.due_day),
            "pay_cash": "cash" in methods,
            "pay_check": "personal check" in methods,
            "pay_money_order": "money order" in methods,
            "pay_cashier_check": "cashier check" in methods,
            "pay_other": "other" in methods,
            "pay_other_desc": self.rent.other_method_desc,
            "payee_name": self.rent.payee_name or self.landlord.name,
            "payee_phone": self.rent.payee_phone or self.landlord.phone,
            "payee_address": self.rent.payee_address or self.landlord.address,
            "payment_hours_start": self.rent.payment_hours_start,
            "payment_hours_end": self.rent.payment_hours_end,
            "payment_days": self.rent.payment_days,
            # Deposit
            "deposit_amount": _money(self.deposit.amount),
            "deposit_held_by_owner": self.deposit.held_by == "owner",
            "deposit_held_by_broker": self.deposit.held_by == "broker",
            # Move-in costs
            "rent_period_start": rent_start,
            "move_in_rows": move_in_rows,
            # Parking
            "parking_permitted": self.parking.permitted,
            "parking_not_permitted": not self.parking.permitted,
            "parking_description": self.parking.description,
            "parking_included_in_rent": self.parking.included_in_rent,
            "parking_not_included_in_rent": not self.parking.included_in_rent,
            "parking_fee": _money(self.parking.monthly_fee)
            if self.parking.monthly_fee
            else None,
            # Storage
            "storage_permitted": self.storage.permitted,
            "storage_not_permitted": not self.storage.permitted,
            "storage_description": self.storage.description,
            "storage_included_in_rent": self.storage.included_in_rent,
            "storage_not_included_in_rent": not self.storage.included_in_rent,
            "storage_fee": _money(self.storage.monthly_fee)
            if self.storage.monthly_fee
            else None,
            # Late charge
            "late_grace_days": str(self.late_charge.grace_days),
            "late_charge_amount": _money(self.late_charge.amount),
            "nsf_fee": _money(self.late_charge.nsf_fee),
            # Condition
            "condition_option_a": self.condition.option == "A",
            "condition_option_b": self.condition.option == "B",
            "condition_option_c": self.condition.option == "C",
            "condition_option_d": self.condition.option == "D",
            "condition_exceptions": self.condition.exceptions,
            "condition_inspection_days": str(self.condition.inspection_days),
            "condition_other_desc": self.condition.other_desc,
            # Utilities
            "utilities_additional": self.utilities.additional_charges,
            "landlord_pays_utilities": ", ".join(self.utilities.landlord_pays)
            if self.utilities.landlord_pays
            else "",
            # Occupants / pets
            "occupants_list": ", ".join(self.occupants),
            "pets_exception": self.pets.permitted_description
            if self.pets.allowed
            else "",
            # HOA
            "is_hoa": self.hoa.applicable,
            "hoa_name": self.hoa.name,
            # Maintenance
            "water_landlord": self.maintenance.watering_by == "landlord",
            "water_tenant": self.maintenance.watering_by == "tenant",
            "maint_landlord": self.maintenance.maintenance_by == "landlord",
            "maint_tenant": self.maintenance.maintenance_by == "tenant",
            "watering_exceptions": self.maintenance.watering_exceptions,
            "maintenance_exceptions": self.maintenance.maintenance_exceptions,
            # Keys
            "premises_keys": str(self.keys.premises_keys),
            "mailbox_keys": str(self.keys.mailbox_keys),
            "common_area_keys": str(self.keys.common_area_keys),
            "garage_remotes": str(self.keys.garage_remotes),
            "locks_rekeyed": self.keys.rekeyed,
            "locks_not_rekeyed": not self.keys.rekeyed,
            # Disclosures
            "lead_paint": self.lead_paint,
            "military_ordinance": self.military_ordinance.applicable,
            # Agency
            "listing_firm": self.agency.listing_firm,
            "listing_represents_landlord_only": self.agency.listing_agent_represents
            == "landlord_only",
            "listing_represents_both": self.agency.listing_agent_represents == "both",
            "leasing_firm": self.agency.leasing_firm,
            "leasing_represents_tenant_only": self.agency.leasing_agent_represents
            == "tenant_only",
            "leasing_represents_landlord_only": self.agency.leasing_agent_represents
            == "landlord_only",
            "leasing_represents_both": self.agency.leasing_agent_represents == "both",
            "lease_exceeds_one_year": self.agency.lease_exceeds_one_year,
            # Broker signatures
            "broker_leasing_firm": self.broker.leasing_firm,
            "broker_leasing_agent": self.broker.leasing_agent,
            "broker_leasing_address": self.broker.leasing_address,
            "broker_leasing_phone": self.broker.leasing_phone,
            "broker_leasing_fax": self.broker.leasing_fax,
            "broker_listing_firm": self.broker.listing_firm,
            "broker_listing_agent": self.broker.listing_agent,
            "broker_listing_address": self.broker.listing_address,
            "broker_listing_phone": self.broker.listing_phone,
            "broker_listing_fax": self.broker.listing_fax,
            # Misc
            "other_terms": self.other_terms,
            "attached_supplements": self.attached_supplements,
        }
