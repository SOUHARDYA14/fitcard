# FitCard Design Spec

The official frontend reference for FitCard. Every value below is pulled
directly from the current implementation — `styles/tokens.css`,
`components/`, `static/theme.css`, and `templates/*.html` — not invented.
Where the live site and the new component library disagree or only one of
them has shipped something, that's called out explicitly rather than
smoothed over.

**Supersedes** the earlier draft at `fitcard/docs/FITCARD_DESIGN_SPEC.md`
(a generic example-structure sketch from before the codebase had been
audited). This document is grounded in six audit/report passes:
`docs/UI_AUDIT.md`, `docs/COMPONENT_AUDIT.md`, `docs/ACCESSIBILITY_REPORT.md`,
`docs/ANIMATION_AUDIT.md`, `docs/CLEANUP_REPORT.md` — treat those as the
detailed appendices behind the summaries here.

**Two codebases, one spec.** FitCard today is a server-rendered Flask +
Jinja2 app (`templates/*.html` + `static/theme.css`/`theme.js`) — that's
what's actually live. Alongside it is a standalone React component
library (`components/`, `hooks/`, `lib/`, `constants/`, `styles/tokens.css`)
built to match this spec exactly, but **not yet wired into the running
app** — no Node toolchain exists in this project. Every section below
says which of the two (or both) it's describing.

---

## 1. Color System

Canonical source: `styles/tokens.css`. Legacy `--gold`/`--mint`/`--rose`/etc.
custom properties in `static/theme.css` map 1:1 to these (noted inline).

| Role | Token | Value |
|---|---|---|
| Primary | `--color-primary` | `#E5C07B` (gold) |
| Primary gradient | `--color-primary-soft` / `--color-primary-strong` | `#f0d090` → `#d8ab55` |
| Primary chip gradient | `--color-primary-chip-start` / `-end` | `#f6e2a8` → `#c9a24a` (lighter than the button gradient — logo/chip only) |
| On-primary text | `--color-on-primary` | `#211a09` |
| Secondary | `--color-secondary` / `--color-secondary-alt` | `#7c3aed` / `#3730a3` (violet/indigo — aurora, mid-tier gradient) |
| Text | `--color-text` / `--color-text-muted` | `#F2F4F8` / `#9AA4B2` |
| Background | `--color-bg` / `--color-surface` / `--color-surface-2` | `#0E1116` / `#171B22` / `#1F2530` |
| Success | `--color-success` | `#34D399` (mint) |
| **Warning** | `--color-warning` | `#FBBF24` — **new**, no warning state existed anywhere in the original UI; shaped to match success/danger's bg/border alpha pattern |
| Danger | `--color-danger` | `#F87171` (rose) |
| Border | `--color-border` | `#2A313D` |

Each of Primary/Success/Warning/Danger also has an alpha ramp
(`-a10`/`-a40`/etc.) for banner backgrounds and borders — see
`styles/tokens.css` for the full list. **Overlay** (`--color-overlay-white-*`,
`--color-overlay-black-*`) and **Tier** (`--color-tier-*`) sections exist
for the recommendation-card gradients and badges — the credit-card tier
system has **two independent color mappings for the same six tiers**
(card gradients vs. list-view dots), kept deliberately separate since
merging them would change what renders. See `constants/tiers.js`.

**Contrast, verified against WCAG AA (`docs/ACCESSIBILITY_REPORT.md` §1):**
body/muted/gold/mint/rose text all clear 6.8:1+ on dark backgrounds.
Two failures exist today: `--color-text-placeholder` on `--color-surface-2`
(2.57:1) and `--color-text-faint` (footer text) on `--color-bg` (2.41:1) —
both fail AA outright. Fix before shipping either as anything but
decorative.

**Rule:** never hand-write a hex/rgba value in new CSS — reference a
token. The one standing exception is the Google OAuth "G" logo's
brand-mandated multi-color mark (`components/Button.jsx`) — third-party
brand colors aren't FitCard's to tokenize.

---

## 2. Typography

**Families** (`--font-display`/`--font-body`/`--font-label`): Fraunces
(serif, italic for headings/brand/numerals), Inter (body copy),
Space Grotesk (buttons, data, uppercase labels). Loaded via Google Fonts
in every template's `<head>`.

**Semantic scale** (`styles/tokens.css`, new): `--text-heading-xl` (fluid
40–72px), `--text-heading-l` (28px), `--text-heading-m` (22px — `Modal`
title), `--text-body` (15px — buttons, inputs, `Modal` body),
`--text-caption` (13px), `--text-small` (12px). Each aliases an existing
raw size, so using it renders identically to the raw token.

**Raw scale**: 13 static steps `--text-50` (9px) through `--text-1200`
(28px), plus 4 fluid `--text-display-*` sizes for hero/section headings.
Not every raw size maps to a semantic role — `components/` alone uses 9
distinct sizes against only 6 semantic slots. Sizes that are incidental
numeric readouts (badge score, OTP digits, brand wordmark, a modal close
glyph) intentionally stay on the raw token rather than being mislabeled
as a "Heading" just because the pixel value happens to match — see
`docs/ANIMATION_AUDIT.md`'s sibling reasoning in `tokens.css` for the
full list of what's excluded and why.

**Weights**: 400/500/600 (Inter), 500/600/700 (Space Grotesk), 500/600
italic+upright (Fraunces). **Known waste** (`docs/CLEANUP_REPORT.md` §4):
Inter 600 and Space Grotesk 500 are fetched from Google Fonts on every
page load and never actually rendered anywhere — safe to drop from the
`<link>` URL.

**Line-height / letter-spacing**: `--leading-tight` (.95) through
`--leading-relaxed` (1.6); 8 `--tracking-*` steps for the
eyebrow/uppercase-label idiom used throughout (form labels, stat
indices, the vertical spine text).

---

## 3. Spacing

`styles/tokens.css`'s `--space-*` scale: `--space-N` = `2×N` px
(`--space-5` = 10px, `--space-12` = 24px, etc.), from `--space-0` (0) to
`--space-60` (120px), plus half-steps (`--space-4-5` = 9px) for the
handful of legacy odd-pixel values that don't land on the even-step
pattern. Anchored to the real padding/margin/gap frequency data in
`docs/UI_AUDIT.md` §3, not an abstract scale.

**Containers**: `--container-narrow` (820px, match.html), `--container-base`
(960px, cards.html), `--container-wide` (1160px, welcome.html/footer) —
three different page widths today with no shared default; pick
deliberately, don't assume one.

**Rule:** every `margin`/`padding`/`gap` in `components/*.css` uses a
`--space-*` token — verified with zero literal px values remaining as of
the spacing-standardization pass.

---

## 4. Components

Standalone library at `components/` (React 17+, function components +
hooks). **Not wired into the live site** — see §12. Full API and usage
examples: `components/README.md`.

| Component | Role |
|---|---|
| `Button` | primary/secondary/oauth/link variants, loading state, optional magnetic pointer-drift |
| `Input` | default/compact/underline/otp variants, built-in label/hint/error |
| `Card` | auth/recommendation/plain variants, tier-aware for recommendations |
| `Badge` | rank/category/tier/score — four small-label patterns unified |
| `Modal` | new primitive (no legacy source), dialog semantics + Escape/backdrop close |
| `Navbar` | full/back-link/brand-only variants around one shared brand mark |
| `Footer` | wide/narrow variants of the page-disclaimer bar |

Supporting layers introduced during the frontend reorganization:
`hooks/` (`useMagnetic`, `usePrefersReducedMotion`, `useEscapeKey`,
`useLockBodyScroll`), `lib/` (`cx()` class-name joiner), `constants/`
(`tiers.js` — the two independent tier-color mappings). See §12 for the
full folder layout.

Every component was built to eliminate a specific duplication found in
`docs/COMPONENT_AUDIT.md` — `Button` alone replaces 6 independent
gold-button declarations plus 2 copies of the Google OAuth button.
`Modal` is the one exception: it has no legacy call site at all, built
ahead of need per the audit's recommendation.

---

## 5. Buttons

**Variants**: `primary` (gold gradient), `secondary` (outlined), `oauth`
(Google sign-in), `link` (unstyled text button). **States**: `loading`
(spinner + dimmed label + `disabled`), `glow` (idle pulse-glow ring —
opt-in, only the original welcome-page CTA used this), `magnetic`
(pointer-follow drift, skipped automatically under
`prefers-reduced-motion`).

**Sizing**: `size="md"` (14px/26–28px padding) vs `size="compact"`
(13px/20px, matches the 4 legacy auth-page buttons) — the same visual
"primary button" renders at two different paddings depending on
context; `Button` exposes both rather than forcing one.

**Focus**: buttons keep the browser's native focus ring — they're the
one interactive element in the whole project that doesn't override
`outline`. Inputs do (§7); this is a deliberate asymmetry worth
preserving, not an inconsistency to "fix."

**No danger-variant button exists.** Error states are communicated via
banners only (`--color-danger-*`), never a filled destructive button —
if one gets built, match the primary/secondary structural pattern with a
danger color fill instead of inventing a new shape.

---

## 6. Cards

**Variants**: `auth` (surface fill, the 4-auth-page wrapper, `fadeUp`
entrance), `recommendation` (tier-gradient fill, 3D `dealIn` entrance,
pointer-tilt-ready), `plain` (new, generic surface container — no
legacy source).

**Tier system**: `recommendation` cards take a `tier` prop
(`entry`/`free`/`mid`/`super`/`luxury`/`na`) that sets the background
gradient from `constants/tiers.js`'s `TIER_GRADIENTS`. A `best` prop adds
the looping gold glow used for the top-ranked match. Composition is the
caller's job — `Card` provides the container only; score/rank/category
badges compose in via `Badge` (§4).

**Radius**: `--radius-2xl` (16px) for `auth`/`recommendation`; the one
outlier is the legacy welcome-page mock-card decoration at `--radius-3xl`
(18px), which has no equivalent in the component library.

---

## 7. Forms

**`Input` variants**: `default` (auth-page style, Inter), `compact`
(match-form style, Space Grotesk, tighter padding), `underline`
(cards.html filter-bar style — no fill, bottom border only), `otp`
(large spaced-out digits). Label/hint/error render inline via props —
this covers what would otherwise be a separate `FormField` component.

**Known accessibility gaps in the live form** (`docs/ACCESSIBILITY_REPORT.md`
§2, §6 — **not yet fixed in either codebase**):
- **Critical**: `match.html`'s Lounge Access / Lifestyle Benefits /
  Milestone Appetite groups hide their radio/checkbox inputs with
  `display:none`, which removes them from the tab order entirely —
  those three groups are currently unreachable by keyboard. Fix: a
  visually-hidden-but-focusable technique, not `display:none`.
- **High**: 6 form controls in `match.html` (2 `<select>`s + 3 groups)
  have a visible section label with no `for`/`fieldset` association to
  the control it describes.
- Every input everywhere (`templates/*.html` and `components/Input.css`)
  removes the native focus ring (`outline:none`) and relies on a 1px
  border-color change alone — high enough contrast to pass, but a weak
  signal on its own.

Any new form work should fix these, not repeat them.

---

## 8. Navigation

**`Navbar` variants**: `full` (brand + nav-links + auth state — the
original site's *only* real `<nav>`, on the welcome page), `back-link`
(brand + one or two plain links — cards/match pages), `brand-only`
(just the brand mark, inside the auth `Card`). All three share one
`Brand` sub-render so the chip-logo gradient has one definition instead
of the 7 copies `docs/COMPONENT_AUDIT.md` found.

**Known gap, unresolved**: only the welcome page has real site
navigation. A user on `/cards` or `/login` has no way to reach
`/insurance` or toggle auth state without returning to `/`. `Navbar`
reproduces this exactly as-is — whether more pages *should* get the
`full` variant is a product decision, not made here.

**`Footer`**: `wide` (1160px, welcome) / `narrow` (820px, match) — only
2 of 7 live pages have a footer at all; `cards.html` and the 4 auth
pages don't.

---

## 9. Animations

**Durations** (`styles/tokens.css`, standardized to 3 tiers): `--duration-fast`
(150ms — all hover/focus feedback), `--duration-medium` (300ms — Modal
backdrop), `--duration-slow` (600ms — one-shot entrances: card fade-up/
deal-in, navbar fade-up, modal panel-in). Open-ended looping/decorative
animations (button idle glow, loading spinner, card shine sweep) are
**deliberately excluded** from that scale and get their own tokens
(`--duration-loop-emphasis` 2.6s, `--duration-loop-spin` 0.7s,
`--duration-shine` 1s) — forcing a multi-second "breathing" loop onto a
600ms tier would either break the effect or flicker under reduced
motion. Full before/after mapping: `docs/ANIMATION_AUDIT.md`.

**Easing**: `--ease-standard` (ease), `--ease-out-soft`
(`cubic-bezier(.16,1,.3,1)` — entrances), `--ease-out-snap`
(`cubic-bezier(.22,1,.36,1)` — magnetic/tilt interactions).

**`prefers-reduced-motion` is respected in `components/`**: the 3 core
duration tokens collapse to `0.01ms` globally; the 3 loop/shine
animations get explicit `animation: none` per-component instead (a
collapsed-duration infinite loop flickers rather than stopping); the
JS-driven magnetic effect checks `matchMedia` directly. **The live site
does not have this yet** — `static/theme.css`'s `fadeUp`, aurora drift,
sparkle twinkle, shimmer text, and floating-card animations have no
reduced-motion handling at all.

**Rule for new work**: any new animation duration is one of the 3 tiers
unless it's a genuinely open-ended loop, in which case it gets its own
named token and its own explicit reduced-motion disable — never rely on
duration-collapse alone for something with `infinite`.

---

## 10. Responsive Rules

**Standard**: Mobile `< 640px` / Tablet `640–879px` / Desktop `≥ 880px`.
Revised 2026-07-23 (debt #4): the desktop split moved from `1024px` to
`880px` to match the Next.js side's `sm`(640)/custom-`880` Tailwind screens
one-for-one — `lg` is retired there, so `1024` no longer anchors anything
on either side. 4 of 7 pages (the auth flows) have no media queries at
all — fixed-width cards that don't need to respond.

**Important limitation**: `--breakpoint-sm`/`--breakpoint-md` in
`styles/tokens.css` are reference values only. CSS custom properties
cannot be used inside an `@media` condition
(`@media (max-width: var(--breakpoint-sm))` is invalid everywhere) — so
new `@media` rules must hand-write `640px`/`880px` to match the standard,
not attempt to reference the token. Making that programmatic would
require a build-time tool (`postcss-custom-media`), which this project
doesn't have.

---

## 11. Accessibility Rules

Full detail: `docs/ACCESSIBILITY_REPORT.md`. Rules distilled from it:

1. **Contrast** — text must clear 4.5:1 against its background (3:1 for
   large text/UI components). `--color-text-placeholder` and
   `--color-text-faint` currently fail this; don't add new uses of them
   for anything a user needs to read.
2. **Keyboard** — every interactive control must be a real
   `<button>`/`<a href>`/`<input>`/`<select>`, never a `display:none`
   input behind a styled label (the live match-form's critical bug) or a
   `<div onClick>`. No positive `tabindex` values.
3. **Focus indicators** — if you remove the native `outline` (as every
   text input does), the replacement must be clearly visible; don't
   remove it with no replacement at all.
4. **ARIA** — dynamic/live-updating regions (search result counts,
   fetched card results) need `aria-live`; the live site currently has
   none anywhere. `Modal` in `components/` is the reference
   implementation (`role="dialog"`, `aria-modal`, `aria-labelledby`,
   Escape-to-close) — match that shape for any future overlay.
5. **Images** — none exist in the project today (everything is CSS/inline
   SVG); if one is added, decorative graphics get `aria-hidden="true"`
   (see `Button.jsx`'s Google icon), meaningful ones get real alt text.
6. **Form labels** — every input needs a `for`/`id` pair or to be wrapped
   by its `<label>`; groups of radio/checkbox inputs need `<fieldset>`/
   `<legend>`, not a floating `<label>` with no association.
7. **Motion** — any new looping or interaction-triggered animation needs
   a `prefers-reduced-motion` accommodation (§9).

---

## 12. Folder Structure

```
templates/         Live Flask/Jinja2 pages (7 .html files) — what's actually served
static/             theme.css + theme.js — the live site's shared CSS/JS
app.py, auth.py,    Flask backend
scoring.py, etc.

components/         UI components — Button, Input, Card, Badge, Modal, Navbar, Footer
pages/               (placeholder) future page-level compositions — see pages/README.md
hooks/               reusable stateful logic — useMagnetic, usePrefersReducedMotion, useEscapeKey, useLockBodyScroll
lib/                 framework-agnostic utilities — cx()
styles/              tokens.css — the design-token source of truth
constants/           static lookup data — tiers.js
assets/              (placeholder) icons/images/fonts — see assets/README.md

docs/                This spec + every audit report behind it
fitcard/docs/        Superseded early draft of this spec
```

The bottom block (`components/` through `assets/`) is the standalone
frontend library — see `components/README.md` for the fuller rationale.
It sits as siblings of `templates/`/`static/` at the repo root rather
than under one `frontend/` parent, since that's lower-risk (no path
churn across the docs that already reference `styles/tokens.css` etc.)
and Flask+component-library repos commonly lay out this way.

`pages/` and `assets/` are intentionally empty placeholders — populating
them (real page compositions, real icon/image assets) is feature work,
not something a reorganization pass invents unprompted.

---

## 13. Coding Standards

**Tokens over literals.** Every color/spacing/radius/shadow/duration/font
value in new `components/*.css` must be a `var(--token)` from
`styles/tokens.css`. If the value you need doesn't have a token yet, add
one at the exact value needed (see `docs/CLEANUP_REPORT.md`'s and every
token-pass doc's precedent) rather than hand-writing a literal "just this
once." The two standing exceptions: Google's brand-mandated OAuth icon
colors, and CSS keywords that aren't really colors (`transparent`,
`currentColor`).

**Naming**: CSS classes are BEM-ish with an `fc-` prefix
(`fc-btn`, `fc-btn--primary`, `fc-btn__spinner`) to avoid collision if
this library and the live site's CSS ever load on the same page.
Design tokens are `--category-modifier[-variant]`
(`--color-primary-a40`, `--space-5-5`, `--text-heading-m`).

**Component structure**: one `.jsx` + one co-located `.css` per component,
flat in `components/` (no per-component subfolder — the library is small
enough that the extra nesting isn't earning its keep yet). Every
component:
- builds its class list with `cx()` from `lib/`, not a hand-rolled
  `.filter(Boolean).join(" ")`
- documents which legacy markup/CSS it replaces in a header JSDoc comment,
  with a `docs/COMPONENT_AUDIT.md` section reference where one exists
- extracts non-trivial stateful logic (pointer tracking, key listeners,
  scroll locking) into `hooks/`, not inline `useEffect`s, once more than
  one component would plausibly reuse it

**Motion**: see §9's rule — one of the 3 Fast/Medium/Slow tiers, or a
named bespoke token with an explicit reduced-motion disable.

**Don't silently "fix" the live site's inconsistencies while
tokenizing them.** Where the legacy templates have two different values
for conceptually the same thing (the two independent tier-color
mappings, e.g.), the token system preserves both rather than picking a
winner — that's a design decision for a human to make deliberately, not
a side effect of a refactor.

---

## 14. Deployment Checklist

**Today, only the Flask app deploys** — the component library isn't
built, bundled, or served by anything, so it has no deployment footprint
yet. Checklist reflects that reality:

**Flask app (current, live):**
- [ ] `requirements.txt` installed (`pip install -r requirements.txt`) — verified clean, every direct dependency is actually imported (`docs/CLEANUP_REPORT.md` §5)
- [ ] Required env vars set: `FLASK_SECRET_KEY`, `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`, `INSURANCE_SERVICE_URL`, `MSG91_AUTH_KEY`/`MSG91_SMS_TEMPLATE_ID`/`MSG91_EMAIL_TEMPLATE_ID`, `FIREBASE_SERVICE_ACCOUNT_JSON`, `RESEND_API_KEY`/`RESEND_FROM_EMAIL` (see `render.yaml`) — note `.env.example` is currently missing 3 keys that `.env`/`render.yaml` both have (`FIREBASE_SERVICE_ACCOUNT_PATH`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`); fix the example file before onboarding anyone new
- [ ] `credit_cards.db` present and migrated to the current schema (confirm any pending `migrate_auth.py`/`migrate_phone.py` runs are applied — they're not run automatically)
- [ ] `firebase-service-account.json` present locally / `FIREBASE_SERVICE_ACCOUNT_JSON` set in production (gitignored, never committed)
- [ ] Start command: `gunicorn app:app --bind 0.0.0.0:$PORT` (matches `Procfile` and `render.yaml`)
- [ ] `/insurance` reverse-proxy target (`INSURANCE_SERVICE_URL`) reachable

**Before the component library ships to production (future, not today):**
- [ ] A Node build step exists (none does currently) — Vite/Webpack/Next/CRA, whichever the integration plan picks
- [ ] `styles/tokens.css` is loaded once, globally, before any component renders
- [ ] The accessibility gaps in §11 are fixed in whichever templates/pages get migrated first — don't ship the keyboard-trap bug forward into the new implementation
- [ ] Unused font weights (Inter 600, Space Grotesk 500 — §2) are dropped from the Google Fonts URL if the migration touches font loading
- [ ] Decide the tier-color-mapping question (§1, §6) deliberately rather than let two answers ship silently
