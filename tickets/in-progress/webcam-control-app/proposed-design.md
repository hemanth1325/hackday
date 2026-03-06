# Proposed Design Document

## Design Version

- Current Version: `v2`

## Revision History

| Version | Trigger | Summary Of Changes | Related Review Round |
| --- | --- | --- | --- |
| v1 | Initial design | Defined modular webcam-control architecture for Windows MVP | 1 |
| v2 | Requirement-gap re-entry | Added executable packaging and install workflow design | 3 |

## Artifact Basis

- Investigation Notes: `tickets/in-progress/webcam-control-app/investigation-notes.md`
- Requirements: `tickets/in-progress/webcam-control-app/requirements.md`
- Requirements Status: `Design-ready`

## Goals

- Deliver a runnable Windows app with webcam-driven desktop control.
- Keep control pipeline modular and testable.
- Prevent unsafe accidental control output via a hard toggle.

## Legacy Removal Policy (Mandatory)

- Policy: `No backward compatibility; remove legacy code paths.`
- Required action: greenfield implementation, so no legacy path retention is needed.

## Requirements And Use Cases

| Requirement ID | Description | Acceptance Criteria ID(s) | Use Case IDs |
| --- | --- | --- | --- |
| R-001 | Webcam frame capture + hand tracking | AC-01 | UC-001 |
| R-002 | Gesture classification from landmarks | AC-02 | UC-002 |
| R-003 | Config-based gesture-action mapping | AC-03 | UC-003 |
| R-004 | Execute Windows control actions | AC-04 | UC-004 |
| R-007 | Safety toggle gate | AC-05 | UC-005 |
| R-008 | Build distributable executable | AC-08 | UC-006 |
| R-009 | Install packaged app with launch shortcuts | AC-09, AC-10 | UC-007 |

## Shared Architecture Principles

- SoC cause: each module owns one responsibility.
- Layering result: orchestration -> gesture logic -> OS adapter.
- Decoupling rule: classifier and dispatcher depend on typed data, not OpenCV/MediaPipe objects.

## Change Inventory (Delta)

| Change ID | Change Type | Current Path | Target Path | Rationale |
| --- | --- | --- | --- | --- |
| C-001 | Add | N/A | `app/main.py` | Runtime entrypoint and app loop. |
| C-002 | Add | N/A | `app/tracking/hand_tracker.py` | Camera + landmark extraction adapter. |
| C-003 | Add | N/A | `app/gestures/classifier.py` | Landmark-to-gesture classification. |
| C-004 | Add | N/A | `app/control/controller.py` | Windows action execution adapter. |
| C-005 | Add | N/A | `app/core/dispatcher.py` | Gesture-to-intent dispatch + cooldown/toggle rules. |
| C-006 | Add | N/A | `app/config/actions.json` | User-editable mapping and tuning. |
| C-007 | Add | N/A | `tests/*` | Unit and integration-like logic tests. |
| C-008 | Add | N/A | `docs/webcam-gesture-control.md` | Long-lived usage and architecture docs. |
| C-009 | Add | N/A | `scripts/build-exe.ps1` | Deterministic executable build command. |
| C-010 | Add | N/A | `scripts/install.ps1` | User-level install + shortcut creation. |
| C-011 | Add | N/A | `scripts/uninstall.ps1` | User-level uninstall cleanup. |
| C-012 | Modify | `app/main.py` | `app/main.py` | Frozen runtime config resolution for executable mode. |

## Target Architecture Shape And Boundaries

| Layer/Boundary | Purpose | Owns | Must Not Own |
| --- | --- | --- | --- |
| Runtime orchestrator (`main`) | Drive frame loop and compose modules | loop lifecycle, FPS, overlay | gesture rules or OS API details |
| Tracking adapter | Convert camera frame to normalized landmarks | OpenCV/MediaPipe calls | action dispatch logic |
| Gesture logic | Classify gestures + map to intents | pure gesture heuristics | camera or OS APIs |
| Control adapter | Execute Windows actions | mouse/keyboard/media actions | gesture classification |

## Backward-Compatibility Rejection Log

| Candidate Compatibility Mechanism | Rejection Decision | Replacement Clean-Cut Design |
| --- | --- | --- |
| Support old and new gesture schemas simultaneously | Rejected | single canonical JSON schema for mappings |
| Mixed legacy and modular runtime loops | Rejected | one orchestrator loop calling typed boundaries |

## File And Module Breakdown

| File/Module | Change Type | Responsibility | Inputs/Outputs |
| --- | --- | --- | --- |
| `app/main.py` | Add | app bootstrap, loop, overlay | frame -> pipeline -> draw |
| `app/tracking/hand_tracker.py` | Add | frame capture + landmark extraction | webcam frame -> hand landmarks |
| `app/gestures/classifier.py` | Add | classify gesture label | landmarks -> gesture |
| `app/core/dispatcher.py` | Add | control toggle, cooldown, action dispatch | gesture -> controller method call |
| `app/control/controller.py` | Add | Windows system actions | intent payload -> OS event |
| `app/config_loader.py` | Add | load/validate config JSON | path -> typed config |
| `scripts/build-exe.ps1` | Add | package app with PyInstaller | repo -> `dist/WebcamGestureControl` |
| `scripts/install.ps1` | Add | install packaged app to user profile | `dist/*` -> `%LOCALAPPDATA%/Programs/*` |
| `scripts/uninstall.ps1` | Add | remove installed app and shortcuts | installed app -> deleted artifacts |

## Dependency Direction

- Allowed direction: `main -> (tracking, classifier, dispatcher, overlay)` and `dispatcher -> controller`.
- Disallowed: controller importing classifier/tracking modules.

## Use-Case Coverage Matrix

| use_case_id | Requirement | Use Case | Runtime Call Stack Section |
| --- | --- | --- | --- |
| UC-001 | R-001 | Capture frame and landmarks | UC-001 |
| UC-002 | R-002 | Classify hand gesture | UC-002 |
| UC-003 | R-003 | Resolve gesture to action intent | UC-003 |
| UC-004 | R-004 | Execute OS action | UC-004 |
| UC-005 | R-007 | Toggle control mode | UC-005 |
| UC-006 | R-008 | Build executable bundle | UC-006 |
| UC-007 | R-009 | Install and launch app from shortcut | UC-007 |

## Change Traceability To Implementation Plan

| Change ID | Implementation Plan Task(s) | Verification | Status |
| --- | --- | --- | --- |
| C-001..C-012 | T-01..T-09 | Unit + integration-style tests + packaging checks | Planned |
