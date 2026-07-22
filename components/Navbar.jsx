import React from "react";
import "./Navbar.css";

/**
 * Consolidates the brand/chip logo mark — declared in all 7 templates,
 * the widest single duplication found in docs/COMPONENT_AUDIT.md (§4) —
 * plus the two page-header shapes built around it: welcome.html's full
 * `<nav>` and the stripped-down `.hero-row` duplicated between
 * cards.html and match.html. The 4 auth pages' brand-mark-only header
 * is the third, smallest shape.
 *
 * @param {"full"|"back-link"|"brand-only"} variant
 *   full        — templates/welcome.html `<nav>`
 *   back-link   — templates/cards.html & templates/match.html `.hero-row`
 *   brand-only  — templates/login.html etc. `.brand` inside the auth card
 * @param {string} [brandHref="/"]
 * @param {{href:string,label:string}[]} [links] variant="full" only
 * @param {{href:string,label:string}[]} [backLinks] variant="back-link" only
 * @param {boolean} [authenticated] variant="full" only — swaps
 *   Sign in/Sign up for Logout, matching welcome.html's
 *   `{% if current_user.is_authenticated %}` branch
 * @param {string} [issueTag] variant="full" only, e.g. "Matching Engine — 2026"
 *   (legacy `.issue-tag` — `display:none` by default in the source CSS,
 *   kept hidden here unless a consumer opts in via className override)
 * @param {boolean} [mastheadRule=true] renders the hairline rule under the header
 */
export default function Navbar({
  variant,
  brandHref = "/",
  links = [],
  backLinks = [],
  authenticated = false,
  issueTag,
  mastheadRule = true,
  loginHref = "/login",
  signupHref = "/signup",
  logoutHref = "/logout",
}) {
  const chipSize = variant === "full" ? "fc-navbar__chip--lg" : "";

  return (
    <>
      <div className={`fc-navbar fc-navbar--${variant}`}>
        <a href={brandHref} className="fc-navbar__brand">
          <span className={`fc-navbar__chip ${chipSize}`} />
          FitCard
        </a>

        {variant === "full" && (
          <div className="fc-navbar__right">
            {issueTag && <span className="fc-navbar__issue-tag">{issueTag}</span>}
            <div className="fc-navbar__links">
              {links.map((link) => (
                <a key={link.href} href={link.href}>
                  {link.label}
                </a>
              ))}
              {authenticated ? (
                <a href={logoutHref}>Logout</a>
              ) : (
                <>
                  <a href={loginHref}>Sign in</a>
                  <a href={signupHref}>Sign up</a>
                </>
              )}
            </div>
          </div>
        )}

        {variant === "back-link" && (
          <div className="fc-navbar__right">
            {backLinks.map((link) => (
              <a key={link.href} href={link.href} className="fc-navbar__back-link">
                {link.label}
              </a>
            ))}
          </div>
        )}
      </div>

      {mastheadRule && variant !== "brand-only" && (
        <div className="fc-navbar__masthead-rule">
          {variant === "full" && <div className="fc-navbar__hairline" />}
        </div>
      )}
    </>
  );
}
