# Requirements

- Ticket: `webcam-control-app`
- Status: `Design-ready`
- Date: `2026-03-06`
- Scope: `Medium`

## Problem Statement

Build a Windows desktop app that lets the user control system actions using webcam hand gestures with a safe enable/disable toggle and visible runtime feedback.

## Functional Requirements

| Requirement ID | Description |
| --- | --- |
| R-001 | Capture webcam frames and detect one primary hand at runtime. |
| R-002 | Recognize gestures from hand landmarks (`pointer`, `pinch`, `two_finger_scroll`, `open_palm`, `v_sign`, `fist`). |
| R-003 | Map recognized gestures to action intents via configurable JSON. |
| R-004 | Execute OS actions on Windows for mapped intents (pointer move, left click, scroll, media toggle, app switch, control toggle). |
| R-005 | Render runtime overlay with current gesture, control mode state, and FPS. |
| R-006 | Enforce cooldown and edge-trigger semantics so actions fire once per eligible gesture transition. |
| R-007 | When control mode is disabled, no system action is emitted. |
| R-008 | Build a distributable Windows executable package from this repository. |
| R-009 | Provide an install flow that copies the app to a user install location and creates launch shortcuts. |

## Non-Functional Requirements

| Requirement ID | Description |
| --- | --- |
| NFR-001 | Run on Windows 10/11 with Python 3.10+. |
| NFR-002 | Keep architecture decoupled: tracking, classification, mapping, and OS control must be separate modules. |
| NFR-003 | Provide deterministic unit tests for gesture mapping and dispatch logic without webcam dependency. |
| NFR-004 | Packaged executable must launch without requiring a separate Python command from the user. |

## Acceptance Criteria

| AC ID | Requirement Mapping | Acceptance Criteria |
| --- | --- | --- |
| AC-01 | R-001, R-005, NFR-001 | Running `python -m app.main --help` validates entrypoint wiring; running `python -m app.main` enters webcam loop with overlay when camera is available. |
| AC-02 | R-002 | Recognizer outputs expected gesture labels for representative landmark patterns in unit tests. |
| AC-03 | R-003, R-006 | Gesture-to-intent mapping and cooldown behavior are configurable and validated in tests. |
| AC-04 | R-004 | Dispatcher calls correct OS controller methods for pointer move, click, scroll, media toggle, and app switch. |
| AC-05 | R-007 | Toggle action disables all other system actions until toggled back on. |
| AC-06 | NFR-002 | Project modules separate concerns with one-way dependency direction (tracking -> gesture -> controller). |
| AC-07 | NFR-003 | `python -m unittest discover -s tests -v` passes without needing webcam hardware. |
| AC-08 | R-008 | Build command produces `dist/WebcamGestureControl/WebcamGestureControl.exe`. |
| AC-09 | R-009 | Install script copies built app into `%LOCALAPPDATA%\\Programs\\WebcamGestureControl` and creates Desktop + Start Menu shortcuts. |
| AC-10 | R-009, NFR-004 | Launching installed shortcut starts the app executable. |

## Out Of Scope For This MVP

- Face authentication and leave-detection lock.
- Browser-specific navigation routing.
- Gaming profile pack and anti-cheat compatibility.
- MSI packaging/signing.
