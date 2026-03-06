# Webcam Gesture Control (Windows)

## Overview

This app maps webcam hand gestures to Windows desktop controls with a safety toggle.

## Implemented Gestures

| Gesture | Action |
| --- | --- |
| `fist` | Toggle control mode on/off |
| `pointer` | Move mouse pointer |
| `pinch` | Left click |
| `two_finger_scroll` | Scroll |
| `open_palm` | Media play/pause |
| `v_sign` | Alt+Tab app switch |

## Run

1. Install dependencies:
   - `python -m pip install -r requirements.txt`
2. Start app:
   - `python -m app.main`
3. Exit:
   - press `q`

## Build Executable

1. Build bundle:
   - `powershell -ExecutionPolicy Bypass -File .\scripts\build-exe.ps1 -Clean`
2. Expected output:
   - `dist\WebcamGestureControl\WebcamGestureControl.exe`

## Install Executable

1. Install app and shortcuts:
   - `powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1`
2. Installation location:
   - `%LOCALAPPDATA%\Programs\WebcamGestureControl`
3. Launch options:
   - Desktop shortcut: `Webcam Gesture Control`
   - Start Menu shortcut: `Webcam Gesture Control`

## Uninstall

- `powershell -ExecutionPolicy Bypass -File .\scripts\uninstall.ps1`

## Config

Edit `app/config/actions.json`:

- `gesture_action_map`: gesture-to-action mapping
- `cooldown_ms`: per-action cooldown to avoid accidental retriggers
- `smoothing`: pointer smoothing factor
- `scroll_scale`: multiplies scroll velocity

## Notes

- Controls start disabled by default; make a `fist` gesture to enable output.
- The overlay shows control state, gesture label, last action, and FPS.
- OpenCV OpenCL is enabled at startup when available, and overlay shows `OpenCL: ON/OFF`.
- Tests cover classifier and dispatch logic without requiring webcam hardware.
