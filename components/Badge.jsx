import React from "react";
import "./Badge.css";
import { TIER_DOT_COLORS } from "../constants";
import { cx } from "../lib";

/**
 * Consolidates 4 different small-label patterns from match.html and
 * cards.html that had no shared definition: the "Best match"/"#2" rank
 * pill (`.rank`), the category pill (`.cat-pill`), the tier dot+label
 * in the all-cards list (`.tier-dot`), and the score readout in the
 * top-right of a recommendation card (`.cc-score`). Not called out as
 * literal duplicates in docs/COMPONENT_AUDIT.md (each had one call
 * site), but requested explicitly as its own component — this is
 * where they now live instead of four separate inline blocks.
 *
 * @param {"rank"|"category"|"tier"|"score"} variant
 * @param {keyof import("../constants/tiers").TIER_DOT_COLORS} [tier] required for variant="tier"
 * @param {string} [label] display text for variant="tier" (e.g. "Lifetime Free");
 *   also the sub-label for variant="score" (defaults to "score")
 * @param {string|number} [value] the number for variant="score"
 */
export default function Badge({
  variant,
  tier,
  label,
  value,
  className = "",
  children,
  ...rest
}) {
  const classes = cx("fc-badge", `fc-badge--${variant}`, className);

  if (variant === "score") {
    return (
      <div className={classes} {...rest}>
        <span className="fc-badge__score-num">{value}</span>
        <span className="fc-badge__score-label">{label || "score"}</span>
      </div>
    );
  }

  if (variant === "tier") {
    const color = TIER_DOT_COLORS[tier] || TIER_DOT_COLORS.na;
    return (
      <span className={classes} style={{ "--fc-tier-color": color }} {...rest}>
        <span className="fc-badge__dot" />
        {label || children}
      </span>
    );
  }

  // rank / category
  return (
    <span className={classes} {...rest}>
      {children}
    </span>
  );
}
