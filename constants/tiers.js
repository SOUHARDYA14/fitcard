/**
 * Shared tier lookup tables for the credit-card tier system
 * (Lifetime Free / Entry / Mid-range / Super Premium / Luxury / n/a).
 *
 * docs/COMPONENT_AUDIT.md found this defined TWICE independently in the
 * legacy templates, with different colors for the same six tiers:
 *   - templates/match.html   `.cc.t-*`      (gradient backgrounds)
 *   - templates/cards.html   `.tier-dot.*`  (dot + label color)
 *
 * Per "do not change functionality," this file does NOT unify those two
 * color sets into one — that would visibly change one of the two contexts.
 * It just gives each of the two existing mappings a single source of
 * truth instead of a copy living in each component that needs it.
 * Reconciling the two mappings into one is a follow-up decision, not
 * made here.
 *
 * Moved here from components/tierTheme.js during the frontend/
 * reorganization — this is data (lookup tables), not a component, so it
 * belongs in constants/, not components/. See components/README.md.
 */

export const TIER_KEYS = ["free", "entry", "mid", "super", "luxury", "na"];

/** Card background gradients — from templates/match.html `.cc.t-*` */
export const TIER_GRADIENTS = {
  entry: "linear-gradient(135deg, var(--color-tier-entry-start), var(--color-tier-entry-end))",
  free: "linear-gradient(135deg, var(--color-tier-free-start), var(--color-tier-free-end))",
  mid: "linear-gradient(135deg, var(--color-secondary-alt), var(--color-secondary-deep))",
  super: "linear-gradient(135deg, var(--color-secondary-super), var(--color-secondary))",
  luxury: "linear-gradient(135deg, var(--color-tier-luxury-start), var(--color-tier-luxury-end))",
  na: "linear-gradient(135deg, var(--color-tier-na-start), var(--color-tier-na-end))",
};

/** Luxury tier also gets a warmer border in the card context */
export const TIER_BORDER_OVERRIDES = {
  luxury: "var(--color-primary-a40)",
};

/** Dot + label color — from templates/cards.html `.tier-dot.*` */
export const TIER_DOT_COLORS = {
  free: "var(--color-success)",
  entry: "var(--color-tier-entry-dot)",
  mid: "var(--color-tier-mid-dot)",
  super: "var(--color-tier-super-dot)",
  luxury: "var(--color-primary)",
  na: "var(--color-tier-na-dot)",
};

/** Maps the DB's human tier label to the internal tier key used above. */
export const TIER_LABEL_TO_KEY = {
  "Lifetime Free": "free",
  "Entry": "entry",
  "Mid-range": "mid",
  "Super Premium": "super",
  "Luxury": "luxury",
};

export function tierKeyFromLabel(label) {
  return TIER_LABEL_TO_KEY[label] || "na";
}
