# Desktop reliability: timer crash and unexpected windows

## Confirmed cause and repair

`FlowLayout.addWidget` created `QWidgetItem` directly, bypassing Qt's widget
ownership registration. A card constructed in a helper could remain parentless;
releasing its Python reference destroyed its chart and child QTimer. The page
retained the chart wrapper and its next metrics refresh raised the exact
`libshiboken: Internal C++ object (PySide6.QtCore.QTimer) already deleted` error.
Parentless cards also behaved as independent windows instead of embedded UI.
The metrics refresh repeats every second, and the exception hook opens a modal
crash dialog. Repeated failures can therefore open additional error dialogs
while the first is still running its nested event loop. This is a source-derived
explanation for extra popups; the specific lab machine's windows were not observed.

The fix delegates widget insertion to `QLayout.addWidget`, retaining the custom
wrapping geometry. Hidden-state handling now distinguishes explicitly hidden
widgets from widgets inside a temporarily hidden page.

The ownership regression fails on the original implementation and passes on the
fix. It releases builder references, forces collection, updates/animates chart
data, and checks hide/show behavior and the card's parent.

## Verification without reinstalling

From the repository root, run:

```powershell
.venv\Scripts\python.exe main.py --smoke-test
```

For a packaged build, run its exact executable with `--smoke-test`. This now
constructs the real MainWindow with temporary configuration/history, navigates
Home/Insights/Settings twelve times, refreshes dashboard trends, exercises timers,
and fails if a visible extra window or invalid chart is found. It neither records
audio nor downloads a speech model. Unhandled Qt callbacks fail the smoke rather
than opening a modal error dialog. Exit code zero means the check passed.

The release workflow runs ownership/UI/instance regressions before packaging and
uses this same smoke on both the bundle and the installed executable on its
Windows runner. The old smoke opened only a blank QWidget and missed this bug.

Local verification on October 13, 2026: the full desktop suite passed with
213 tests and 73 platform skips, including both ownership orders and generated
data packaging exclusions. Source `--smoke-test` passed. The rebuilt
`dist-desktop-fix/RotaAI/RotaAI.exe --smoke-test` exited zero. This is a development
build using the repository's existing version; it is not a published update.
Installed-app validation on a clean Windows runner remains a release gate.
The spec now excludes local databases and cached bytecode. The completed local
bundle was cleaned with that same exclusion rule (139 generated files removed),
and its desktop smoke passed again. No such generated files remain in the bundle.
Inno Setup successfully compiled the cleaned bundle to
`installer-output/desktop-fix/RotaAI-Desktop-Fix-Setup.exe`. The local installer
was not installed over the user's existing app. Release v1.2.2 requires the
packaged and installed desktop checks on a clean Windows runner before upload.
The website resolves the latest published release dynamically; publication must
be followed by verification of its live download redirect and asset response.

## Wispr Flow evidence and remaining work

Read-only inspection selected the locally installed `app-1.6.1102/resources/app.asar`
(SHA-256 `5a35c867858fd0c14c643bf3530b0ba928869ff01a1383a437eb255db4969a74`).
REA extraction evidence: `ev_e55af3b07e540e2339769677854b84b52a6a7e169630f078c72bd323529e2a37`.
The `.webpack/main/index.js` bundle contains a single-instance lock, second-launch
handling, explicit handling of Squirrel installer events, startup preference
handling, and crash reporting hooks. These are static observations, not proof of
runtime reliability or a reconstruction of the private speech backend. Full
application graph analysis timed out. Three unpacked native files differed from
their declared archive integrity; extraction retained that limitation explicitly.

Rota already has a mutex/loopback instance guard and embedded settings. Its
loopback regression passes outside the network-restricted sandbox.

Further parity requires separate validation of microphone/device changes,
hotkey registration and focus, text insertion into normal/elevated applications,
clipboard restoration, model/provider failure recovery, shutdown while workers
are active, suspend/resume, update installation, and multi-monitor/DPI behavior.
This patch verifies desktop ownership/navigation; it does not certify those
hardware, provider, or operating-system scenarios.

Wispr's documented tray/relaunch behavior and text insertion recovery are useful
behavioral references:

- https://docs.wisprflow.ai/articles/7492559320-Quit-and-relaunch-Wispr-Flow
- https://docs.wisprflow.ai/articles/7971211038-fix-text-not-pasting-after-dictation
