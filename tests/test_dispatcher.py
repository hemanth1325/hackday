import unittest

from app.core.dispatcher import DispatcherConfig, GestureDispatcher
from app.models import HandObservation, Point


class FakeController:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def execute(self, action_id: str, observation: HandObservation) -> None:
        self.calls.append(action_id)


def _observation() -> HandObservation:
    return HandObservation(landmarks=[Point(0.5, 0.5)] * 21, pointer=Point(0.5, 0.5), scroll_velocity=0.2)


class GestureDispatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = FakeController()
        self.dispatcher = GestureDispatcher(
            DispatcherConfig(
                gesture_action_map={
                    "pointer": "move_pointer",
                    "pinch": "left_click",
                    "open_palm": "media_toggle",
                    "v_sign": "app_switch",
                    "fist": "toggle_control",
                },
                cooldown_ms={
                    "move_pointer": 0,
                    "left_click": 300,
                    "media_toggle": 1000,
                    "app_switch": 1000,
                    "toggle_control": 500,
                },
                control_enabled=False,
            ),
            controller=self.controller,
        )

    def test_toggle_enables_and_disables_control(self) -> None:
        obs = _observation()
        first = self.dispatcher.dispatch("fist", obs, 1000)
        self.assertTrue(first.executed)
        self.assertTrue(self.dispatcher.control_enabled)

        second = self.dispatcher.dispatch("pointer", obs, 1100)
        self.assertTrue(second.executed)
        self.assertIn("move_pointer", self.controller.calls)

        third = self.dispatcher.dispatch("fist", obs, 1600)
        self.assertTrue(third.executed)
        self.assertFalse(self.dispatcher.control_enabled)

    def test_action_blocked_when_control_disabled(self) -> None:
        obs = _observation()
        result = self.dispatcher.dispatch("pinch", obs, 1000)
        self.assertFalse(result.executed)
        self.assertEqual([], self.controller.calls)

    def test_cooldown_prevents_retrigger(self) -> None:
        obs = _observation()
        self.dispatcher.dispatch("fist", obs, 1000)  # enable
        first = self.dispatcher.dispatch("pinch", obs, 1010)
        second = self.dispatcher.dispatch("pinch", obs, 1200)
        third = self.dispatcher.dispatch("pinch", obs, 1400)
        self.assertTrue(first.executed)
        self.assertFalse(second.executed)
        self.assertTrue(third.executed)
        self.assertEqual(["left_click", "left_click"], [c for c in self.controller.calls if c == "left_click"])


if __name__ == "__main__":
    unittest.main()
