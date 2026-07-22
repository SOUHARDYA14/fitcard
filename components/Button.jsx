import React from "react";
import "./Button.css";
import { useMagnetic } from "../hooks";
import { cx } from "../lib";

/**
 * Consolidates 6 independent gold-button declarations
 * (welcome .btn-primary, match .submit-btn, and the bare `button` in
 * login / login_phone / signup / verify_otp) plus the 2x-duplicated
 * .btn-google, into one component. See docs/COMPONENT_AUDIT.md §1.
 *
 * Renders an <a> when `href` is passed, a <button> otherwise — the
 * legacy primary buttons were sometimes links (welcome CTAs) and
 * sometimes real submit buttons (auth forms, match form).
 *
 * @param {"primary"|"secondary"|"oauth"|"link"} [variant="primary"]
 * @param {"md"|"compact"} [size="md"] "compact" matches the 13px/20px
 *   padding used by the 4 auth-page buttons; "md" matches welcome/match.
 * @param {boolean} [fullWidth] auth-page buttons and .btn-google are width:100%
 * @param {boolean} [loading] shows the spinner + dims the label, exactly
 *   like match.html's `button.submit-btn.loading` (the only legacy
 *   button that had a loading state)
 * @param {boolean} [glow] idle pulse-glow ring — only welcome.html's
 *   primary CTA used this (`pulseGlow` animation)
 * @param {boolean} [magnetic] pointer-follow drift, matching the
 *   `.magnetic` behavior from static/theme.js
 * @param {React.ReactNode} [icon]
 */
export default function Button({
  variant = "primary",
  size = "md",
  fullWidth = false,
  loading = false,
  glow = false,
  magnetic = false,
  disabled = false,
  icon,
  href,
  type = "button",
  className = "",
  children,
  onClick,
  ...rest
}) {
  // usePrefersReducedMotion is checked inside useMagnetic itself (WCAG
  // 2.3.3, Animation from Interactions) — see hooks/useMagnetic.js.
  const { ref, onMouseMove, onMouseLeave } = useMagnetic(magnetic);

  const classes = cx(
    "fc-btn",
    `fc-btn--${variant}`,
    size === "compact" && "fc-btn--compact",
    fullWidth && "fc-btn--full",
    glow && "fc-btn--glow",
    loading && "is-loading",
    className
  );

  const content =
    variant === "link" ? (
      children
    ) : (
      <>
        {loading && <span className="fc-btn__spinner" aria-hidden="true" />}
        {!loading && variant === "oauth" && (icon || <GoogleIcon />)}
        {!loading && icon && variant !== "oauth" && icon}
        <span className="fc-btn__label">{children}</span>
      </>
    );

  const commonProps = {
    ref,
    className: classes,
    onMouseMove,
    onMouseLeave,
    onClick,
    ...rest,
  };

  if (href) {
    return (
      <a href={href} {...commonProps}>
        {content}
      </a>
    );
  }

  return (
    <button
      type={type}
      disabled={disabled || loading}
      {...commonProps}
    >
      {content}
    </button>
  );
}

// Colors below are Google's mandated multi-color "G" mark, not part of
// FitCard's design system — left hardcoded intentionally, same call
// docs/UI_AUDIT.md made. Tokenizing brand-mandated third-party colors
// would let a future palette change silently violate Google's usage
// guidelines.
function GoogleIcon() {
  return (
    <svg viewBox="0 0 48 48" width="16" height="16" aria-hidden="true">
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3c-1.6 4.7-6.1 8-11.3 8-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.1 8 3l6-6C34.5 5.1 29.5 3 24 3 12.4 3 3 12.4 3 24s9.4 21 21 21 21-9.4 21-21c0-1.4-.1-2.7-.4-3.5z" />
      <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.6 15.9 18.9 13 24 13c3.1 0 5.8 1.1 8 3l6-6C34.5 5.1 29.5 3 24 3c-7.4 0-13.8 4.2-17 10.3z" />
      <path fill="#4CAF50" d="M24 45c5.4 0 10.3-1.8 14.1-5l-6.5-5.5C29.5 36 26.9 37 24 37c-5.2 0-9.6-3.3-11.2-8l-6.6 5.1C9.1 40.6 16 45 24 45z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.3-2.2 4.2-4.1 5.5l6.5 5.5C41.5 35.7 45 30.5 45 24c0-1.4-.1-2.7-.4-3.5z" />
    </svg>
  );
}
