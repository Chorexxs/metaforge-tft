import logging
from typing import Any

import mss
import numpy as np
from PIL import Image

from backend.ocr.coords import SCREEN_SCALE, Coords

logger = logging.getLogger(__name__)


class ScreenReader:
    def __init__(self) -> None:
        self._sct = mss.mss()

    def _capture_region(self, coord) -> Image.Image:
        x = int(coord.x * SCREEN_SCALE)
        y = int(coord.y * SCREEN_SCALE)
        w = int(coord.width * SCREEN_SCALE)
        h = int(coord.height * SCREEN_SCALE)

        screenshot = self._sct.grab({"left": x, "top": y, "width": w, "height": h})
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return img

    def _count_color_pixels(self, img: Image.Image, color_range: tuple) -> int:
        arr = np.array(img)
        h, w, _ = arr.shape

        r_min, r_max = color_range[0]
        g_min, g_max = color_range[1]
        b_min, b_max = color_range[2]

        mask = (
            (arr[:, :, 0] >= r_min)
            & (arr[:, :, 0] <= r_max)
            & (arr[:, :, 1] >= g_min)
            & (arr[:, :, 1] <= g_max)
            & (arr[:, :, 2] >= b_min)
            & (arr[:, :, 2] <= b_max)
        )
        return int(np.sum(mask))

    def get_gold(self) -> int:
        img = self._capture_region(Coords.GOLD)

        gold_icon = ((200, 255), (170, 220), (0, 80))
        white_text = ((200, 255), (200, 255), (200, 255))

        gold_pixels = self._count_color_pixels(img, gold_icon)
        white_pixels = self._count_color_pixels(img, white_text)

        total_pixels = gold_pixels + white_pixels
        logger.debug("gold_pixels", gold=gold_pixels, white=white_pixels, total=total_pixels)

        if total_pixels < 20:
            return 0
        elif total_pixels < 100:
            return int(total_pixels / 10)
        elif total_pixels < 200:
            return int(total_pixels / 12)
        elif total_pixels < 400:
            return int(total_pixels / 15)
        elif total_pixels < 600:
            return int(total_pixels / 18)
        else:
            return min(100, int(total_pixels / 20))

    def get_hp(self) -> int:
        img = self._capture_region(Coords.HP)

        white_heart = ((200, 255), (200, 255), (200, 255))
        white_text = ((200, 255), (200, 255), (200, 255))

        white_pixels = self._count_color_pixels(img, white_heart) + self._count_color_pixels(
            img, white_text
        )

        logger.debug("hp_pixels", white=white_pixels)

        if white_pixels < 20:
            return 100

        hp_value = min(100, int(white_pixels / 8))

        return max(1, hp_value)

    def get_level(self) -> int:
        img = self._capture_region(Coords.LEVEL)

        blue_text = ((60, 120), (140, 200), (220, 255))
        white_text = ((220, 255), (220, 255), (220, 255))
        orange_text = ((255, 255), (165, 220), (0, 100))

        blue_pixels = self._count_color_pixels(img, blue_text)
        white_pixels = self._count_color_pixels(img, white_text)
        orange_pixels = self._count_color_pixels(img, orange_text)

        total = blue_pixels + white_pixels + orange_pixels
        logger.debug(
            "level_pixels", blue=blue_pixels, white=white_pixels, orange=orange_pixels, total=total
        )

        if total < 30:
            return 1
        elif total < 200:
            return 2
        elif total < 350:
            return 3
        elif total < 500:
            return 4
        elif total < 650:
            return 5
        elif total < 800:
            return 6
        elif total < 950:
            return 7
        elif total < 1100:
            return 8
        elif total < 1250:
            return 9
        elif total < 1400:
            return 10
        return 1

    def get_game_stats(self) -> dict[str, Any]:
        gold = self.get_gold()
        hp = self.get_hp()
        level = self.get_level()

        logger.debug("game_stats", gold=gold, hp=hp, level=level)

        return {
            "gold": gold,
            "hp": hp,
            "level": level,
        }

    def close(self) -> None:
        self._sct.close()


_screen_reader: "ScreenReader | None" = None


def get_screen_reader() -> "ScreenReader":
    global _screen_reader
    if _screen_reader is None:
        try:
            _screen_reader = ScreenReader()
        except Exception as e:
            logger.warning("screen_reader_init_failed", error=str(e))
    return _screen_reader
