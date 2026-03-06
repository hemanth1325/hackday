# Investigation Notes

- Ticket: `webcam-control-app`
- Date: `2026-03-06`
- Stage: `1`
- Scope triage: `Medium`

## Current Codebase Snapshot

- Repository has no source code yet.
- No existing architecture constraints from legacy modules.
- This allows a clean-cut module design without compatibility layers.

## Technology Decision Summary

| Area | Selected Option | Why |
| --- | --- | --- |
| Webcam + frame loop | `opencv-python` | Stable camera + overlay APIs for Windows. |
| Hand landmark detection | `mediapipe` | Fast real-time hand landmarks with enough accuracy for gesture mapping. |
| OS actions | `pyautogui` + Windows virtual key via `ctypes` | Cross-action support (mouse/scroll/hotkeys) and native media key event. |
| Test framework | `unittest` | No extra runtime dependency for deterministic logic tests. |
| Packaging | `PyInstaller onedir` | Most reliable for OpenCV/MediaPipe runtime assets on Windows. |

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Webcam permission/camera index mismatch | App appears broken | Configurable camera index with startup error message. |
| False-positive gestures | Unwanted system actions | Gesture confidence thresholds + cooldown + explicit control toggle gesture. |
| Action spam during steady gesture | Repeated triggers | Edge-triggered dispatcher and per-action cooldown timestamps. |
| External deps unavailable in test env | CI/test flakiness | Keep tests on pure logic modules, avoid importing OpenCV/MediaPipe in tests. |
| Frozen executable misses runtime assets | Packaged app fails at startup | Use PyInstaller collect options and config path resolver for frozen mode. |
| Installer permissions in protected folders | Install fails for non-admin users | Install into `%LOCALAPPDATA%\\Programs` to avoid elevation requirement. |

## Scope Triage Rationale

- Medium scope due to multi-module runtime pipeline plus packaging/install workflow and executable verification.
- Delivery now includes installable executable workflow in addition to Python runtime mode.
