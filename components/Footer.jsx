import React from "react";
import "./Footer.css";
import { cx } from "../lib";

/**
 * Consolidates the page-disclaimer `<footer>` that exists on only 2 of
 * 7 pages (welcome.html, match.html) and was declared independently in
 * each with slightly different max-width/margin/padding. cards.html
 * and the 4 auth pages currently have no footer at all — see
 * docs/COMPONENT_AUDIT.md §5. Not to be confused with `.foot`, the
 * auth-card "Already have an account?" links block, which the audit
 * explicitly calls out as a different component despite the name.
 *
 * @param {"wide"|"narrow"} [variant="wide"]
 *   wide   — templates/welcome.html <footer> (max-width 1160px)
 *   narrow — templates/match.html <footer> (max-width 820px)
 */
export default function Footer({ variant = "wide", className = "", children }) {
  const classes = cx("fc-footer", `fc-footer--${variant}`, className);
  return <footer className={classes}>{children}</footer>;
}
