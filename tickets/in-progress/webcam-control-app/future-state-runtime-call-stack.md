# Future-State Runtime Call Stacks (Debug-Trace Style)

## Design Basis

- Scope Classification: `Medium`
- Call Stack Version: `v2`
- Requirements: `tickets/in-progress/webcam-control-app/requirements.md` (status `Design-ready`)
- Source Artifact: `tickets/in-progress/webcam-control-app/proposed-design.md`
- Source Design Version: `v2`

## Use Case Index (Stable IDs)

| use_case_id | Source Type | Requirement ID(s) | Use Case Name | Coverage Target |
| --- | --- | --- | --- | --- |
| UC-001 | Requirement | R-001 | Camera frame and landmark acquisition | Primary/Error |
| UC-002 | Requirement | R-002 | Gesture classification | Primary/Error |
| UC-003 | Requirement | R-003, R-006 | Gesture-action mapping with cooldown | Primary/Error |
| UC-004 | Requirement | R-004 | Execute system action | Primary/Error |
| UC-005 | Requirement | R-007 | Toggle control mode gate | Primary/Error |
| UC-006 | Requirement | R-008 | Build packaged executable | Primary/Error |
| UC-007 | Requirement | R-009 | Install and launch packaged app | Primary/Error |

## Use Case: UC-001 Camera frame and landmark acquisition

### Primary Runtime Call Stack

```text
[ENTRY] app/main.py:main()
-> app/main.py:run()
-> app/tracking/hand_tracker.py:HandTracker.read_frame() [IO]
-> app/tracking/hand_tracker.py:HandTracker.extract_landmarks(frame)
```

### Error Path

```text
[ERROR] camera unavailable
app/tracking/hand_tracker.py:HandTracker.read_frame()
-> app/main.py:run() # render runtime error text
```

## Use Case: UC-002 Gesture classification

### Primary Runtime Call Stack

```text
[ENTRY] app/main.py:run()
-> app/gestures/classifier.py:GestureClassifier.classify(landmarks)
```

### Error Path

```text
[ERROR] empty landmarks
app/gestures/classifier.py:GestureClassifier.classify(...)
-> returns "none"
```

## Use Case: UC-003 Gesture-action mapping with cooldown

### Primary Runtime Call Stack

```text
[ENTRY] app/main.py:run()
-> app/core/dispatcher.py:GestureDispatcher.dispatch(gesture, hand_state)
-> app/core/dispatcher.py:_is_allowed(action, timestamp) [STATE]
```

### Error Path

```text
[ERROR] unknown gesture mapping
app/core/dispatcher.py:GestureDispatcher.dispatch(...)
-> returns no-op
```

## Use Case: UC-004 Execute system action

### Primary Runtime Call Stack

```text
[ENTRY] app/core/dispatcher.py:GestureDispatcher.dispatch(...)
-> app/control/controller.py:SystemController.execute(action, hand_state)
-> app/control/controller.py:move_pointer()/left_click()/scroll_vertical()/toggle_media_play_pause()/switch_app()
```

### Error Path

```text
[ERROR] unsupported action id
app/control/controller.py:SystemController.execute(...)
-> raises ValueError handled by dispatch caller
```

## Use Case: UC-005 Toggle control mode gate

### Primary Runtime Call Stack

```text
[ENTRY] app/core/dispatcher.py:GestureDispatcher.dispatch(...)
-> app/core/dispatcher.py:toggle_control branch [STATE]
```

### Error Path

```text
[ERROR] repeated toggle gesture in cooldown window
app/core/dispatcher.py:_is_allowed(...)
-> suppress action and keep prior mode
```

## Use Case: UC-006 Build packaged executable

### Primary Runtime Call Stack

```text
[ENTRY] scripts/build-exe.ps1
-> pyinstaller:main()
-> collect mediapipe/cv2/pyautogui runtime assets [IO]
-> write dist/WebcamGestureControl/WebcamGestureControl.exe [IO]
```

### Error Path

```text
[ERROR] missing dependency or hook failure
pyinstaller:main()
-> build-exe.ps1 exits non-zero and reports error
```

## Use Case: UC-007 Install and launch packaged app

### Primary Runtime Call Stack

```text
[ENTRY] scripts/install.ps1
-> copy dist/WebcamGestureControl -> %LOCALAPPDATA%/Programs/WebcamGestureControl [IO]
-> create Desktop and Start Menu shortcuts [IO]
-> user launches shortcut -> WebcamGestureControl.exe:main() [ENTRY]
```

### Error Path

```text
[ERROR] dist folder missing
scripts/install.ps1
-> exits with message requiring build step first
```
