import { useRef } from "react";
import usePrefersReducedMotion from "./usePrefersReducedMotion";

/**
 * Pointer-follow drift, matching the `.magnetic` behavior from
 * static/theme.js. Extracted out of Button.jsx so any future component
 * (the welcome-page CTAs and the match-form submit button both used
 * `.magnetic` in the legacy site) can reuse it without copying the
 * mousemove/mouseleave math again.
 *
 * @param {boolean} enabled
 * @returns {{ref: React.RefObject, onMouseMove: Function, onMouseLeave: Function}}
 */
export default function useMagnetic(enabled) {
  const ref = useRef(null);
  const reducedMotion = usePrefersReducedMotion();

  const onMouseMove = (e) => {
    if (!enabled || !ref.current || reducedMotion) return;
    const rect = ref.current.getBoundingClientRect();
    const dx = e.clientX - (rect.left + rect.width / 2);
    const dy = e.clientY - (rect.top + rect.height / 2);
    ref.current.style.transform = `translate(${dx * 0.25}px, ${dy * 0.35}px)`;
  };

  const onMouseLeave = () => {
    if (!enabled || !ref.current) return;
    ref.current.style.transform = "translate(0,0)";
  };

  return { ref, onMouseMove, onMouseLeave };
}
