# FitCard Cleanup Report

Read-only review of the entire project — the live Flask app
(`templates/`, `static/`, `*.py`) and the standalone frontend library
(`components/`, `hooks/`, `lib/`, `constants/`, `styles/`). **Nothing was
deleted or modified.** Every finding below was verified programmatically
(AST parsing for Python, cross-file regex/reference checks for CSS/JS),
not guessed — see the specific evidence under each item.

## Summary

| Category | Found | Notes |
|---|---|---|
| Unused CSS | 6 selectors | `static/theme.css` only — every template's own inline CSS and every `components/*.css` file is fully consumed |
| Unused Components | 7 of 7 (by design) | Whole `components/` library has zero render call sites — it's standalone/unwired, not abandoned |
| Unused Images | 0 files | No image assets exist anywhere in the project to be unused |
| Unused Fonts | 2 weights | Requested from Google Fonts, never rendered |
| Unused Packages | 0 direct | Every direct dependency is imported; the rest of `requirements.txt` is normal transitive-dependency noise from a `pip freeze` |
| Unused Imports | 0 | Verified via Python AST across all 10 `.py` files, and cross-reference across the JS library |
| Dead Code | 4 items | 3 unused exports, 2 orphaned utility scripts, 1 local-only backup file |

---

## 1. Unused CSS

**`static/theme.css` — 6 dead selectors, confirmed via cross-reference
against all 7 templates + `theme.js`:**

| Selector | Issue |
|---|---|
| `.big-numeral` | Defined, never referenced anywhere — not in any template, not in `theme.js`, not even elsewhere in `theme.css` |
| `.reveal.r-1` through `.reveal.r-5` (5 rules) | Stagger-delay modifiers for the scroll-reveal effect. `.reveal` itself is applied to exactly **one** element sitewide (`welcome.html`'s `.stats` div, line 261) and it never carries an `.r-N` modifier — these were built for a staggered multi-element reveal that was never wired up |

**Everywhere else, CSS is clean:**
- Every one of the 7 templates' own inline `<style>` blocks was checked against that same template's HTML/JS — zero unused selectors found in any of them.
- Every `components/*.css` file was checked against its paired `.jsx` — zero unused selectors, including the dynamically-built variant classes (`fc-btn--${variant}` etc.), which a naive literal-string grep would false-positive on but which are genuinely used via template-literal construction.

## 2. Unused Components

**All 7 components in `components/` (`Button`, `Input`, `Card`, `Badge`,
`Modal`, `Navbar`, `Footer`) currently have zero render call sites** —
nothing in this project imports from `./components` except the library's
own internal cross-references (`Card`/`Badge` importing tier constants).
This isn't neglect: every prior pass this session confirmed the library is
intentionally standalone and not wired into the live Jinja app yet (see
`components/README.md`, "Why standalone, not wired in"). Listed here
because "unused" was asked for literally, not because it's a problem.

Worth distinguishing one from the rest: **`Modal`** has no legacy pattern
behind it at all (`docs/COMPONENT_AUDIT.md` §8 confirmed no modal/dialog
exists anywhere in the original templates) — it's speculative in a way
the other 6 aren't, since they at least map 1:1 to real duplicated markup
that used to exist.

## 3. Unused Images

**Nothing to report — no image assets exist in the project at all.**
Zero `<img>` tags anywhere (confirmed independently in
`docs/ACCESSIBILITY_REPORT.md` too), zero `.png`/`.jpg`/`.svg`/`.ico`
files anywhere in `static/` or elsewhere, and no `background-image: url(...)`
referencing a local file (every gradient/mockup visual is CSS or inline
SVG). Also no favicon/icon `<link>` in any template — not "unused," but a
gap worth knowing about if it comes up separately.

## 4. Unused Fonts

No self-hosted font files exist (all 3 families load from the Google
Fonts CDN). Checked every requested weight against actual `font-weight`
declarations across all 7 templates + `theme.css`:

| Family | Requested weights | Actually rendered |
|---|---|---|
| Fraunces | 500, 600 (upright + italic, both axes) | Both weights, both styles genuinely used — e.g. `welcome.html`'s hero `h1` uses upright 500, its nested `<em>` uses italic 600 |
| Space Grotesk | 500, 600, 700 | **600 and 700 only** — weight 500 is fetched and never used anywhere |
| Inter | 400, 500, 600 | **400 (default) and 500 only** — weight 600 is fetched and never used anywhere |

Two unused weight downloads on every page load (Inter 600, Space Grotesk
500) — dropping them from the Google Fonts URL in the 7 `<link>` tags
would be a pure size win with no visual change, once confirmed nothing
relies on browser weight-matching/synthesis picking them up indirectly.

## 5. Unused Packages

**Every direct top-level dependency is actively imported:** `Authlib`
(`auth.py`), `Flask`/`Flask-Login` (`app.py`, `auth.py`), `firebase_admin`
(`firebase_otp.py`), `python-dotenv` (`app.py`, via its `dotenv` import
name), `requests` (`app.py`, `msg91.py`, `resend_email.py`), `Werkzeug`
(`auth.py`, `werkzeug.security`). `gunicorn` isn't imported in any `.py`
file, but that's expected — it's invoked as the WSGI process runner via
`Procfile`/`render.yaml`, not used as a library.

The other ~15 entries (`blinker`, `certifi`, `cffi`, `charset-normalizer`,
`click`, `cryptography`, `idna`, `importlib_metadata`, `itsdangerous`,
`Jinja2`, `MarkupSafe`, `packaging`, `pycparser`, `typing_extensions`,
`urllib3`, `zipp`) are transitive dependencies of the packages above
(Flask needs `click`/`itsdangerous`/`Jinja2`/`MarkupSafe`/`blinker`;
`requests` needs `certifi`/`charset-normalizer`/`idna`/`urllib3`;
`cryptography`/`cffi`/`pycparser` back `Authlib`'s JWT signing). This
`requirements.txt` reads as a full `pip freeze` dump rather than a
hand-curated direct-dependency list — normal and reproducible-build-friendly,
just means "unused package" isn't a meaningful question at the file level;
the meaningful check (every *direct* dependency has a real call site) passes.

No frontend package manager exists (no `package.json` anywhere in the
project), so there's no JS dependency tree to audit.

## 6. Unused Imports

**Zero found.** Every `.py` file was parsed with Python's `ast` module
(not just grepped) and every imported name checked for a use elsewhere in
its file — clean across all 10 files. Every `.jsx`/`.js` file in
`components/`, `hooks/`, `lib/`, `constants/` was checked the same way in
the frontend-reorganization pass two turns ago and re-verified here —
also clean.

## 7. Dead code

**`constants/tiers.js` — 3 of 6 exports are never imported anywhere:**
`TIER_KEYS`, `TIER_LABEL_TO_KEY`, `tierKeyFromLabel`. `Card.jsx` and
`Badge.jsx` only consume `TIER_GRADIENTS`, `TIER_BORDER_OVERRIDES`, and
`TIER_DOT_COLORS`. The other three look like they were built to map the
database's tier-label string (e.g. `"Lifetime Free"`) to the internal key
(`"free"`) once a page component fetches real card data — reasonable to
anticipate, but nothing calls them today.

**`verify_recommend.py` — zero references anywhere in the project**, and
its own scoring logic (`tier_from_fee`, category matching) is
hand-duplicated locally rather than importing from `scoring.py`, which
suggests it predates or has drifted from the current recommendation
engine. Strongest dead-code candidate in the backend — but it's plausibly
a manually-run verification script someone still invokes by hand
(`python verify_recommend.py`), so this flags it for **you to confirm**,
not a claim that it's safe to delete.

**`migrate_auth.py` / `migrate_phone.py` — one-time DB migration
scripts**, not imported or run by the live app (`app.py` never touches
them), referenced only in a one-line comment in `auth.py` ("see
migrate_auth.py"). Whether these are dead depends on information this
review can't see from the repo alone: has the migration they perform
already been applied to the production database? If yes, they're now
historical/dead; if any environment still needs to run them (e.g. a fresh
local setup from an old schema), they're not. Flagging for your
confirmation rather than guessing.

**`credit_cards.db.bak_old_schema` — local-only backup file**, correctly
listed in `.gitignore` (`*.db.bak_old_schema`) so it was never committed
to the repo, and unreferenced by any code. Safe to remove from your local
checkout whenever convenient — this one's genuinely inert, just not
committed cruft since git already excludes it.

No commented-out code blocks or `TODO`/`FIXME`/`XXX` markers found
anywhere in the project.

---

## One adjacent finding (not a requested category, surfaced while checking related things)

`.env.example` is missing 3 keys that both `.env` and `render.yaml`
reference: `FIREBASE_SERVICE_ACCOUNT_PATH`, `RESEND_API_KEY`,
`RESEND_FROM_EMAIL`. Not "unused" — the opposite, they're used but
undocumented for anyone setting up a new environment from the example
file. Mentioned since it surfaced directly while checking env-var usage
for this report.
