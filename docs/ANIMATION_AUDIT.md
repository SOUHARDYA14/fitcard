# FitCard Animation Audit

Scope: `components/` (the standalone React library — the live `templates/*.html`
site has its own, separate set of `@keyframes`/`animation`/`transition` rules
that this pass didn't touch; see `docs/UI_AUDIT.md` §9 for those). Every
animation and transition in the library is inventoried below, with the
before/after duration mapping and reduced-motion coverage.

## Before: 7-step scale, 2 unused

| Old token | Value | Used by |
|---|---|---|
| `--duration-fast` | 150ms | Button/Modal/Navbar hover-feedback transitions |
| `--duration-base` | 200ms | Card hover transform/shadow, Input border-color |
| `--duration-moderate` | 250ms | *(none — defined, never used)* |
| `--duration-slow` | 350ms | Modal backdrop fade-in |
| `--duration-slower` | 500ms | Card fade-up, Navbar fade-up, Modal panel-in |
| `--duration-slowest` | 650ms | Card deal-in (×2: base + best-match) |
| `--duration-entrance` | 700ms | *(none — defined, never used)* |

Plus 4 more durations hardcoded directly in `animation:` shorthand, not
tokenized at all: Button pulse-glow (2.6s), Button spinner (0.7s), Card
shine sweep (1s), Card best-match glow (2.6s).

## After: Fast / Medium / Slow + 3 bespoke loop tokens

| New token | Value | Role |
|---|---|---|
| `--duration-fast` | 150ms | All hover/focus feedback — filter, opacity, color, border-color, box-shadow, transform |
| `--duration-medium` | 300ms | Modal backdrop dim-in |
| `--duration-slow` | 600ms | One-shot entrances — Card fade-up/deal-in, Navbar fade-up, Modal panel-in |
| `--duration-loop-emphasis` | 2.6s | Button idle pulse-glow + Card best-match glow (same effect, now one token instead of two hardcoded literals) |
| `--duration-loop-spin` | 0.7s | Button loading-spinner rotation |
| `--duration-shine` | 1s | Card one-shot diagonal shine sweep |

**Why 3 tiers plus 3 bespoke tokens, not 6 in one scale:** Fast/Medium/Slow
was requested as the transition-duration standard, and every discrete
UI-transition/one-shot-entrance in the library maps cleanly onto it. The
remaining three are open-ended *looping* or freeform decorative
animations (a "breathing" idle glow, a spinner, a light sweep) — forcing a
2.6s ambient pulse onto a 600ms "Slow" tier would either destroy the effect
or, worse, interact badly with the reduced-motion override below (an
infinite-loop animation whose duration collapses toward 0ms doesn't stop,
it flickers). Keeping them separate also let two near-identical hardcoded
values (Button's pulse-glow and Card's best-glow, both 2.6s) collapse onto
one shared token.

## Full before → after mapping

| File | Element | Before | After |
|---|---|---|---|
| Button.css | `.fc-btn` filter/opacity/border-color transition | 150ms | 150ms (unchanged) |
| Button.css | `.fc-btn` box-shadow transition | 200ms | **150ms** |
| Button.css | pulse-glow (idle CTA glow) | 2.6s (hardcoded) | 2.6s (now tokenized) |
| Button.css | spinner rotation | 0.7s (hardcoded) | 0.7s (now tokenized) |
| Card.css | `.fc-card--auth` fade-up | 500ms | **600ms** |
| Card.css | `.fc-card--recommendation` hover transform/shadow | 200ms | **150ms** |
| Card.css | `.fc-card--recommendation` deal-in (×2) | 650ms | **600ms** |
| Card.css | shine sweep | 1s (hardcoded) | 1s (now tokenized) |
| Card.css | best-match glow | 2.6s (hardcoded) | 2.6s (now tokenized, shares Button's token) |
| Navbar.css | `.fc-navbar--back-link` fade-up | 500ms | **600ms** |
| Navbar.css | link/back-link color/opacity transitions | 150ms | 150ms (unchanged) |
| Modal.css | backdrop dim-in | 350ms | **300ms** |
| Modal.css | panel in | 500ms | **600ms** |
| Modal.css | close-button color transition | 150ms | 150ms (unchanged) |
| Input.css | border-color transition | 200ms | **150ms** |

Net effect: every hover/focus micro-transition converges on one speed
(150ms, was split 150/200ms); every notable one-shot entrance converges on
one speed (600ms, was split 500/650ms); the modal backdrop is the one
"in-between" case and got its own tier (300ms, was 350ms). All shifts are
modest (±20% at most) and in the direction of *more* consistency, not
arbitrary.

## Reduced-motion coverage

`styles/tokens.css` collapses `--duration-fast`/`-medium`/`-slow` to
`0.01ms` under `@media (prefers-reduced-motion: reduce)` — every transition
and one-shot entrance in the table above gets this for free, no
per-component change needed, since they all reference those 3 tokens.

The 3 bespoke loop/shine tokens are **not** sped up (an infinite-loop
animation collapsed to ~0ms duration flickers instead of stopping) —
instead, each gets an explicit `animation: none` override:

| Component | What's disabled under reduced motion |
|---|---|
| `Button.css` | idle pulse-glow, loading spinner rotation |
| `Card.css` | fade-up/deal-in entrance (card appears instantly at full opacity), shine sweep, best-match glow |
| `Navbar.css` | back-link-variant fade-up entrance |
| `Modal.css` | backdrop fade + panel entrance (modal appears instantly) |
| `Button.jsx` | the JS-driven magnetic pointer-follow effect, gated with `window.matchMedia('(prefers-reduced-motion: reduce)')` since it's driven by a `mousemove` handler, not CSS |

`Footer.css`, `Badge.css`, and `Input.css`'s only motion is simple
transitions on the 3 core tokens, so they needed no explicit override — the
global `:root` collapse in `tokens.css` already covers them.

## Not covered by this pass

The live site (`templates/*.html`, `static/theme.css`) has its own,
larger set of animations — `fadeUp` (copy-pasted into all 7 templates),
`driftA/B/C` (aurora), `twinkle` (sparkles), `shimmerText`, `floatCard`/
`floatCardBack`, `grainShift`, `rowIn`, `cardShine`, `bestGlow`,
`pulseGlow`, `spin` — none of which reference `styles/tokens.css` (it isn't
linked into any template) and none of which have `prefers-reduced-motion`
handling today. That's the same live-site/components-library split every
token pass this session has drawn, for the same reason: the live app has
no build step to verify changes against safely in this environment.
