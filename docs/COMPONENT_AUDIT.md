# FitCard Component Audit

Scan of the full frontend (`static/theme.css`, `static/theme.js`, all 7 files
in `templates/`) for duplicated UI. Companion to `docs/UI_AUDIT.md` (which
catalogs raw values); this file catalogs **components** — the same chunk of
markup+CSS copy-pasted across pages instead of shared once.

No `.js`/`.html`/`.css` outside `templates/`, `static/`, and `styles/` exist
in the project (`/insurance` is a reverse-proxied external service, not part
of this codebase — see `app.py:379`).

---

## 1. Buttons

**6 independent declarations of the same gold "primary" button:**

| File | Selector | Notes |
|---|---|---|
| welcome.html | `.btn.btn-primary` | anchor tag; adds `pulseGlow` idle animation, only variant that does |
| match.html | `button.submit-btn` | adds loading-spinner state, only variant that does |
| login.html | bare `button` | |
| login_phone.html | bare `button` | |
| signup.html | bare `button` | |
| verify_otp.html | bare `button` | |

All six share the identical core: `linear-gradient(180deg,#f0d090,#d8ab55)`
fill, `#211a09` text, Space Grotesk 600, `border-radius:10px`, hover
`filter:brightness(1.06)`. Each file redeclares this from scratch — a global
button-color change today means editing 6 places by hand.

**`.btn-google`** — declared identically in `login.html` and `signup.html`
(byte-for-byte same block, same inline SVG). 2 copies of one component.

**`.btn.btn-secondary`** — exists once, in welcome.html only. Not duplicated,
but it's the *only* secondary-button variant on the whole site — the 4 auth
pages and match.html have no equivalent "quiet" action button, so any future
auth-page secondary action would currently have nowhere to inherit from.

**`button.link`** (verify_otp.html "Resend code") — `all:unset` text button,
one instance, no duplicate.

### Recommendation
A `Button` component with variants — `primary`, `secondary`, `oauth`, `link`
— and a `loading` state built in (not bolted on only in match.html). Collapses
6+2 declarations into 1.

---

## 2. Cards

**Auth card wrapper `.card`** — declared identically in `login.html`,
`login_phone.html`, `signup.html`, `verify_otp.html` (4 copies): same
`width/max-width`, `background:var(--surface)`, border, `border-radius:var(--r)`,
`padding:38px 34px`, `box-shadow:0 30px 70px rgba(0,0,0,.4)`, `fadeUp`
entrance. This is the single clearest duplication in the codebase — 4 files,
one component, zero variation beyond the content inside it.

**Other card-shaped components are each single-instance** (not duplicated,
but worth naming since they're real components today with no reusable
definition):
- `.cc` recommendation card (match.html) — has internal tier variants (`t-entry/t-free/t-mid/t-super/t-luxury/t-na`) plus a `.best` modifier; effectively already "one component, several variants" but expressed as ad hoc classes rather than a documented component.
- `.mock-card` decorative card (welcome.html), with a second `.mock-card.back` modifier behind it.
- `.row` list row (cards.html) — flat, not boxed; conceptually a "compact card" but styled as a bordered row.
- `.state` / `.state.error` empty/error box (match.html).

### Recommendation
1. **`AuthCard`** — turn the 4-times-copied `.card` block into one partial (e.g. `templates/partials/auth_card.html` via Jinja `{% include %}`, or a shared CSS class pulled into `theme.css`). Highest-value fix in this audit — pure duplication, no logic differences.
2. Formalize `.cc` as a documented `Card` component with a `tier` variant prop, since match.html already treats it that way informally.

---

## 3. Inputs

**Standard text/email/password/tel input** — `login.html`, `login_phone.html`,
`signup.html`, `verify_otp.html` redeclare the same base block 4 times:
`background:var(--surface-2)`, `border:1px solid var(--line)`,
`border-radius:8px`, `padding:11px 12px`, `font-size:15px`, Inter, focus
border → gold. verify_otp.html overrides `font-size`/`letter-spacing`/
`text-align` on top of the same base for its OTP field (see §6).

**`.field` wrapper** (`label` + `input` + gap) — declared identically 4×
across the same auth pages, plus a near-duplicate in match.html (`.field`
exists there too, slightly different gap/margin).

**`label{...}`** (uppercase, muted, 12px) — declared identically in
`login.html`, `login_phone.html`, `signup.html`, `verify_otp.html`, and
match.html — 5 copies of the same rule.

**`.hint{...}`** — declared identically in `login_phone.html` and
`signup.html` (2 copies); `login.html` and `verify_otp.html` don't use hints
at all, so the pattern is inconsistently applied as well as duplicated.

**match.html has two more input-shaped patterns that don't exist anywhere
else**, each internally near-duplicated:
- `.field-row input, select` — same visual language as the standard input but different padding (`9px 10px` vs `11px 12px`) and a hand-rolled CSS-only select arrow. A near-miss duplicate of the standard input rather than a clean reuse.
- `.chip-toggle` and `.radio-toggle` (checkbox/radio styled as pills) — two blocks that are copy-pasted structurally (`display:inline-flex`, `border-radius`, `background`, `:has(input:checked)` swap) and differ only in corner radius (20px vs 10px) and accent color (gold vs mint) for the checked state.

**cards.html `.controls input, select`** — underline-only style, unique to
that page, no duplicate but also no shared base with the "standard input."

### Recommendation
1. **`Input`** component (base: surface-2 fill, bordered, 8px radius, gold focus) with size/variant props to cover the auth-page and match.html cases instead of two near-identical hand-rolled versions.
2. **`FormField`** (label + input + optional hint), replacing the 4–5× duplicated `.field`/`label`/`.hint` trio.
3. **`ToggleChip`** as one component with a `shape` (`pill`|`rounded`) and `accent` (`primary`|`success`) prop, replacing the copy-pasted `.chip-toggle`/`.radio-toggle` pair.
4. Leave `.controls` (cards.html underline filter field) as an intentional one-off *or* fold it into `Input` as a `variant="underline"` if that filter-bar pattern gets reused elsewhere.

---

## 4. Headers

**Brand mark + chip logo (`.brand` / `.brand .chip`)** — the gold gradient
chip-logo block is declared in **all 7 templates**, the widest duplication
found in this audit. Six of the seven use identical dimensions
(`20px×15px` chip, ~19–20px brand text); welcome.html alone uses a slightly
larger variant (`22px×16px` chip, 22px text) for the full-nav header.

**Two distinct "header" shapes exist, each itself duplicated:**

| Shape | Files | Contents |
|---|---|---|
| Full navbar | welcome.html only | brand + `.nav-links` (Match / All cards / Insurance / auth state) — see §7 Navbar |
| Mini header (`.hero-row`) | cards.html, match.html | brand + one or two plain-text "back" links (`.back-link` / `.browse-link`), no nav menu — declared independently in both files with near-identical CSS |
| Card-only brand | login.html, login_phone.html, signup.html, verify_otp.html | brand mark alone, inside `.card`, no links at all |

So there are effectively 3 header tiers today, none sharing a base — the
brand mark itself is the only truly shared visual, and it's shared by
copy-paste, not by reference.

### Recommendation
**`PageHeader`** component with a `variant` prop (`full-nav` | `back-link` |
`brand-only`) built from one shared `Brand` sub-component (logo chip + name).
Collapses 7 chip-logo declarations and the 2 duplicated `.hero-row` blocks
into one definition with 3 configurations.

---

## 5. Footers

Only **2 of 7 pages have a page footer** at all: welcome.html and
match.html. Both declare their own block independently — same intent
(`color:#4A5261`, `font-size:12px`, `border-top:1px solid var(--line)`,
centered text) but different `max-width` (1160px vs 820px) and different
margin values, so even the two that exist aren't sharing a definition.
cards.html and the 4 auth pages have no footer.

Separately, don't confuse the page footer with **`.foot`** (login/signup/
login_phone/verify_otp) — that's the small "Already have an account? /
Sign in with phone instead" links block *inside* the auth card, a different
component that happens to share a name. `.foot` itself is duplicated
identically across all 4 auth pages.

### Recommendation
1. **`PageFooter`** — one component for the disclaimer footer, parameterized by `maxWidth`; decide deliberately whether cards.html and the auth pages should get one too, rather than the current accidental omission.
2. **`AuthFootLinks`** — separate small component for the `.foot` auth-navigation links, replacing its 4× duplication.

---

## 6. OTP Inputs

Only **one** OTP input exists (`verify_otp.html #otp`) — not duplicated
today, since there's only one OTP flow. It's built by overriding the
standard input's `font-size`/`letter-spacing`/`text-align` inline in the same
`<style>` block rather than as a named variant.

### Recommendation
Not urgent (nothing to deduplicate yet), but worth formalizing as
`Input variant="otp"` now — the codebase already has two OTP-adjacent flows
(email OTP via Firebase/Resend, phone OTP via MSG91, per recent commit
history), so a second OTP entry point is a realistic near-term addition and
should reuse a defined variant rather than hand-rolling a second one-off.

---

## 7. Navbar

Exactly **one** real `<nav>` element in the project: welcome.html. It is not
duplicated, but it is also the *only* place site-wide navigation (Match / All
cards / Insurance / sign in-out) exists — cards.html and match.html only
offer a single "back" link each (see §4), and the 4 auth pages offer no
navigation at all beyond the brand mark. A user landing on `/cards` or
`/login` has no way to reach `/insurance` or toggle auth state without going
back through `/`.

### Recommendation
Decide whether that's intentional (minimal auth/utility pages) or an
oversight. If site nav should be reachable from more pages, extract
welcome.html's `<nav>` into the same `PageHeader` component from §4
(`variant="full-nav"`) and apply it to cards.html and match.html rather than
their current stripped-down `.hero-row`.

---

## 8. Modals

**None found.** No `modal`, `dialog`, `<dialog>`, or overlay-panel pattern
exists anywhere in `templates/` or `static/`. Current UI handles all
transient/blocking states with inline banners instead:
- `.error` (validation/server errors, 4 auth pages + match.html's `.state.error`)
- `.dev-otp` (verify_otp.html, dev-mode notice)
- `.widened-note` (match.html, "we relaxed a filter" notice)

That's a reasonable pattern for the current feature set (nothing here truly
needs to block interaction), but there's no primitive to reach for if a
future feature does need one — e.g. a confirm-before-logout prompt, a card
detail/comparison overlay, or a delete-account confirmation.

### Recommendation
No dedup needed. If a blocking confirmation or detail-overlay use case comes
up, build one `Modal` primitive (backdrop + focus trap + Esc-to-close) up
front rather than letting the first feature that needs one improvise its own
— the same way the button/card/input duplication above happened one page at
a time.

---

## Recommended Component Library

Consolidated list, ranked by how much duplication each removes:

| # | Component | Replaces | Copies removed |
|---|---|---|---|
| 1 | **`AuthCard`** | `.card` wrapper | 4 → 1 |
| 2 | **`PageHeader`** (`variant`: full-nav / back-link / brand-only) | `.brand`/`.brand .chip` (7×), `.hero-row` (2×), welcome `<nav>` (1×) | 7+2 → 1 |
| 3 | **`Button`** (`variant`: primary / secondary / oauth / link, `loading` state) | 6 gold-button declarations, 2× `.btn-google` | 8 → 1 |
| 4 | **`FormField`** (label + input + optional hint) | `.field`/`label`/`.hint` (4–5×) | 4–5 → 1 |
| 5 | **`Input`** (`variant`: default / underline / otp) | standard input (4×) + match.html's `.field-row input` near-duplicate | 5 → 1 |
| 6 | **`ErrorBanner`** / **`InlineNote`** (`tone`: error / warning / success) | `.error` (5×), `.dev-otp` (1×), `.widened-note` (1×) | 7 → 1, plus gets the new `--color-warning-*` tokens from `styles/tokens.css` a home |
| 7 | **`ToggleChip`** (`shape`, `accent` props) | `.chip-toggle` + `.radio-toggle` | 2 → 1 |
| 8 | **`AuthFootLinks`** | `.foot` | 4 → 1 |
| 9 | **`PageFooter`** (`maxWidth` prop) | welcome/match `<footer>` | 2 → 1, and gives cards.html/auth pages a definition to opt into |
| 10 | **`AmbientBackground`** (grain + aurora blobs + radial-gradient body bg) | `.aurora` (6×), body radial-gradient (6×) — not requested in the original 8 categories, but the single largest *raw CSS* duplication found while scanning for the above | 6 → 1 |

Items 1–5 correspond directly to the requested Buttons/Cards/Inputs/Headers
scan; 6–9 fill out Footers/Modals/OTP coverage; 10 surfaced as a side effect
of scanning every template and is included since it's larger (6 copies) than
several of the requested categories.

This report does not implement any of the above — it only identifies what to
build once `styles/tokens.css` is wired in, so the new components can be
written directly against tokens instead of against another round of literal
values.
