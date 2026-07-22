import React from "react";
import "./AmbientBackground.css";

/**
 * The soft radial-gradient glow + grain texture that sits behind every
 * legacy page's content (`templates/*.html`'s body background +
 * `static/theme.css`'s `.grain`). Flagged as a recommended-but-unbuilt
 * component in docs/COMPONENT_AUDIT.md (§"Recommended Component
 * Library" #10, the largest single raw-CSS duplication found in that
 * audit — 6 copies) but never built, so `pages/cards/CardsPage.jsx`
 * shipped with a flat background instead. This is that component,
 * built after the fact once the gap became visible.
 *
 * Render once, near the top of a page's tree — it's fixed-position and
 * covers the viewport regardless of where it's mounted.
 */
export default function AmbientBackground() {
  return (
    <>
      <div className="fc-ambient-glow" aria-hidden="true" />
      <div className="fc-ambient-grain" aria-hidden="true" />
    </>
  );
}
