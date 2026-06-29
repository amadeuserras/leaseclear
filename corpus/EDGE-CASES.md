# Edge Cases 

Edge cases planted in each template where any of the steps (parsing, chunking, retreival, generation) could choke on. Used to source eval questions. 

# Meridian Template

### 1. Checkbox mechanism
Form has checkbox fields throughout: term type (§2), payment methods (§3A), garden duties (§6C), short-term-rental ban (§10), disclosures (§11A–E), liability insurance (§12), pet insurance (Sched A §6). ☐ and ☒ are near-identical chars in flat text. *(Which boxes are marked is value-level.)*

### 2. Contradictions (Override structure)
- §7 "no pets" → Pet Addendum can grant pets *and says it controls*.
- §6C garden duties → §6D water restrictions *supersede* §6C.
- §2B fixed term → converts to month-to-month if Landlord accepts rent after end date.

### 3. Text outside any clause
Preamble (parties, date, address), move-in condition table (§13), initials/signature blocks. Not inside a numbered section — check the chunker keeps them findable.

### 4. "Only if checked" conditional logic
§11 disclosures apply *only if* their box is checked. Structural trap: §11D (mold) ventilation duties apply "whether or not this box is checked."

### 5. Embedded definitions
"Rent" (§3) = all monetary obligations *except* the deposit; Pet Addendum says pet rent *is* part of Rent. Deposit is explicitly *not* Rent.

### 6. Conditional charges & cross-references
- Drain blockages: Tenant pays *unless* defective plumbing / tree roots (§6B).
- Entry: 24h notice *unless* emergency / tenant present+consents / abandoned (§9B).
- Cross-refs to chase: §4, §14, Schedule A.

### 7. Structural gaps (refusal targets in every cousin)
Form has no field for these, so every fill is silent on them:
- **No late fee** — only a *returned-payment* fee (§3B), the lookalike trap.
- **No smoking** policy.
- **No parking** clause.
- **Deposit-return deadline** = fixed wording "period required by law" (§5) — never a number.

# California Template

### 1. Checkbox mechanism
Checkbox fields throughout: term type (§2), payment methods (§3D), parking (§6), storage (§7), condition (§9), garden duties (§16B–C), keys (§18), and the unchecked disclosures (HOA §15, lead paint §22, military §34, interpreter §42). ☐ and ☒ are near-identical chars in flat text. *(Which boxes are marked is value-level.)*

### 2. Contradictions / lookalikes
- Title says "...OR MONTH-TO-MONTH" and §2A fully describes it → but **§2B (fixed lease) is the box checked**.
- §13 "No animal or pet" → *except* one cat. Pets are allowed.
- §2B fixed term → converts to month-to-month if Landlord accepts rent after end date.

### 3. Text outside any clause
Preamble (parties, address), move-in costs table (§5), repeated page boilerplate (copyright, initials, "PAGE X OF 4"), signature page. Not inside a numbered clause — check the chunker keeps them findable and strips the boilerplate.

### 4. "Only if checked" conditional logic
Disclosures apply *only if* their box is ticked — all unchecked here: HOA (§15), lead paint (§22), military munitions (§34), interpreter (§42). Correct answer to each = "not applicable."

### 5. Inversions ("except" flips the rule)
- **Utilities** (§11): Tenant pays all *except* trash + water/sewer (Landlord pays those).
- **Garden** (§16): Tenant waters, Landlord maintains — *except* tenant's patio container plants.
- Deposit *shall not* be used in lieu of last month's rent (§4B).

### 6. Conditional charges & cross-references
- Drain blockages: Tenant pays *unless* defective plumbing / tree roots (§16A).
- Entry: 24h notice *unless* emergency (§19).
- Cross-refs to chase: §2A (holdover), §3 (parking/storage rent), §9 → §24 (move-out), §24 → §25 (early termination).

### 7. Refusal / nuance targets
- **Pet Agreement Addendum** referenced as attached (§38) but *not in this PDF* — the clean "not in document" trap.
- **Deposit: two numbers** — §4A says $2,650; §5 table shows only $1,325 received, $1,325 still due.
- **No "grace period" label** — the 5-day window is buried in the late-charge clause (§8), alongside two fees ($100 late, $25 NSF).