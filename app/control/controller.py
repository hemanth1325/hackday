from __future__ import annotations

import ctypes

import pyautogui

from app.models import HandObservation, Point


VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_KEYUP = 0x0002


class SystemController:
    def __init__(self, smoothing: float = 0.25, scroll_scale: int = 900) -> None:
        self._smoothing = max(0.0, min(1.0, smoothing))
        self._scroll_scale = max(1, scroll_scale)
        self._last_mouse: Point | None = None
        pyautogui.FAILSAFE = False

    def execute(self, action_id: str, observation: HandObservation) -> None:
        if action_id == "move_pointer":
            self.move_pointer(observation.pointer)
            return
        if action_id == "left_click":
            pyautogui.click()
            return
        if action_id == "scroll":
            self.scroll_vertical(observation.scroll_velocity)
            return
        if action_id == "media_toggle":
            self.toggle_media_play_pause()
            return
        if action_id == "app_switch":
            pyautogui.hotkey("alt", "tab")
            return
        raise ValueError(f"Unsupported action: {action_id}")

    def move_pointer(self, pointer: Point | None) -> None:
        if pointer is None:
            return
        screen_w, screen_h = pyautogui.size()
        target_x = int(pointer.x * screen_w)
        target_y = int(pointer.y * screen_h)

        if self._last_mouse is None:
            smoothed = Point(float(target_x), float(target_y))
        else:
            smoothed = Point(
                x=self._last_mouse.x + (target_x - self._last_mouse.x) * self._smoothing,
                y=self._last_mouse.y + (target_y - self._last_mouse.y) * self._smoothing,
            )
        self._last_mouse = smoothed
        pyautogui.moveTo(int(smoothed.x), int(smoothed.y), duration=0)

    def scroll_vertical(self, scroll_velocity: float) -> None:
        amount = int(scroll_velocity * self._scroll_scale)
        if amount == 0:
            return
        pyautogui.scroll(amount)

    @staticmethod
    def toggle_media_play_pause() -> None:
        user32 = ctypes.windll.user32
        user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
        user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_KEYUP, 0)
