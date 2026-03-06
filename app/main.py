from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2

from app.config_loader import load_config
from app.control.controller import SystemController
from app.core.dispatcher import DispatcherConfig, GestureDispatcher
from app.gestures.classifier import ClassifierThresholds, GestureClassifier
from app.models import HandObservation
from app.tracking.hand_tracker import HandTracker, TrackerConfig


def _default_config_path() -> Path:
    if getattr(sys, "frozen", False):
        exe_config = Path(sys.executable).resolve().parent / "app" / "config" / "actions.json"
        if exe_config.exists():
            return exe_config
        bundled_config = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent)) / "app" / "config" / "actions.json"
        return bundled_config
    return Path(__file__).resolve().parent / "config" / "actions.json"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Windows webcam gesture control app.")
    parser.add_argument("--config", type=Path, default=_default_config_path(), help="Path to actions JSON config")
    return parser


def run(config_path: Path) -> None:
    app_config = load_config(config_path)
    cv2.ocl.setUseOpenCL(True)
    opencl_enabled = bool(cv2.ocl.haveOpenCL() and cv2.ocl.useOpenCL())

    tracker = HandTracker(TrackerConfig(camera_index=app_config.camera_index))
    classifier = GestureClassifier(
        ClassifierThresholds(
            pinch_distance=app_config.thresholds.get("pinch_distance", 0.045),
            v_sign_spread=app_config.thresholds.get("v_sign_spread", 0.08),
        )
    )
    controller = SystemController(smoothing=app_config.smoothing, scroll_scale=app_config.scroll_scale)
    dispatcher = GestureDispatcher(
        DispatcherConfig(
            gesture_action_map=app_config.gesture_action_map,
            cooldown_ms=app_config.cooldown_ms,
            control_enabled=app_config.control_starts_enabled,
        ),
        controller=controller,
    )

    prev_index_y = None
    prev_time = time.time()
    fps = 0.0
    last_action = "none"

    try:
        while True:
            ok, frame = tracker.read_frame()
            if not ok:
                print("Camera frame read failed. Check camera availability.")
                break

            landmarks = tracker.extract_landmarks(frame)
            gesture = "none"
            confidence = 0.0

            if landmarks:
                result = classifier.classify(landmarks)
                gesture = result.name
                confidence = result.confidence

                pointer = landmarks[8]
                scroll_velocity = 0.0
                if prev_index_y is not None:
                    scroll_velocity = prev_index_y - pointer.y
                prev_index_y = pointer.y

                observation = HandObservation(landmarks=landmarks, pointer=pointer, scroll_velocity=scroll_velocity)
                dispatch_result = dispatcher.dispatch(gesture, observation, int(time.time() * 1000))
                if dispatch_result.executed and dispatch_result.action:
                    last_action = dispatch_result.action
                tracker.draw_landmarks(frame, landmarks)
            else:
                prev_index_y = None

            now = time.time()
            dt = max(1e-6, now - prev_time)
            fps = 1.0 / dt
            prev_time = now

            _draw_overlay(
                frame=frame,
                control_enabled=dispatcher.control_enabled,
                gesture=gesture,
                confidence=confidence,
                last_action=last_action,
                fps=fps,
                opencl_enabled=opencl_enabled,
            )
            cv2.imshow("Webcam Gesture Control", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
    finally:
        tracker.close()
        cv2.destroyAllWindows()


def _draw_overlay(
    frame,
    control_enabled: bool,
    gesture: str,
    confidence: float,
    last_action: str,
    fps: float,
    opencl_enabled: bool,
) -> None:
    status = "ON" if control_enabled else "OFF"
    lines = [
        f"Control: {status} (toggle with fist)",
        f"Gesture: {gesture} ({confidence:.2f})",
        f"Action: {last_action}",
        f"FPS: {fps:.1f}",
        f"OpenCL: {'ON' if opencl_enabled else 'OFF'}",
        "Press q to quit",
    ]
    y = 30
    for line in lines:
        cv2.putText(frame, line, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2, cv2.LINE_AA)
        y += 28


def main() -> None:
    args = _build_parser().parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
