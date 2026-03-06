from __future__ import annotations

from dataclasses import dataclass

from app.models import Point

try:
    import cv2
except ImportError as exc:  # pragma: no cover - runtime dependency
    _cv2_import_error = str(exc)
    cv2 = None

try:
    from mediapipe.python.solutions import hands as mp_hands
except ImportError as exc:  # pragma: no cover - runtime dependency
    _mediapipe_import_error = str(exc)
    mp_hands = None


@dataclass
class TrackerConfig:
    camera_index: int = 0
    max_hands: int = 1
    min_detection_confidence: float = 0.6
    min_tracking_confidence: float = 0.6


class HandTracker:
    def __init__(self, config: TrackerConfig) -> None:
        if cv2 is None or mp_hands is None:
            details = []
            cv2_error = globals().get("_cv2_import_error")
            mediapipe_error = globals().get("_mediapipe_import_error")
            if cv2_error:
                details.append(f"cv2 import failed: {cv2_error}")
            if mediapipe_error:
                details.append(f"mediapipe import failed: {mediapipe_error}")
            detail_text = "; ".join(details) if details else "unknown import error"
            raise RuntimeError(f"OpenCV/MediaPipe runtime import failed ({detail_text}).")

        self._config = config
        self._capture = cv2.VideoCapture(config.camera_index)
        self._mp_hands = mp_hands
        self._hands = self._mp_hands.Hands(
            max_num_hands=config.max_hands,
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence,
        )

    def read_frame(self):
        return self._capture.read()

    def extract_landmarks(self, frame) -> list[Point] | None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self._hands.process(rgb)
        if not result.multi_hand_landmarks:
            return None
        hand_landmarks = result.multi_hand_landmarks[0]
        return [Point(x=lm.x, y=lm.y) for lm in hand_landmarks.landmark]

    def draw_landmarks(self, frame, landmarks) -> None:
        if landmarks is None:
            return
        hand_landmarks = self._mp_hands.HandLandmark
        # Re-run inference result cannot be reconstructed from bare points.
        # Draw a minimal pointer indicator instead.
        index_tip = landmarks[hand_landmarks.INDEX_FINGER_TIP]
        height, width = frame.shape[:2]
        cv2.circle(frame, (int(index_tip.x * width), int(index_tip.y * height)), 8, (0, 255, 0), -1)

    def close(self) -> None:
        if self._capture:
            self._capture.release()
        self._hands.close()
