import unittest

from app.gestures.classifier import GestureClassifier
from app.models import Point


def _blank_landmarks() -> list[Point]:
    landmarks = [Point(0.5, 0.8) for _ in range(21)]
    landmarks[4] = Point(0.15, 0.8)
    return landmarks


def _set_finger_up(landmarks: list[Point], tip: int, pip: int, x: float) -> None:
    landmarks[pip] = Point(x, 0.62)
    landmarks[tip] = Point(x, 0.35)


def _set_finger_down(landmarks: list[Point], tip: int, pip: int, x: float) -> None:
    landmarks[pip] = Point(x, 0.55)
    landmarks[tip] = Point(x, 0.78)


class GestureClassifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.classifier = GestureClassifier()

    def test_recognizes_pinch(self) -> None:
        landmarks = _blank_landmarks()
        landmarks[4] = Point(0.48, 0.42)
        landmarks[8] = Point(0.50, 0.43)
        result = self.classifier.classify(landmarks)
        self.assertEqual("pinch", result.name)

    def test_recognizes_pointer(self) -> None:
        landmarks = _blank_landmarks()
        _set_finger_up(landmarks, 8, 6, 0.46)
        _set_finger_down(landmarks, 12, 10, 0.52)
        _set_finger_down(landmarks, 16, 14, 0.58)
        _set_finger_down(landmarks, 20, 18, 0.64)
        result = self.classifier.classify(landmarks)
        self.assertEqual("pointer", result.name)

    def test_recognizes_v_sign(self) -> None:
        landmarks = _blank_landmarks()
        _set_finger_up(landmarks, 8, 6, 0.35)
        _set_finger_up(landmarks, 12, 10, 0.60)
        _set_finger_down(landmarks, 16, 14, 0.68)
        _set_finger_down(landmarks, 20, 18, 0.76)
        result = self.classifier.classify(landmarks)
        self.assertEqual("v_sign", result.name)

    def test_recognizes_two_finger_scroll(self) -> None:
        landmarks = _blank_landmarks()
        _set_finger_up(landmarks, 8, 6, 0.45)
        _set_finger_up(landmarks, 12, 10, 0.50)
        _set_finger_down(landmarks, 16, 14, 0.62)
        _set_finger_down(landmarks, 20, 18, 0.70)
        result = self.classifier.classify(landmarks)
        self.assertEqual("two_finger_scroll", result.name)

    def test_recognizes_open_palm(self) -> None:
        landmarks = _blank_landmarks()
        _set_finger_up(landmarks, 8, 6, 0.42)
        _set_finger_up(landmarks, 12, 10, 0.50)
        _set_finger_up(landmarks, 16, 14, 0.58)
        _set_finger_up(landmarks, 20, 18, 0.66)
        result = self.classifier.classify(landmarks)
        self.assertEqual("open_palm", result.name)

    def test_recognizes_fist(self) -> None:
        landmarks = _blank_landmarks()
        _set_finger_down(landmarks, 8, 6, 0.46)
        _set_finger_down(landmarks, 12, 10, 0.54)
        _set_finger_down(landmarks, 16, 14, 0.62)
        _set_finger_down(landmarks, 20, 18, 0.70)
        result = self.classifier.classify(landmarks)
        self.assertEqual("fist", result.name)


if __name__ == "__main__":
    unittest.main()
