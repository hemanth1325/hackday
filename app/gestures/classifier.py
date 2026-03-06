from __future__ import annotations

import math
from dataclasses import dataclass

from app.models import GestureResult, Point


@dataclass(frozen=True)
class ClassifierThresholds:
    pinch_distance: float = 0.045
    v_sign_spread: float = 0.08


class GestureClassifier:
    """Heuristic classifier over 21-point hand landmarks."""

    def __init__(self, thresholds: ClassifierThresholds | None = None) -> None:
        self.thresholds = thresholds or ClassifierThresholds()

    def classify(self, landmarks: list[Point] | None) -> GestureResult:
        if not landmarks or len(landmarks) < 21:
            return GestureResult(name="none", confidence=0.0)

        index_up = self._is_finger_up(landmarks, 8, 6)
        middle_up = self._is_finger_up(landmarks, 12, 10)
        ring_up = self._is_finger_up(landmarks, 16, 14)
        pinky_up = self._is_finger_up(landmarks, 20, 18)

        pinch_distance = self._distance(landmarks[4], landmarks[8])
        if pinch_distance <= self.thresholds.pinch_distance:
            confidence = max(0.55, 1.0 - pinch_distance / max(self.thresholds.pinch_distance, 0.001))
            return GestureResult(name="pinch", confidence=min(confidence, 1.0))

        if index_up and middle_up and not ring_up and not pinky_up:
            spread = abs(landmarks[8].x - landmarks[12].x)
            if spread >= self.thresholds.v_sign_spread:
                return GestureResult(name="v_sign", confidence=0.9)
            return GestureResult(name="two_finger_scroll", confidence=0.82)

        if index_up and not middle_up and not ring_up and not pinky_up:
            return GestureResult(name="pointer", confidence=0.88)

        if index_up and middle_up and ring_up and pinky_up:
            return GestureResult(name="open_palm", confidence=0.86)

        if not index_up and not middle_up and not ring_up and not pinky_up:
            return GestureResult(name="fist", confidence=0.78)

        return GestureResult(name="none", confidence=0.25)

    @staticmethod
    def _is_finger_up(landmarks: list[Point], tip_idx: int, pip_idx: int) -> bool:
        return landmarks[tip_idx].y < landmarks[pip_idx].y

    @staticmethod
    def _distance(a: Point, b: Point) -> float:
        return math.hypot(a.x - b.x, a.y - b.y)
