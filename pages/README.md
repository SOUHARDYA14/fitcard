# pages/

Empty placeholder, created as part of the frontend reorganization
(components/ pages/ hooks/ lib/ styles/ constants/ assets/).

Intended to hold future page-level compositions that assemble the
`components/` atoms into full screens — one per live route, mirroring
`templates/*.html`: `WelcomePage`, `MatchPage`, `CardsPage`, `LoginPage`,
`LoginPhonePage`, `SignupPage`, `VerifyOtpPage`.

Not built here — assembling those is new feature work (deciding page
structure, wiring the `/recommend` fetch call, replicating each page's
specific JS behavior), not a file reorganization. This README exists so
the folder isn't silently empty with no explanation.
