# FITCARD DESIGN SPEC

Single source of truth for FitCard's visual language. Tokens below are the actual
values declared in `static/theme.css` and used across `templates/*.html` — update
this file whenever a token changes, and update the code to match if they drift.

## Colors

| Token | Value | Usage |
|---|---|---|
| Primary (Gold) | `--gold: #E5C07B` | CTAs, highlights, "best match" glow, active states |
| Secondary (Surface 2) | `--surface-2: #1F2530` | Secondary buttons, input backgrounds |
| Background (Ink) | `--ink: #0E1116` | Page background |
| Background (Surface) | `--surface: #171B22` | Panels, cards, elevated surfaces |
| Border (Line) | `--line: #2A313D` | Hairlines, dividers, input borders |
| Text (Primary) | `--text: #F2F4F8` | Body copy, headings |
| Text (Muted) | `--muted: #9AA4B2` | Captions, labels, secondary copy |
| Success (Mint) | `--mint: #34D399` | Success states, positive indicators |
| Error (Rose) | `--rose: #F87171` | Error banners, validation messages |

Radius token: `--r: 16px` (cards, mock card faces).

## Typography

| Role | Font | Notes |
|---|---|---|
| Headings / Display | `'Fraunces', Georgia, serif` (`--serif`) | Italic 500/600 weight for h1/h2, big numerals, brand wordmark |
| Body | `'Inter', system-ui, sans-serif` | Default page font, 400/500/600 weights |
| Labels / Data / Buttons | `'Space Grotesk', sans-serif` | Eyebrows, stats, form labels, button text, letter-spaced uppercase tags |
| Caption | `'Inter'` @ 12–14px, `var(--muted)` color | Footnotes, disclaimers, helper text |

Loaded via Google Fonts: `Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500;1,9..144,600`, `Space+Grotesk:wght@500;600;700`, `Inter:wght@400;500;600`.

## Buttons

| Variant | Style |
|---|---|
| Primary | `linear-gradient(180deg,#f0d090,#d8ab55)` fill, `#211a09` text, `border-radius:10px`, `padding:14px 26px`, Space Grotesk 600. Hover: `filter: brightness(1.06)`. Idle: `pulseGlow` gold ring animation. Active: `scale(.98)`. |
| Secondary | `var(--surface-2)` fill, `1px solid var(--line)` border, `var(--text)` text. Hover: border turns `var(--gold)`. |
| Danger / Error | Not filled — surfaced as `.error` / `.state.error` banners: `rgba(248,113,113,.1)` background, `1px solid rgba(248,113,113,.4)` border, `var(--rose)` text. |

## Cards

| Card | Description |
|---|---|
| Recommendation Card (`.cc`) | Result card in the match flow — gradient-filled, `var(--r)` radius, deals in with a 3D `dealIn` rotate/scale animation, gets a diagonal shine sweep. Tier-based gradients (`.t-entry`, `.t-free`, `.t-mid`, …). |
| Best-Match Card (`.cc.best`) | Same as Recommendation Card plus a looping `bestGlow` gold box-shadow pulse to mark the top pick. |
| Mock Card (`.mock-card`) | Decorative floating card on the welcome hero — purple gradient, chip, masked number, brand mark, gentle `floatCard` rotate/translate loop with a light-shine sweep. |
| Listing Row (`.row`, cards.html) | Flat list-style card for "browse all cards" — index numeral, name, stat values; on hover, indents `12px` and its border warms to gold. |

## Layout

| Element | Spec |
|---|---|
| Navbar | Simple flex row inside `.wrap`; brand mark (italic serif + chip) on the left, nav links + auth links on the right. Bordered underneath by a `.hairline` gradient rule, not a solid line. |
| Footer | Centered, `max-width:1160px`, `#4A5261` text at `12px`, `1px solid var(--line)` top border. |
| Container | `.wrap { max-width:1160px; margin:0 auto; padding:40px 32px 0 }` |
| Spacing | Section rhythm in large jumps (`margin-top:120px` between hero and stats on desktop, collapsing to `60px` under 1024px). Component padding generally `14px–26px`. |
| Breakpoints | `640px` (mobile), `1024px` (tablet/desktop split) — standardized repo-wide per the theme-token unification pass. |

## Animations

| Name | Where | Behavior |
|---|---|---|
| Button Hover | `.btn-primary:hover`, `.btn-secondary:hover` | Primary brightens (`filter:brightness(1.06)`); secondary's border shifts to gold. Both scale to `.98` on `:active`. |
| Card Hover | `.cc:hover` | Box-shadow deepens from `0 10px 30px` to `0 20px 46px` for lift. |
| Card Reveal | `.cc` (`dealIn`) | 3D deal-in: rotateX/rotateY + translateY + scale, staggered per card via `--i` index, followed by a one-shot diagonal `cardShine` sweep. |
| Loading | `button.submit-btn.loading .spinner` | `15px` circular spinner, `spin .7s linear infinite`, shown only while `.loading` class is active; label opacity drops to `.85`. |
| Idle Glow | `.btn-primary`, `.cc.best` | Looping soft box-shadow pulse (`pulseGlow` / `bestGlow`) in gold to draw attention without being a hover state. |
| Scroll Reveal | `.reveal` | Fades + translates up `28px` on enter, staggered via `.r-1`…`.r-5` delay classes. |
