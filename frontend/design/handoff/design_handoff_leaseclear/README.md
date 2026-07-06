# Handoff: LeaseClear (Document Q&A App)

## Overview
LeaseClear is a document-Q&A web app for residential leases. Users upload lease PDFs, select which ones are "in context," and ask questions in a chat interface that answers with inline citations back to source clauses. This package covers two screens: **Login** and the **Main App** (Sources panel + Chat panel).

## About the Design Files
The files in this bundle (`LeaseClear.dc.html`) are **design references built in HTML** — high-fidelity prototypes showing the intended look, layout, and static interaction states. They are not production code to copy directly. The task is to **recreate this design in the target codebase's existing environment** (React was requested) using React's established patterns — componentized, with real state management, routing, and API integration — rather than embedding this HTML as-is. If the target repo has an existing component library/design system, prefer its primitives (buttons, inputs, checkboxes) styled to match the tokens below, rather than introducing new ones.

## Fidelity
**High-fidelity.** Colors, typography, spacing, radii, and copy are final/intended. Recreate pixel-precisely using the values below. The chat conversation content and file names shown are illustrative placeholder data — wire up real data from the backend.

## Design Tokens

### Color palette — "tonal grayscale, no accent hue"
The product deliberately has **no colored accent**. All emphasis is done through neutral value contrast (near-black surfaces, near-white for emphasis) rather than hue. This was chosen over four other explored options (blue, teal, indigo, warm/amber accents) specifically for a calmer, more neutral "legal document" feel.

- Page background: `#16171b` (login), `#17181b`/`#16171b` interchangeable near-black
- Panel/card background: `#1e2025`
- Input / secondary-button background: `#26282e`
- Row hover background: `rgba(255,255,255,0.05)`
- Hairline border (all panels, inputs, dividers): `rgba(255,255,255,0.08)` default, `rgba(255,255,255,0.1)` on inputs, `rgba(255,255,255,0.16)` on hover
- Primary text: `#ECEDEF`
- Secondary text: `rgba(236,237,239,0.62)`
- Tertiary / muted text (placeholders, counts): `rgba(236,237,239,0.4)` – `rgba(236,237,239,0.5)`
- **Emphasis color (replaces "accent")**: `#EDEDEF` (near-white) — used for the logo mark, primary buttons, and the send button. Text/icons on top of it are dark: `#17181b`
- Emphasis hover: `#ffffff`
- Citation chip: text `#ECEDEF`, background `rgba(255,255,255,0.1)`, border `rgba(255,255,255,0.18)`
- Avatar background (neutral, distinct from emphasis color): `#3C4450`, initials text `#ECEDEF`
- Focus ring: `box-shadow: 0 0 0 3px rgba(255,255,255,0.12)` with border `rgba(255,255,255,0.4)`

### Typography
- Font: **Inter** (weights 400, 500, 600), fallback `system-ui, -apple-system, sans-serif`
- Sizes in use: 17px (login title), 15px (app wordmark), 14.5px (chat text/bubbles), 14px (inputs), 13.5px (panel headers), 13px (source names, select-all), 12.5px (form labels, secondary button text), 12px (counts), 11.5px (citation chip), 11px, 10px
- Weights: regular (400) for body copy, medium (500) for labels/secondary buttons, semibold (600) for headings/primary buttons/wordmark

### Radii
- Cards/panels: 12px
- Buttons/inputs: 8px
- Logo mark: asymmetric `14px 14px 14px 4px` (speech-bubble shape — flat corner bottom-left)
- Chat input pill: 24px (fully rounded)
- Citation chips: 20px (fully rounded/pill)
- Source-list PDF icon: 3px

### Shadows
- Login card: `0 8px 30px rgba(0,0,0,0.35)`
- Dropdown menu: `0 6px 20px rgba(0,0,0,0.4)`
- No shadow on the two main app panels — border only (never combine border + shadow on the same element in this system)

### Spacing
- Page padding (app content area): 28px horizontal, 20px vertical
- Panel internal padding: 14–18px
- Gap between Sources and Chat panels: 20px
- Row gap in lists: ~2px margin, 9px vertical padding per row
- Form field gap: 14px

## Logo
Speech-bubble mark: a rounded rectangle with one flat corner (`border-radius: 14px 14px 14px 4px`, ~46×38px on login, ~32×26px in the top bar), filled `#EDEDEF`, with a centered checkmark icon (`stroke: #17181b`, stroke-width ~2.6–2.8, rounded caps/joins). Paired with the wordmark "LeaseClear" in Inter 600.

## Screens

### 1. Login
**Purpose:** Authenticate before accessing lease documents.
**Layout:** Full-viewport, flex center. A single card, 380px max-width, centered both axes, 36px/32px padding.
**Contents (top to bottom):**
1. Logo mark + "LeaseClear" wordmark, stacked, centered, 14px gap
2. Subtitle: "Sign in to ask questions about your lease" (13px, secondary text, centered)
3. Email field (label + input)
4. Password field (label + input)
5. "Forgot password?" link, right-aligned, secondary text, hover → primary text color
6. Primary button "Sign in" — full width, emphasis-colored background, dark text, 11px vertical padding
7. Divider row: hairline — "or" — hairline
8. Secondary button "Continue with Google" — full width, `#26282e` background, hairline border, Google "G" logo (real 4-color mark) + label

**States:** Inputs get a focus ring (see tokens). Buttons darken/lighten background on hover (see tokens).
**Behavior:** Both "Sign in" and "Continue with Google" navigate to the Main App in the prototype (real auth wiring is out of scope here).

### 2. Main App
**Purpose:** Manage source documents and ask questions about them.
**Layout:** Full-viewport column: top bar (fixed height), then a flex row filling remaining height with two panels and a 20px gap, padded 28px/20px.

**Top bar:**
- Height: auto (14px vertical padding), bottom hairline border
- Left: logo mark (30px-ish) + "LeaseClear" wordmark
- Right: circular avatar, 32px, `#3C4450` background, initials "JD" centered, 12.5px semibold

**Left panel — Sources (300px fixed width):**
1. Header row: "Sources" label (13.5px semibold) + count "X of Y" (12px muted), space-between
2. "Upload documents" button: full-width, secondary-button style, up-arrow-into-tray icon + label, centered
3. "Select all" row: right-aligned — label (13px) then checkbox (15×15, accent = emphasis color) then a 22px spacer matching the row's kebab-button width (for checkbox alignment with rows below). Bottom hairline border.
4. Scrollable source list. Each row: PDF icon (26×30px rounded rect with folded corner + tiny "PDF" caption) → filename (13px, truncates with ellipsis) → checkbox (right-aligned, aligned with header checkbox) → kebab button "⋯" (22px circular hit area, hover background). Kebab opens a small absolute-positioned dropdown (min-width 110px) with a single "Remove" item (not wired up — visual only per spec).
   - Row hover: `rgba(255,255,255,0.05)` background, 8px radius.

**Right panel — Chat (flexible width):**
1. Scrollable message list, 28px/32px padding, 22px gap between messages.
   - User messages: right-aligned, compact rounded bubble (`#26282e` background, 14px radius, 10×15px padding, max-width 72%)
   - Assistant messages: left-aligned, **no background/box**, max-width 84%, 14.5px, line-height 1.7 — plain flowing text like Claude/ChatGPT
   - Citations: rendered **inline** within assistant text as small pill badges (see tokens) — never as a separate list or footnote block
2. Input bar, top hairline border, 16–20px padding: a pill-shaped input (24px radius, `#26282e` bg, hairline border, focus → lighter border) containing a text input (placeholder "Ask a question about your lease…") and a circular send button (34px, emphasis-colored bg, up-arrow icon in dark stroke).

## Sample Content (placeholder — replace with real data)
- Sources: "123 Oak Street Lease Agreement.pdf" (selected), "Pet Policy Addendum.pdf" (selected), "Move-In Inspection Report.pdf" (not selected), "Lease Renewal Notice 2026.pdf" (selected)
- Chat: three Q&A turns covering security deposit / return timeline, pet policy & pet deposit, and late-rent fee — each assistant answer cites clause references like "Lease · §4.1" inline.

## Interactions & Behavior (prototype scope)
- Checkbox toggle per source row (local state)
- "Select all" toggles all rows on/off based on current all-checked state
- Kebab (⋯) opens/closes a per-row dropdown with a "Remove" item (click closes the menu; no actual removal wired — intentionally out of scope per the design brief)
- Sign in / Continue with Google → navigates from Login to Main App
- **Explicitly out of scope for this handoff** (per design brief): citation hover tooltips/previews, actual source removal, settings screen, dark/light mode toggle (app is dark-mode only by design), profile picture upload, real chat input send/streaming behavior, real authentication.

## State Management (suggested)
- `view`: 'login' | 'app'
- `sources[]`: `{ id, name, checked }`
- `openMenuId`: id of source row with open kebab dropdown, or null
- `messages[]`: `{ role: 'user' | 'assistant', text? , segments?: [{type: 'text'|'citation', value, citationRef?}] }` — for a real build, citations should probably carry a clause/document reference (id, page, snippet) rather than just a display string, so they can support future hover/click-to-source behavior.

## Assets
- Google "G" logo: standard 4-color multi-path SVG (included inline in the HTML file), used as-is — this is Google's publicly documented brand mark, safe to reuse for a "Sign in with Google" button.
- No other external image assets; PDF icon and logo mark are drawn with CSS/SVG shapes.

## Files in this package
- `LeaseClear.dc.html` — the design reference file (Design Component format; open directly in a browser to view/interact with the static prototype). Contains both the Login and Main App screens with the final "tonal grayscale" palette and speech-bubble logo applied.
