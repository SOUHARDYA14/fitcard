import React from "react";
import "./Card.css";
import { TIER_GRADIENTS, TIER_BORDER_OVERRIDES } from "../constants";
import { cx } from "../lib";

/**
 * Consolidates the auth-page `.card` (identical in login / login_phone /
 * signup / verify_otp — 4 copies of the same block) and formalizes
 * match.html's `.cc` recommendation card (already effectively "one
 * component with tier variants" in the legacy CSS, just expressed as
 * ad hoc classes). See docs/COMPONENT_AUDIT.md §2.
 *
 * @param {"auth"|"recommendation"|"plain"} [variant="plain"]
 *   auth           — templates/login.html etc. `.card`
 *   recommendation — templates/match.html `.cc` / `.cc.t-*` / `.cc.best`
 *   plain          — new: generic surface container, no legacy source,
 *                    provided for any future card that isn't one of the
 *                    two above rather than a third hand-rolled block
 * @param {keyof typeof TIER_GRADIENTS} [tier] required for variant="recommendation"
 * @param {boolean} [best] adds the looping gold glow + is used by
 *   consumers to decide whether to render a "Best match" Badge instead
 *   of a rank number (the badge itself is not this component's concern)
 * @param {number} [index] stagger index for the recommendation card's
 *   entrance animation delay, mirrors the legacy `--i` custom property
 * @param {boolean} [animate=true]
 */
export default function Card({
  variant = "plain",
  tier,
  best = false,
  index = 0,
  animate = true,
  className = "",
  style,
  children,
  ...rest
}) {
  const classes = cx(
    "fc-card",
    `fc-card--${variant}`,
    variant === "recommendation" && tier && `fc-card--t-${tier}`,
    variant === "recommendation" && best && "fc-card--best",
    !animate && "fc-card--static",
    className
  );

  const cardStyle = { ...style };
  if (variant === "recommendation") {
    cardStyle["--fc-card-i"] = index;
    if (tier && TIER_GRADIENTS[tier]) {
      cardStyle.background = TIER_GRADIENTS[tier];
    }
    if (tier && TIER_BORDER_OVERRIDES[tier]) {
      cardStyle.borderColor = TIER_BORDER_OVERRIDES[tier];
    }
  }

  return (
    <div className={classes} style={cardStyle} {...rest}>
      {children}
    </div>
  );
}
