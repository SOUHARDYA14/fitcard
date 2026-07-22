# FitCard UI Audit

Read-only inventory of every color, size, and effect currently in the frontend
(`static/theme.css`, `static/theme.js`, and all 7 files in `templates/`).
Nothing was changed — this is a snapshot for cleanup/consolidation planning.

Legend: **token** = defined in `static/theme.css :root`. **hardcoded** = literal
value repeated inline in one or more templates instead of using a token.

---

## 1. Colors

### 1.1 Design tokens (`static/theme.css`)

| Token | Value | Used as |
|---|---|---|
| `--ink` | `#0E1116` | page background |
| `--surface` | `#171B22` | auth-card background |
| `--surface-2` | `#1F2530` | inputs, secondary buttons, chip/radio toggles |
| `--line` | `#2A313D` | borders, hairlines, dividers |
| `--text` | `#F2F4F8` | primary text |
| `--muted` | `#9AA4B2` | secondary text, labels, captions |
| `--gold` | `#E5C07B` | primary accent — CTAs, focus rings, highlights |
| `--mint` | `#34D399` | success accent, "back to matcher" links |
| `--rose` | `#F87171` | error accent |

Usage counts across templates: `--muted` 36×, `--gold` 33×, `--text` 30×,
`--line` 30×, `--surface-2` 10×, `--ink` 7×, `--rose` 5×, `--mint` 5×,
`--surface` 4×. Two utility classes in `theme.css` fall back to hardcoded hex
if the var is missing: `var(--gold,#E5C07B)` and `var(--muted,#9AA4B2)` /
`var(--line,#2A313D)` — these are defensive fallbacks, not distinct colors.

### 1.2 Hardcoded colors (not tokenized)

**Gold button gradient** — repeated literally in 6 files (welcome, login,
login_phone, signup, verify_otp, match) instead of deriving from `--gold`:
- `#f0d090` (gradient top), `#d8ab55` (gradient bottom), `#211a09` (button text)

**Body background radial-gradient blobs** — repeated in 6 files (cards, login,
login_phone, signup, verify_otp, match):
- `#1a2130`, `#201a2b`

**Aurora / mock-card / recommendation-card gradients** — indigo→violet pair
repeated in 6 files (login, login_phone, signup, verify_otp, welcome, match):
- `#3730a3`, `#7c3aed`

**Card-chip gradient** (brand mark chip, mock card chip, `.cc` chip) — repeated
in 6 files:
- `#f6e2a8`, `#c9a24a`

**Recommendation-card tier gradients** (`match.html` only, `.cc.t-*`):
| Tier | Gradient |
|---|---|
| Entry | `#0f766e` → `#0d9488` |
| Free | `#155e63` → `#1f9e8f` |
| Mid | `#3730a3` → `#4f46e5` |
| Super | `#5b21b6` → `#7c3aed` |
| Luxury | `#1c1c22` → `#3a3320` (also used for `welcome.html` mock-card back) |
| N/A | `#334155` → `#475569` |

**Tier-dot colors** (`cards.html` list view — a *second*, independent color
mapping for the same tiers, not shared with the `.cc.t-*` gradients above):
- Free `#34D399` (= `--mint`, written literally instead of the var)
- Entry `#2dd4bf`
- Mid `#818cf8`
- Super `#c084fc`
- Luxury → `var(--gold)` (correctly tokenized)
- N/A `#94a3b8`

**Misc one-offs:**
- `#6B7383` — `.row-suited` text (cards.html)
- `#4A5261` — footer text (welcome.html, match.html)
- `#5B6472` — input placeholder text (match.html)
- `#fff`, `#fff6df` — mock-brand text, shimmer gradient highlight (welcome.html)
- Google "G" logo brand colors (login.html, signup.html, decorative SVG,
  not part of the design system): `#FFC107`, `#FF3D00`, `#4CAF50`, `#1976D2`

### 1.3 rgba() overlays

Grouped by base hue — 32 distinct rgba() values total, all ad hoc (no alpha
scale/tokens exist):

| Base | Alphas in use |
|---|---|
| Black `rgba(0,0,0,…)` | `.15 .25 .28 .35 .4 .5` — shadows, chip inset, card overlays |
| White `rgba(255,255,255,…)` | `.09 .12 .14 .18 .28 .4 .55 .6 .65 .7 .85 .9` — card borders, meta text, shine sweep |
| Gold `rgba(229,192,123,…)` | `0 .1 .14 .3 .35 .4 .5 .8` — focus glow, pulse rings, widened-note bg, chip-toggle checked bg |
| Rose `rgba(248,113,113,…)` | `.1 .4` — error banner bg/border |
| Mint `rgba(52,211,153,…)` | `.1 .12 .4` — dev-otp banner, radio-toggle checked bg |
| Ink `rgba(33,26,9,…)` | `.35` — spinner ring on gold buttons |

---

## 2. Font sizes

| Size | Occurrences | Typical use |
|---|---|---|
| `13px` | 22 | captions, hints, footers, meta labels |
| `15px` | 15 | inputs, buttons, body-ish text |
| `14px` | 13 | secondary body, stat values |
| `12px` | 12 | uppercase labels |
| `11px` | 9 | eyebrows, tiny uppercase labels |
| `20px` | 5 | auth-card brand mark, h1 (verify_otp/login/signup context) |
| `28px` | 4 | auth-card `h1` |
| `22px` | 4 | OTP input digits, results-head, big-numeral-ish |
| `19px` | 3 | brand mark (cards.html/match.html), field-row numeral |
| `17px` | 3 | row-name, welcome `.sub` |
| `16px` | 2 | match `.sub`, mock-number |
| `9px` | 1 | `.cc-score-label` |
| `10px` | 1 | `.stat-label` (cards.html) |
| **Fluid (`clamp`)** | 4 | `clamp(28px,5vw,42px)` (cards h1), `clamp(30px,5.6vw,46px)` (match h1), `clamp(38px,4.6vw,56px)` (welcome stat-num), `clamp(40px,6.4vw,72px)` (welcome hero h1) |

No explicit type scale/tokens — every size above is a literal px value declared
per-selector.

---

## 3. Spacing (padding / margin / gap)

No spacing tokens exist; all values below are literal and drawn from a loose
~2px-step scale rather than a formal system.

**Most common padding:** `padding:0` (reset, 7×), `10px 12px` (5×),
`40px 20px` (auth-page body, 4×), `38px 34px` (auth-card, 4×),
`13px 20px` (auth button, 4×), `11px 12px` (auth input, 4×).
Full range seen: `0, 4px 9px, 4px 10px, 6px 2px, 7px 13px, 8px 14px, 9px 10px,
10px 14px, 10px 16px, 11px 12px, 11px 20px, 13px 20px, 14px 26px, 14px 28px,
18px 4px, 22px, 22px 0, 22px 24px, 26px 0 4px, 28px 32px 48px, 36px 20px,
38px 34px, 40px 0, 40px 20px, 40px 20px 80px, 40px 32px 0, 44px 0 40px,
48px 20px 80px`.

**Most common margin:** `margin-bottom:18px` (13×), `margin-bottom:26px` (9×),
`margin:0` (7×), `margin:0 auto` (5×), `margin-top:6px` (5×),
`margin-bottom:6px` (5×), `margin-top:24px` (4×), `margin-left:54px` (3×
— indents form/list content past the vertical "spine" rule).
Layout-scale outliers: `margin-top:120px` (welcome stats section, desktop),
collapsing to `margin-top:60px` under the 1024px breakpoint;
`margin:40px 0 0 54px` (match form-wrap).

**Gap:** `8px` (10×), `6px` (9×), `14px` (6×), `10px` (5×), `12px` (4×),
`24px`/`22px`/`16px` (3× each), then one-offs at `1px, 2px, 3px, 4px, 9px,
18px, 28px, 36px`.

**Container widths:** `.wrap` max-width differs per page — `960px` (cards),
`1160px` (welcome), `820px` (match) — with no shared container token.

**Breakpoints:** `640px` and `1024px`, applied consistently across all pages
(standardized in the most recent commit). Re-audited 2026-07-22 across all 7
templates: only these two width values are used anywhere (3 occurrences
total — `cards.html`, `match.html` at 640px; `welcome.html` at 1024px), no
drift. `login.html`/`login_phone.html`/`signup.html`/`verify_otp.html` have
no media queries at all (fixed-width auth cards). Formalized as a named
Mobile/Tablet/Desktop standard in `styles/tokens.css`
(`--breakpoint-sm`/`--breakpoint-md`):

| Tier | Range |
|---|---|
| Mobile | `< 640px` |
| Tablet | `640px – 1023px` |
| Desktop | `>= 1024px` |

Also found, separately: `@media (pointer:coarse), (hover:none)` — a
device-*capability* query (not a width breakpoint), byte-identical in
`static/theme.css` and 3 templates (used to disable the custom cursor on
touch devices). Not part of the Mobile/Tablet/Desktop standard since it's
orthogonal to viewport width, but flagged here as its own small duplication.

---

## 4. Border radius

| Value | Occurrences | Where |
|---|---|---|
| `8px` | 11 | inputs (auth forms, match form) |
| `50%` | 9 | circular elements — dots, spinner, aurora blobs, avatar-style chips |
| `10px` | 9 | buttons (primary/secondary/submit), btn-google |
| `4px` | 7 | brand chip mark |
| `var(--r)` (`16px`) | 6 | auth-card, `.cc` recommendation card, `.state` empty/error box |
| `20px` | 3 | pill shapes — chip-toggle, rank badge, cat-pill |
| `6px` | 2 | mock-chip, `.cc` chip |
| `18px` | 1 | `.mock-card` (welcome hero) |
| `12px` | 1 | `.cc-score` badge |
| `0` | 1 | `.controls input/select` (cards.html — underline-style field, deliberately square) |

`--r: 16px` is the only radius token; the rest (`8px`, `10px`, `20px`, etc.)
are untokenized literals reused by convention rather than reference.

---

## 5. Shadows

| Shadow | Where |
|---|---|
| `0 30px 70px rgba(0,0,0,.4)` | auth `.card` (login/login_phone/signup/verify_otp) |
| `0 30px 70px rgba(0,0,0,.5)` | `.mock-card` (welcome hero) |
| `0 20px 46px rgba(0,0,0,.5)` | `.cc:hover` (recommendation card hover) |
| `0 10px 30px rgba(0,0,0,.35)` | `.cc` base shadow |
| `0 10px 30px rgba(0,0,0,.35), 0 0 0 0 rgba(229,192,123,.35)` | `.cc.best` glow, `bestGlow` keyframe start/end |
| `0 10px 30px rgba(0,0,0,.35), 0 0 0 8px rgba(229,192,123,0)` | `.cc.best` glow, `bestGlow` keyframe mid |
| `0 0 0 0 rgba(229,192,123,.5)` | `.btn-primary` base (pre-pulse) |
| `0 0 0 0 rgba(229,192,123,.35)` / `0 0 0 10px rgba(229,192,123,0)` | `pulseGlow` keyframe (welcome CTA) |
| `0 0 6px 1px rgba(229,192,123,.8)` | sparkle particles (welcome hero) |
| `inset 0 0 0 1px rgba(0,0,0,.15)` | chip embossing (brand chip, mock-chip, `.cc` chip) |

Two independent "glow pulse" shadow animations exist (`pulseGlow` on the
welcome CTA, `bestGlow` on the best-match result card) with near-identical
gold rgba values but different radii/timing — candidates to unify.

---

## 6. Button styles

| Variant | Where | Style |
|---|---|---|
| **Primary (gold)** | `.btn.btn-primary` (welcome), `.submit-btn`/`button.submit-btn` (match), bare `button` (login, login_phone, signup, verify_otp) | `linear-gradient(180deg,#f0d090,#d8ab55)` fill, `#211a09` text, Space Grotesk 600, `border-radius:10px`. Hover: `filter:brightness(1.06)`. Active: `scale(.98)`. Welcome variant additionally idles with `pulseGlow` (infinite gold ring pulse) — the match/auth variants don't. |
| **Secondary** | `.btn.btn-secondary` (welcome only) | `var(--surface-2)` fill, `1px solid var(--line)` border, `var(--text)` text. Hover: border → `var(--gold)`. No other page has a secondary button variant. |
| **Google OAuth** | `.btn-google` (login, signup) | `var(--surface-2)` fill, `1px solid var(--line)` border, Inter 500, `border-radius:10px`. Hover: border → `var(--gold)`. |
| **Text/link button** | `button.link` (verify_otp "Resend code") | `all:unset`, gold text, underline on hover — not a filled button at all. |
| **Loading state** | `button.submit-btn.loading` (match) | Adds a 15px spinning ring (`spin .7s linear infinite`), label opacity drops to `.85`, button `cursor:progress` + `opacity:.7` while `:disabled`. No equivalent loading state exists on the auth-page buttons even though those also submit forms. |
| **Danger** | *None found* | No button variant carries the `--rose` error color — error states are communicated via banners only (see §8), never a button style. |

All primary/submit buttons redeclare the same gold gradient + `#211a09` text
independently rather than sharing a class across templates.

---

## 7. Card styles

| Card | Where | Style |
|---|---|---|
| **Auth card** | `.card` (login, login_phone, signup, verify_otp) | `var(--surface)` fill, `1px solid var(--line)`, `border-radius:var(--r)`, `padding:38px 34px`, `box-shadow:0 30px 70px rgba(0,0,0,.4)`, entrance `fadeUp .5s`. |
| **Recommendation card** | `.cc` (match.html) | `border-radius:var(--r)`, `padding:22px 24px`, `1px solid rgba(255,255,255,.09)`, tier-based gradient background (see §1.2), `box-shadow:0 10px 30px rgba(0,0,0,.35)`. Entrance: 3D `dealIn` (rotateX/rotateY/translateY/scale) staggered by `--i`, plus a one-shot diagonal `cardShine` sweep. Hover: shadow deepens + JS-driven pointer-tilt (`rotateY`/`rotateX` from mousemove) and lift/scale. |
| **Best-match card** | `.cc.best` (match.html) | Same as Recommendation card + looping `bestGlow` box-shadow pulse and a `"Best match"` badge instead of a rank number. |
| **Mock/decorative card** | `.mock-card` (welcome.html) | `border-radius:18px`, `padding:22px`, purple gradient, `box-shadow:0 30px 70px rgba(0,0,0,.5)`, `1px solid rgba(255,255,255,.12)`. Loops `floatCard` (gentle rotate/translateY) plus a `shine` sweep. A second `.mock-card.back` sits behind it at reduced size/opacity with its own `floatCardBack` loop. |
| **List row ("row-card")** | `.row` (cards.html) | Not boxed — a flat, bottom-bordered row (`border-bottom:1px solid var(--line)`) rather than a discrete card. Hover: indents `padding-left:12px` and border warms to `rgba(229,192,123,.4)`. Entrance: staggered `rowIn` fade+translateY. |
| **Empty/error state card** | `.state` / `.state.error` (match.html) | `1px dashed var(--line)`, `border-radius:var(--r)`, `padding:36px 20px`, centered text. `.error` modifier swaps border/text to rose. |

Three different corner radii are used across "card-like" containers depending
on page (`var(--r)`=16px for auth/recommendation/state; `18px` hardcoded for
the welcome mock-card) — the mock-card is the one card that doesn't use the
`--r` token.

---

## 8. Input styles

| Variant | Where | Style |
|---|---|---|
| **Standard text/email/password/tel input** | `input` (login, login_phone, signup, verify_otp) | `var(--surface-2)` fill, `1px solid var(--line)`, `border-radius:8px`, `padding:11px 12px`, `font-size:15px`, Inter. Focus: border → `var(--gold)`, no visible outline (`outline:none`). |
| **OTP input** | `input#otp` (verify_otp.html) | Same base as standard input but `font-size:22px`, `letter-spacing:.3em`, `text-align:center`, Space Grotesk — a distinct visual variant for 6-digit codes. |
| **Underline input/select** | `.controls input/select` (cards.html) | No fill, no border — just `border-bottom:1px solid var(--line)`, `border-radius:0`, transparent background, Space Grotesk. Focus: bottom border → `var(--gold)`. Different pattern from every other input on the site. |
| **Match-form input/select** | `.field-row input/select` (match.html) | Closer to the standard input (`var(--surface-2)`, `1px solid var(--line)`, `border-radius:8px`) but tighter padding (`9px 10px`) and a custom CSS-only select arrow (two rotated gradients, no native chrome). Placeholder text uses `#5B6472` (hardcoded, not `--muted`). |
| **Chip toggle (checkbox-as-pill)** | `.chip-toggle` (match.html, lifestyle benefits) | Pill-shaped (`border-radius:20px`), `var(--surface-2)`/`var(--line)` idle; checked state via `:has(input:checked)` → `rgba(229,192,123,.14)` bg, `var(--gold)` border, `var(--text)` label. |
| **Radio toggle (radio-as-pill)** | `.radio-toggle` (match.html, lounge/milestone questions) | Same pattern as chip-toggle but `border-radius:10px` (not fully pill) and checked state uses mint (`rgba(52,211,153,.12)` bg, `var(--mint)` border) instead of gold — the one place mint is used as a "selected" affordance rather than "success." |

Four distinct input skins exist (filled/bordered, underline, OTP-spaced, and
pill-toggle) with no shared base class — each template redeclares its own
`input{...}` block.

---

## 9. Animations

### Keyframes defined

| Name | Duration / easing | Purpose | Where |
|---|---|---|---|
| `fadeUp` | varies, `.35s`–`.7s`, `ease` | Generic entrance: opacity 0→1 + translateY(14–16px)→0 | Declared independently in **every** template (7×, identical or near-identical bodies — `14px` vs `16px` offset is the only variance) |
| `rowIn` | `.4s ease` | List row entrance, staggered | cards.html |
| `dealIn` | `.65s cubic-bezier(.16,1,.3,1)` | 3D card deal-in (rotateX/Y + translateY + scale), staggered via `--i` | match.html |
| `cardShine` | `1s ease` | One-shot diagonal light sweep across a recommendation card | match.html |
| `bestGlow` | `2.6s ease-in-out infinite` | Looping gold shadow pulse on the best-match card | match.html |
| `pulseGlow` | `2.6s ease-in-out infinite` | Looping gold shadow pulse on the welcome primary CTA (near-duplicate of `bestGlow`) | welcome.html |
| `shimmerText` | `4s linear infinite` | Gold gradient sweeping across the hero `<em>` text | welcome.html |
| `floatCard` | `5s ease-in-out infinite` | Gentle rotate + vertical drift on the hero mock card | welcome.html |
| `floatCardBack` | `5s ease-in-out infinite` | Same, offset, for the mock card sitting behind it | welcome.html |
| `shine` | `4.5s ease-in-out infinite` | Looping diagonal sweep on the mock card | welcome.html |
| `twinkle` | duration randomized in JS, `linear infinite` | Sparkle opacity/scale pulse | welcome.html |
| `driftA` / `driftB` / `driftC` | `22–30s ease-in-out infinite alternate` | Slow aurora blob drift; `driftA`/`driftB` redeclared with different durations in both welcome.html and match.html, `driftC` only in welcome.html | welcome.html, match.html |
| `spin` | `.7s linear infinite` | Loading spinner rotation | match.html |
| `grainShift` | `8s steps(8) infinite` | Film-grain overlay texture shift | theme.css (shared) |

### JS-driven interaction animations (`theme.js` + inline scripts)

- **Custom crosshair cursor** — snaps to pointer position via `mousemove`; widens on hover over `a, button, input, select, .magnetic, .cc, .row` (theme.js, all pointer-capable pages).
- **Scroll reveal** — `IntersectionObserver` adds `.in` to `.reveal` elements at 15% visibility, triggering the CSS `reveal` opacity/translateY transition (theme.js + `.reveal` rule in theme.css). Currently only applied to the welcome stats strip.
- **Magnetic buttons** — `.magnetic` elements translate up to `±0.25×/0.35×` the pointer offset from center on `mousemove`, reset on `mouseleave` (theme.js). Applied to welcome CTAs and the match submit button.
- **3D pointer tilt** — welcome hero mock-card group tilts via `rotateY`/`rotateX` driven by global `mousemove` (inline script, welcome.html); match result cards get a per-card version bound to each `.cc`'s own `mousemove`/`mouseleave` (inline script, match.html).
- **Count-up numerals** — cubic-eased `requestAnimationFrame` count from 0 to a target, used for welcome's "by the numbers" stats (fires once, on scroll into view) and match's per-card score numbers (fires on results render, staggered by index).

### Transitions (non-keyframe, hover/focus-driven)

`filter .15s`, `border-color .15s`/`.2s`, `opacity .15s`/`.2s`,
`color .15s`, `all .15s`, `padding-left .2s ease, border-color .2s ease`,
`transform .25s cubic-bezier(.22,1,.36,1)`,
`transform .2s cubic-bezier(.22,1,.36,1), box-shadow .2s ease`,
`width .2s ease, height .2s ease` (cursor hover-grow),
`opacity .7s cubic-bezier(.16,1,.3,1), transform .7s cubic-bezier(.16,1,.3,1)` (`.reveal`).

---

## Notable duplication (for future consolidation)

1. **`fadeUp` keyframe** is copy-pasted into all 7 templates instead of living once in `theme.css`, despite being identical in intent everywhere.
2. **`pulseGlow` and `bestGlow`** are near-duplicate gold pulse animations that could be one shared keyframe with a parameterized radius.
3. **`driftA`/`driftB`** aurora keyframes are redeclared with different durations in welcome.html vs match.html rather than sharing one definition with a per-instance duration override.
4. **Gold button gradient** (`#f0d090`/`#d8ab55`/`#211a09`) is hand-copied into 6 files rather than derived from `--gold`.
5. **Tier colors exist twice**, independently: the `.cc.t-*` gradient set (match.html) and the `.tier-dot.*` dot-color set (cards.html) use different hex values for the same six tiers.
6. **Four separate input skins** (filled, underline, OTP, pill-toggle) with no shared base class.
7. `--mint` is both a "success" semantic (green check marks, success text) and a "this option is selected" semantic (`.radio-toggle:has(input:checked)`) — the two meanings aren't visually distinguished.
