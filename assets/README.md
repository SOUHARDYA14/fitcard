# assets/

Empty placeholder, created as part of the frontend reorganization
(components/ pages/ hooks/ lib/ styles/ constants/ assets/).

Intended for static files a component or page imports directly — icons,
images, fonts. Currently empty because the only graphic in the library,
the Google "G" logo in `Button.jsx`'s `GoogleIcon`, is kept as inline JSX
rather than a separate `.svg` file here: importing raw SVG as a React
component needs a loader (e.g. `vite-plugin-svgr`) that this
no-build-tooling project doesn't have configured, and inlining a 4-path
icon avoids that dependency entirely. If a real image/font asset shows
up, it belongs here.
