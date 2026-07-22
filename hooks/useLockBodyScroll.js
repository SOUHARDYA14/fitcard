import { useEffect } from "react";

/**
 * Locks `document.body` scrolling while `active` is true, restoring
 * whatever the previous inline `overflow` value was on cleanup (not
 * just resetting to `""`, in case something else had already set it).
 * Extracted out of Modal.jsx's mount effect for the same reason as
 * useEscapeKey — reusable by any future full-screen overlay.
 *
 * @param {boolean} active
 */
export default function useLockBodyScroll(active) {
  useEffect(() => {
    if (!active) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prevOverflow;
    };
  }, [active]);
}
