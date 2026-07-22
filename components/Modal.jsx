import React from "react";
import "./Modal.css";
import { useEscapeKey, useLockBodyScroll } from "../hooks";

/**
 * NEW component — docs/COMPONENT_AUDIT.md §8 confirmed no modal/dialog
 * pattern exists anywhere in the current templates (grep for
 * modal|dialog|popup returned nothing). This isn't deduplicating
 * anything; it's the primitive the audit recommended building up
 * front, styled to match the site's existing surfaces (same
 * background/border/radius/shadow language as the `Card` "auth"
 * variant) so a future feature doesn't hand-roll its own overlay.
 *
 * @param {boolean} open
 * @param {() => void} onClose called on Escape or backdrop click
 * @param {string} [title]
 * @param {React.ReactNode} [footer] optional action row (e.g. Buttons)
 * @param {"sm"|"md"} [size="md"]
 */
export default function Modal({
  open,
  onClose,
  title,
  footer,
  size = "md",
  children,
}) {
  useEscapeKey(open, onClose);
  useLockBodyScroll(open);

  if (!open) return null;

  return (
    <div
      className="fc-modal-backdrop"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose?.();
      }}
    >
      <div
        className={`fc-modal fc-modal--${size}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? "fc-modal-title" : undefined}
      >
        {title && (
          <div className="fc-modal__header">
            <h2 id="fc-modal-title" className="fc-modal__title">
              {title}
            </h2>
            <button
              type="button"
              className="fc-modal__close"
              aria-label="Close"
              onClick={onClose}
            >
              ×
            </button>
          </div>
        )}
        <div className="fc-modal__body">{children}</div>
        {footer && <div className="fc-modal__footer">{footer}</div>}
      </div>
    </div>
  );
}
