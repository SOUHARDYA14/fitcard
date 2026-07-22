import React from "react";
import "./Input.css";
import { cx } from "../lib";

/**
 * Consolidates the standard auth-page input (declared identically in
 * login / login_phone / signup / verify_otp, 4x — plus its `label`,
 * `.field` wrapper and `.hint` line, each also duplicated 4-5x), the
 * near-duplicate match.html `.field-row` input/select, the cards.html
 * underline filter input, and the verify_otp OTP-digit override.
 * See docs/COMPONENT_AUDIT.md §3.
 *
 * @param {"default"|"compact"|"underline"|"otp"} [variant="default"]
 *   default    — auth pages: surface-2 fill, Inter, 11px/12px padding
 *   compact    — match.html field-row: surface-2 fill, Space Grotesk, 9px/10px padding
 *   underline  — cards.html filter bar: no fill, bottom-border only
 *   otp        — verify_otp: `default` styling + large spaced-out digits
 * @param {"input"|"select"} [as="input"]
 * @param {string} [label]
 * @param {string} [hint]
 * @param {string} [error] renders in the danger color instead of the hint
 */
export default function Input({
  variant = "default",
  as = "input",
  id,
  label,
  hint,
  error,
  className = "",
  fieldClassName = "",
  children,
  ...rest
}) {
  const Tag = as;
  const classes = cx("fc-input", `fc-input--${variant}`, className);

  const field = (
    <Tag id={id} className={classes} {...rest}>
      {as === "select" ? children : undefined}
    </Tag>
  );

  if (!label && !hint && !error) {
    return field;
  }

  return (
    <div className={cx("fc-field", fieldClassName)}>
      {label && (
        <label className="fc-field__label" htmlFor={id}>
          {label}
        </label>
      )}
      {field}
      {error ? (
        <p className="fc-field__hint fc-field__hint--error">{error}</p>
      ) : (
        hint && <p className="fc-field__hint">{hint}</p>
      )}
    </div>
  );
}
