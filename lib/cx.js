/**
 * Joins class names, dropping falsy values. Every component
 * (Button, Input, Card, Badge, Footer) independently built this exact
 * `[...].filter(Boolean).join(" ")` one-liner inline — pulled out here
 * during the frontend/ reorganization so there's one definition instead
 * of five copies.
 *
 * @param  {...(string|false|null|undefined)} classes
 * @returns {string}
 */
export default function cx(...classes) {
  return classes.filter(Boolean).join(" ");
}
