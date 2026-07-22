import React from "react";
import { createRoot } from "react-dom/client";

/**
 * Reads the server-provided initial data out of the page-data script
 * tag and mounts a React root into #root. Every migrated page's
 * main.jsx calls this instead of hand-rolling JSON.parse + createRoot
 * — see the migration plan's "React islands" approach: Flask/Jinja
 * renders the shell + this data, React only owns the mount div's
 * contents, no client-side routing.
 *
 * Plain .js (no JSX) so this file needs no special Vite/esbuild loader
 * config — every *.jsx file in this project does get one automatically.
 *
 * @param {React.ComponentType<any>} PageComponent
 */
export default function mountPage(PageComponent) {
  const rootEl = document.getElementById("root");
  const dataEl = document.getElementById("page-data");

  if (!rootEl) {
    throw new Error("mountPage: no #root element found in the page shell");
  }

  const initialData = dataEl ? JSON.parse(dataEl.textContent) : {};

  createRoot(rootEl).render(
    React.createElement(
      React.StrictMode,
      null,
      React.createElement(PageComponent, initialData)
    )
  );
}
