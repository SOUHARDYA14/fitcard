import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Builds React "island" entries that Flask mounts into Jinja shell
// templates — see vite_assets.py and the plan this implements
// (docs/FITCARD_DESIGN_SPEC.md §12-14, and the migration plan under
// /Users/test/.claude/plans/). One named entry per migrated page;
// grows as more templates are migrated. Never a single SPA entry —
// there's no client-side router, Flask stays the document server.
export default defineConfig({
  plugins: [react()],
  root: ".",
  base: "/static/dist/",
  server: {
    port: 5173,
    strictPort: true,
  },
  build: {
    outDir: "static/dist",
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        cards: "pages/cards/main.jsx",
      },
    },
  },
});
