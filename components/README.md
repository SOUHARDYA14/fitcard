# FitCard frontend

A standalone component library — **not wired into the live site.**
`app.py` still serves the 7 Jinja templates in `templates/` exactly as
before; this project has no `package.json`, Node toolchain, or React
runtime today, and none of that was added. These files exist so the
duplication documented in `docs/COMPONENT_AUDIT.md` has a single,
correct place to live once the app is ready to consume it.

This doc covers the whole reorganized frontend layout, not just
`components/` — it's kept here since this is where the library's story
started, but the folders below all live as siblings at the repo root.

## Layout

```
components/   UI components — Button, Input, Card, Badge, Modal, Navbar, Footer
pages/        (placeholder) future page-level compositions — see pages/README.md
hooks/        reusable stateful logic — usePrefersReducedMotion, useMagnetic, useEscapeKey, useLockBodyScroll
lib/          framework-agnostic utilities — currently just cx() (class-name join)
styles/       tokens.css — the design-token source of truth
constants/    static lookup data — tiers.js (tier gradients/colors)
assets/       (placeholder) icons/images/fonts — see assets/README.md
```

Why `components/` doesn't have per-component subfolders (`components/Button/Button.jsx`
etc.): only 7 small, flat files — one extra nesting level wasn't worth the
churn for a library this size. Revisit if it grows.

## Why standalone, not wired in

Wiring these into the running Flask app would mean introducing a Node
build pipeline from scratch and touching every template and `app.py` —
a much larger, riskier change than "reduce duplication." Building the
library standalone, directly against `styles/tokens.css`, means each
component can match `docs/FITCARD_DESIGN_SPEC.md` exactly, with no
legacy CSS to reconcile against. Integration is a deliberate next step,
not a side effect of this pass.

## Requirements

- React 17+ (function components, hooks — no other runtime dependency)
- `styles/tokens.css` loaded once, globally, before these components render
- Each component imports its own co-located `.css` file (`Button.jsx` →
  `Button.css`, etc.) — a bundler that supports plain CSS imports
  (Vite, Webpack, Next, CRA) is assumed, but nothing here is
  bundler-specific

## Components

| Component | Legacy duplication it replaces | Source |
|---|---|---|
| `Button` | 6× gold-button declarations + 2× `.btn-google` | COMPONENT_AUDIT.md §1 |
| `Input` | standard input (4×), `label`/`.field`/`.hint` (4-5×), `.field-row` input, OTP override | COMPONENT_AUDIT.md §3, §6 |
| `Card` | `.card` auth wrapper (4× identical) + formalizes `.cc` recommendation card | COMPONENT_AUDIT.md §2 |
| `Badge` | `.rank`, `.cat-pill`, `.tier-dot`, `.cc-score` — four separate small-label patterns | COMPONENT_AUDIT.md (requested directly; not a literal duplicate, each had one call site) |
| `Modal` | none — **new primitive**, confirmed no modal/dialog exists anywhere in the codebase | COMPONENT_AUDIT.md §8 |
| `Navbar` | brand/chip logo (7×) + `.hero-row` (2×) + welcome `<nav>` | COMPONENT_AUDIT.md §4, §7 |
| `Footer` | welcome/match `<footer>` (2×, independently declared) | COMPONENT_AUDIT.md §5 |

`Button` and `Modal` also each use one or more of the hooks below —
neither hand-rolls its pointer/keyboard/scroll-lock logic inline anymore.

## Hooks (`hooks/`)

| Hook | Used by | Purpose |
|---|---|---|
| `usePrefersReducedMotion` | `useMagnetic` | live-updating OS reduced-motion preference |
| `useMagnetic` | `Button` (`magnetic` prop) | pointer-follow drift, matching legacy `.magnetic` from `static/theme.js`; skips itself under reduced motion |
| `useEscapeKey` | `Modal` | Escape-to-close |
| `useLockBodyScroll` | `Modal` | locks page scroll while open |

Extracted out of `Button.jsx`/`Modal.jsx` during the frontend
reorganization so they're independently reusable — a future toast or
dropdown can use `useEscapeKey` without copying Modal's effect.

## Lib (`lib/`)

`cx(...)` — joins class names, dropping falsy values. Every component
that builds a dynamic class list (`Button`, `Input`, `Card`, `Badge`,
`Footer`) used to have its own identical `[...].filter(Boolean).join(" ")`
inline; now there's one definition.

## Constants (`constants/`)

`tiers.js` — the shared tier lookup tables (moved here from
`components/tierTheme.js`). Gives the two independent legacy tier-color
mappings (`.cc.t-*` gradients vs `.tier-dot.*` colors) one definition each
instead of a copy wherever they're needed. Intentionally keeps the two
mappings **separate** (they use different colors for the same six tiers
in the original code) rather than merging them, since merging would
change what renders. Consumed by `Card` (gradients) and `Badge`
(dot colors) — import from `../constants`, not from inside `components/`.

## Pages (`pages/`) and Assets (`assets/`)

Both currently empty placeholders with their own README explaining
intended contents — see `pages/README.md` and `assets/README.md`. Not
populated here: building actual page-level compositions or sourcing
real asset files is new feature work, not a reorganization, and wasn't
asked for.

## Usage

```jsx
import { Button, Input, Card, Badge, Navbar, Footer } from "./components";
import "./styles/tokens.css"; // load once, at the app root

function LoginPage() {
  return (
    <Card variant="auth">
      <Navbar variant="brand-only" />
      <h1>Welcome back</h1>
      <Input id="email" type="email" label="Email" required />
      <Input id="password" type="password" label="Password" required />
      <Button type="submit" fullWidth>Sign in</Button>
    </Card>
  );
}
```

```jsx
<Card variant="recommendation" tier="luxury" best index={0}>
  <Badge variant="score" value={94.2} />
  <Badge variant="rank">Best match</Badge>
  {/* name, bank, meta, category Badges, reasons list — composed by the caller */}
</Card>
```

## What's deliberately not included

Only the 7 requested components were built. The audit also flagged
`FormField`, `ErrorBanner`/`InlineNote`, `ToggleChip`, `AuthFootLinks`,
and `AmbientBackground` as reusable candidates — not built here since
they weren't asked for, but `Input`'s `label`/`hint`/`error` props cover
the `FormField` case already, and `Badge`'s `tier` variant shares its
color source with `Card`'s `recommendation` variant via `constants/tiers.js`.

## Known open question

`docs/COMPONENT_AUDIT.md` §7 notes that only `welcome.html` has full
site navigation — `cards.html`/`match.html` only show a single back-link,
and the 4 auth pages have none. `Navbar`'s three variants (`full` /
`back-link` / `brand-only`) reproduce that exactly as-is; deciding
whether more pages *should* get full navigation is a product decision
this library doesn't make for you.
