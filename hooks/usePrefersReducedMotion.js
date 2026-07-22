import { useEffect, useState } from "react";

const QUERY = "(prefers-reduced-motion: reduce)";

function getInitial() {
  if (typeof window === "undefined" || !window.matchMedia) return false;
  return window.matchMedia(QUERY).matches;
}

/**
 * Tracks the user's OS-level reduced-motion preference live (updates if
 * they change the setting without reloading, not just on mount). Not
 * currently wired into any component -- kept as a ready-to-use utility
 * for whichever future animation needs it (Lumen requires every new
 * animation to have a reduced-motion branch).
 */
export default function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(getInitial);

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mql = window.matchMedia(QUERY);
    const onChange = () => setReduced(mql.matches);
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, []);

  return reduced;
}
