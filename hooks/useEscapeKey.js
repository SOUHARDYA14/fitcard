import { useEffect } from "react";

/**
 * Calls `onEscape` while `active` is true and the Escape key is pressed.
 * Extracted out of Modal.jsx's mount effect so it's reusable by any
 * future dismissible overlay (a toast, a dropdown) without copying the
 * listener-add/remove boilerplate again.
 *
 * @param {boolean} active
 * @param {() => void} onEscape
 */
export default function useEscapeKey(active, onEscape) {
  useEffect(() => {
    if (!active) return;
    const onKeyDown = (e) => {
      if (e.key === "Escape") onEscape?.();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [active, onEscape]);
}
