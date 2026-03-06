from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass
class HandObservation:
    landmarks: list[Point]
    pointer: Point | None = None
    scroll_velocity: float = 0.0


@dataclass(frozen=True)
class GestureResult:
    name: str
    confidence: float


@dataclass
class DispatchResult:
    gesture: str
    action: str | None
    executed: bool
    control_enabled: bool


@dataclass
class AppConfig:
    camera_index: int
    control_starts_enabled: bool
    smoothing: float
    scroll_scale: int
    gesture_action_map: dict[str, str]
    cooldown_ms: dict[str, int]
    thresholds: dict[str, float] = field(default_factory=dict)

    @staticmethod
    def from_dict(payload: dict[str, Any]) -> "AppConfig":
        return AppConfig(
            camera_index=int(payload.get("camera_index", 0)),
            control_starts_enabled=bool(payload.get("control_starts_enabled", False)),
            smoothing=float(payload.get("smoothing", 0.25)),
            scroll_scale=int(payload.get("scroll_scale", 900)),
            gesture_action_map=dict(payload.get("gesture_action_map", {})),
            cooldown_ms={k: int(v) for k, v in dict(payload.get("cooldown_ms", {})).items()},
            thresholds={k: float(v) for k, v in dict(payload.get("thresholds", {})).items()},
        )
