from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.models import DispatchResult, HandObservation


class ControllerProtocol(Protocol):
    def execute(self, action_id: str, observation: HandObservation) -> None:
        ...


@dataclass
class DispatcherConfig:
    gesture_action_map: dict[str, str]
    cooldown_ms: dict[str, int]
    control_enabled: bool = False


class GestureDispatcher:
    def __init__(self, config: DispatcherConfig, controller: ControllerProtocol) -> None:
        self._gesture_action_map = config.gesture_action_map
        self._cooldown_ms = config.cooldown_ms
        self._controller = controller
        self._control_enabled = config.control_enabled
        self._last_action_ts: dict[str, int] = {}

    @property
    def control_enabled(self) -> bool:
        return self._control_enabled

    def dispatch(
        self,
        gesture_name: str,
        observation: HandObservation,
        timestamp_ms: int,
    ) -> DispatchResult:
        action_id = self._gesture_action_map.get(gesture_name)
        if not action_id:
            return DispatchResult(gesture=gesture_name, action=None, executed=False, control_enabled=self._control_enabled)

        if not self._is_allowed(action_id, timestamp_ms):
            return DispatchResult(gesture=gesture_name, action=action_id, executed=False, control_enabled=self._control_enabled)

        if action_id == "toggle_control":
            self._control_enabled = not self._control_enabled
            self._last_action_ts[action_id] = timestamp_ms
            return DispatchResult(gesture=gesture_name, action=action_id, executed=True, control_enabled=self._control_enabled)

        if not self._control_enabled:
            return DispatchResult(gesture=gesture_name, action=action_id, executed=False, control_enabled=False)

        self._controller.execute(action_id, observation)
        self._last_action_ts[action_id] = timestamp_ms
        return DispatchResult(gesture=gesture_name, action=action_id, executed=True, control_enabled=True)

    def _is_allowed(self, action_id: str, timestamp_ms: int) -> bool:
        min_gap = self._cooldown_ms.get(action_id, 0)
        last_ts = self._last_action_ts.get(action_id)
        if last_ts is None:
            return True
        return timestamp_ms - last_ts >= min_gap
