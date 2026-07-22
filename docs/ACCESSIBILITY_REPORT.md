# FitCard Accessibility Audit

Read-only audit — no code was changed. Covers all 7 live pages
(`templates/*.html` + `static/theme.css` + `static/theme.js`) and the
standalone `components/` React library. Checked against WCAG 2.1 AA unless
noted. Contrast ratios below are computed directly from the hex/rgba values
in `styles/tokens.css` using the standard WCAG relative-luminance formula,
not eyeballed.

## Severity summary

| # | Finding | Category | Severity | Where |
|---|---|---|---|---|
| 1 | Radio/checkbox groups unreachable by keyboard | Keyboard nav | **Critical** | `templates/match.html` |
| 2 | Focus ring removed on all inputs, sitewide | Focus indicators | High | 6 templates + `components/Input.css` |
| 3 | 6 form controls with a visible label that isn't programmatically associated | Form labels | High | `templates/match.html` |
| 4 | Live-updating result regions have no `aria-live` | ARIA | High | `templates/match.html`, `templates/cards.html` |
| 5 | Zero ARIA attributes anywhere in the live site | ARIA | Medium | all 7 templates |
| 6 | Google icon SVG not hidden from assistive tech | ARIA / images | Low | `templates/login.html`, `templates/signup.html` |
| 7 | Two low-contrast text colors | Color contrast | Medium | `static/theme.css`-driven styles, several templates |
| 8 | No skip-to-content link | Keyboard nav | Low | all 7 templates |
| 9 | Toggle pills have no focus-visible style even if focusability is fixed | Focus indicators | Medium | `templates/match.html` |
| 10 | Loading state not announced to screen readers | ARIA | Low | `templates/match.html`, `components/Button.jsx` |

---

## 1. Color contrast

Computed against the actual token values (`styles/tokens.css`):

| Pair | Ratio | AA normal text (4.5:1) | AA large text/UI (3:1) |
|---|---|---|---|
| `--text` on `--ink` (body copy) | 17.17:1 | PASS | PASS |
| `--text` on `--surface` (auth card) | 15.68:1 | PASS | PASS |
| `--muted` on `--ink` / `--surface` / `--surface-2` | 7.50 / 6.85 / 6.10 :1 | PASS | PASS |
| `--gold` on `--ink` (eyebrows, footer links) | 10.95:1 | PASS | PASS |
| `--mint` on `--ink` (back-link/browse-link) | 9.84:1 | PASS | PASS |
| `--rose` on `--ink` / error-banner bg | 6.84 / 6.26 :1 | PASS | PASS |
| `--color-on-primary` on gold-button gradient (both stops) | 11.62 / 8.12 :1 | PASS | PASS |
| gold focus border vs `--surface-2` / `--surface` | 8.90 / 10.00 :1 | PASS | PASS |
| **`--color-text-placeholder` (`#5B6472`) on `--surface-2`** | **2.57:1** | **FAIL** | FAIL |
| **footer text (`#4A5261`) on `--ink`** | **2.41:1** | **FAIL** | FAIL |
| `.row-suited` text (`#6B7383`) on `--ink` | 3.97:1 | FAIL | PASS |

**Finding #7 (Medium):** placeholder text and footer disclaimer text fall well
below AA even for large text. Placeholder text is technically exempt from
WCAG's SC 1.4.3 in most interpretations (it's not "text" until typed), but
it's still the only hint some of these fields give before focus, and at
2.57:1 it's hard to read for a meaningful fraction of users. Footer text at
2.41:1 has no such exemption — it's static body copy on every page that uses
it (welcome.html, match.html via `Footer`) and fails outright.
`.row-suited` (cards.html list) clears the large-text/UI threshold but not
normal-text.

**Recommendation:** lighten `--color-text-placeholder` and
`--color-text-faint` a few steps, or accept them only for genuinely
decorative/non-essential text and route anything a user needs to read
through `--color-text-muted` (7.5:1+) instead.

**Tier-gradient text** (white text on the 6 recommendation-card gradients,
`constants/tiers.js`): computed against both gradient stops per tier —
`mid`/`super`/`luxury`/`na` all clear 5.7:1+ even at their darkest stop.
`entry` and `free` dip to **3.74:1** and **3.31:1** at their lighter stop —
below AA for the small body text used inside the card (`.cc-bank`,
`.meta-label`) though the card's larger `.cc-name` heading text would
qualify under the large-text threshold. Worth a closer look specifically for
those two tiers.

---

## 2. Keyboard navigation

**Finding #1 (Critical):** `templates/match.html` hides its radio/checkbox
inputs with `display:none` to build custom-styled pill toggles:

```css
.chip-toggle input{display:none}
.radio-toggle input{display:none}
```

`display:none` removes an element from both the tab order *and* the
accessibility tree — not just visually. The `<label>` wrapping each input is
not itself focusable. Result: **Lounge access, Lifestyle benefits, and
Milestone appetite — three full input groups in the core matching form —
cannot be reached or operated by keyboard at all.** A mouse-only pattern
that happens to also fail screen readers, since a `display:none` input is
invisible to both. This is the single highest-impact finding in this audit:
it blocks a core task (finding a card) for keyboard-only and most
screen-reader users.

The standard fix for this exact "custom-styled native input" pattern is a
visually-hidden-but-focusable technique (`position:absolute; opacity:0;
width:1px; height:1px; overflow:hidden` — or the common `.sr-only`-adjacent
"clip" pattern) instead of `display:none`, so the input stays in the tab
order and the accessibility tree while the custom label visual stays what's
shown.

**Finding #8 (Low):** none of the 7 pages have a skip-to-content link.
Lower impact here than usual since none of the pages have a large repeated
nav block before the main content (only welcome.html has a real `<nav>`),
but worth adding if `Navbar`'s `full` variant (components library, §COMPONENT_AUDIT
recommendation) ever gets applied to more pages.

Everything else checked out: all interactive elements are real
`<button>`/`<a href>`/`<input>`/`<select>` elements (no `<div onClick>`
patterns found), so standard Tab/Enter/Space semantics work everywhere
except the toggle pills above. No positive `tabindex` values or tab traps
found anywhere in either the live templates or `components/`.

---

## 3. Focus indicators

**Finding #2 (High):** every text input across the entire project —
`login.html`, `login_phone.html`, `signup.html`, `verify_otp.html`,
`cards.html`, `match.html`, and `components/Input.css` — does this on
focus:

```css
input:focus{outline:none; border-color:var(--gold)}
```

The native focus ring is removed and replaced with only a 1px border-color
change. The color itself has good contrast (8.9–10:1, see §1), but a 1px
border swap is a much weaker signal than a ring — easy to miss for anyone
scanning quickly, and thin borders are a known trouble spot for
low-vision users. `components/Button.css` does **not** do this (no
`outline` rule at all), so buttons and links keep their native focus ring —
inputs are the one component type where the indicator was intentionally
swapped, everywhere it's used.

**Finding #9 (Medium):** even setting §Finding #1 aside, the `.chip-toggle`
and `.radio-toggle` pills have no `:focus` or `:focus-within` style defined
at all. So fixing the `display:none` keyboard-trap doesn't automatically
restore a visible focus indicator for these controls — that needs its own
CSS once the inputs are focusable again.

---

## 4. ARIA labels

**Finding #5 (Medium):** grepped for `aria-` and `role=` across all 7
templates — **zero matches**. Every ARIA attribute in the project exists
only in the new `components/` library (`Modal.jsx`'s `role="dialog"`,
`aria-modal`, `aria-labelledby`, `aria-label`; `Button.jsx`'s
`aria-hidden` on the Google icon). None of that has shipped to the live
site yet.

**Finding #4 (High):** `match.html`'s `#results`, `#resultsHead`,
`#resultsSub`, `#widenedNote`, and `cards.html`'s `#count` are all populated
by JS after the page loads (`innerHTML =` in a `fetch().then()`/render
call) with no `aria-live` region anywhere near them. A screen-reader user
who submits the match form gets no announcement that results arrived, how
many, or that a filter was widened — they'd have to manually re-navigate to
that part of the page and hope something changed. Same for the live card
count in `cards.html` as someone types into the search box.

**Finding #10 (Low):** the loading spinner (`match.html`'s
`button.submit-btn.loading`, and `components/Button.jsx`'s `loading` prop)
has no `aria-busy` on the button and no visually-hidden "Loading…" text —
a screen-reader user gets no feedback that their submission is in flight,
only silence until the results region updates (which itself isn't
announced — see Finding #4).

**Finding #6 (Low):** the Google "G" logo SVG is inlined directly (not an
`<img>`) in `login.html`/`signup.html` with no `aria-hidden="true"`.
It sits next to visible "Continue with Google" text, so it's redundant to
assistive tech at best and, in some screen readers, an unlabeled graphic
may still get announced as "image" with no useful name. `components/Button.jsx`
already fixed this in its own copy of the icon (`aria-hidden="true"`,
newly commented as intentional) — the live template's copy predates that.

---

## 5. Image alt text

**No `<img>` elements exist anywhere in the project** — every visual
(card mockups, chip artwork, tier badges) is built from CSS gradients or
inline SVG, not raster images, so there's no `alt` text to audit in the
traditional sense. The one graphic content — the Google "G" logo SVG — is
covered under Finding #6 above (ARIA, not `alt`, since it's inline SVG).

---

## 6. Form labels

Checked every `<label>`/`<input>`/`<select>` pairing across
`login.html`, `login_phone.html`, `signup.html`, `verify_otp.html`,
`cards.html`, and `match.html`.

**Correctly paired** (label `for` matches input/select `id`, or the label
wraps the control): email/password/name/phone/OTP fields on all 4 auth
pages, the search/sort controls in `cards.html`, all 11 per-category spend
inputs in `match.html`'s question 01, and (via wrap-association rather than
`for`) every individual chip-toggle/radio-toggle option.

**Finding #3 (High):** 6 of `match.html`'s 7 form sections use a plain
`<label class="title">` as a visual section heading, sitting as a *sibling*
of the control it describes rather than wrapping it or using `for`/`id`:

```html
<div class="field-row-head">
  <label class="title">Joining fee budget</label>
  <span class="desc">The most you're willing to pay up front.</span>
</div>
<select id="fee_budget">…</select>
```

Because there's no `for="fee_budget"`, this `<label>` has no programmatic
relationship to the `<select>` at all — a screen reader announces the
control with no name ("combo box, blank") rather than "Joining fee budget,
combo box." Affects: **Joining fee budget** (`select#fee_budget`),
**Primary goal** (`select#primary_goal`), **Lounge access** (radio group),
**Lifestyle benefits** (checkbox group), **Bank preference**
(`select#bank_preference`), and **Milestone appetite** (radio group).
Question 01 ("Monthly spend by category") is *not* included in this finding
— it's a genuine section heading over 11 individually-and-correctly-labeled
sub-fields, not a mislabeled single control.

The two `<select>` cases have a simple fix (`for="fee_budget"` etc., since
these labels aren't already wrapping anything). The three group cases
(lounge_need, lifestyle_benefits, milestone_appetite) are better fixed with
`<fieldset>`/`<legend>` — a `<label>` can only ever name one control, but
these are groups of several radio/checkbox inputs, which `<fieldset>` was
built for. Neither the live template nor the `components/` library
currently has a fieldset/radio-group primitive (`components/README.md`
already flags `ToggleChip` as a recommended-but-not-built component) — if
that gets built, this is the reason it needs group-labeling support, not
just visual styling.

`components/Input.jsx` itself pairs `label`/`htmlFor`/`id` correctly and has
no equivalent bug — this finding is specific to the live `match.html`
markup, which predates the component library and hasn't been migrated to
it.

---

## What's already solid

Worth naming, not just gaps: every page has `<html lang="en">`; every input
in the audited flows (aside from Finding #3's six) has a correctly
associated label; there are no positive `tabindex` values or keyboard traps
anywhere; all interactive elements are semantic HTML rather than
click-handler `<div>`s; body text, muted text, gold, mint, and rose all
clear AA contrast comfortably; and the `components/Modal.jsx` primitive
already implements `role="dialog"`, `aria-modal`, `aria-labelledby`, and
Escape-to-close correctly for whenever a modal ships.
