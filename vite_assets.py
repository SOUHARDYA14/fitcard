"""Bridges Vite's build output (or its dev server) into Jinja templates.

Registered as a Jinja global (`vite_asset`) in app.py so a template can do:

    {{ vite_asset('pages/cards/main.jsx') }}

and get back the right <script type="module">/<link rel="stylesheet">
tags for that entry, in both modes:

- prod (default): reads static/dist/.vite/manifest.json, built by
  `npm run build`. The manifest is cached in memory unless FLASK_DEBUG=1,
  matching how the rest of this app already treats FLASK_DEBUG as its
  "don't trust cached/precomputed state" flag (see app.py's DEV_OTP_ALLOWED).
- dev (VITE_DEV=1): points straight at the Vite dev server
  (http://localhost:5173) instead of the manifest, plus the
  @vite/client script it needs for HMR. The <script> tag being
  cross-origin does NOT make the page cross-origin — the document
  itself is still served by Flask, so fetch()/cookies stay same-origin.
  See the migration plan for why that distinction matters here (this
  app has no CSRF tokens; its actual defense is "no CORS headers are
  ever sent," which this dev setup does not disturb).
"""

import json
import os
from pathlib import Path
from urllib.parse import quote

from markupsafe import Markup

_DIST_DIR = Path(__file__).parent / "static" / "dist"
_MANIFEST_PATH = _DIST_DIR / ".vite" / "manifest.json"
_VITE_DEV_SERVER = "http://localhost:5173"

_manifest_cache = None


def _load_manifest():
    global _manifest_cache
    if _manifest_cache is not None and not os.environ.get("FLASK_DEBUG"):
        return _manifest_cache
    if not _MANIFEST_PATH.exists():
        raise RuntimeError(
            f"No Vite manifest at {_MANIFEST_PATH}. Run `npm run build` first "
            "(or set VITE_DEV=1 and run `npm run dev` for the dev workflow)."
        )
    with open(_MANIFEST_PATH) as f:
        manifest = json.load(f)
    _manifest_cache = manifest
    return manifest


def vite_asset(entry_name: str) -> Markup:
    """Returns the <script>/<link> tags for a Vite entry, given its
    source path relative to the repo root (e.g. "pages/cards/main.jsx",
    matching the key used in vite.config.js's build.rollupOptions.input
    — Vite's manifest keys entries by their source path, not the name
    given in the input map)."""
    if os.environ.get("VITE_DEV"):
        # vite.config.js sets base: "/static/dist/" for the production build
        # path; Vite's dev server applies that same base to its own URLs
        # too (not just prod output), so dev requests need the identical
        # prefix or the dev server 404s them ("did you mean to visit
        # /static/dist/@vite/client instead?").
        base = "/static/dist"
        src = f"{_VITE_DEV_SERVER}{base}/{quote(entry_name)}"
        # @vitejs/plugin-react's Fast Refresh runtime normally gets wired
        # up by Vite's own transformIndexHtml hook, which only runs when
        # Vite serves the HTML document itself. Here Flask serves the
        # HTML, so that hook never runs -- component modules that use
        # Fast Refresh (anything with JSX) fail at import time with
        # "@vitejs/plugin-react can't detect preamble" unless this
        # preamble is injected by hand, before any component script
        # loads. Standard workaround for any non-Vite-served-HTML +
        # @vitejs/plugin-react integration (Rails+Vite, Django+Vite, etc.
        # all carry an equivalent snippet).
        preamble = (
            f'<script type="module">\n'
            f'  import RefreshRuntime from "{_VITE_DEV_SERVER}{base}/@react-refresh"\n'
            f"  RefreshRuntime.injectIntoGlobalHook(window)\n"
            f"  window.$RefreshReg$ = () => {{}}\n"
            f"  window.$RefreshSig$ = () => (type) => type\n"
            f"  window.__vite_plugin_react_preamble_installed__ = true\n"
            f"</script>"
        )
        return Markup(
            f"{preamble}\n"
            f'<script type="module" src="{_VITE_DEV_SERVER}{base}/@vite/client"></script>\n'
            f'<script type="module" src="{src}"></script>'
        )

    manifest = _load_manifest()
    entry = manifest.get(entry_name)
    if entry is None:
        raise RuntimeError(
            f"No manifest entry for {entry_name!r}. Available entries: "
            f"{list(manifest.keys())}"
        )

    tags = []
    for css_path in entry.get("css", []):
        tags.append(f'<link rel="stylesheet" href="/static/dist/{css_path}">')
    tags.append(
        f'<script type="module" src="/static/dist/{entry["file"]}"></script>'
    )
    return Markup("\n".join(tags))
