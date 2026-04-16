from dataclasses import dataclass


@dataclass
class ScreenCoords:
    x: int
    y: int
    width: int
    height: int

    def to_bbox(self) -> tuple[int, int, int, int]:
        return self.x, self.y, self.x + self.width, self.y + self.height


class Coords:
    HP = ScreenCoords(x=320, y=55, width=180, height=40)
    GOLD = ScreenCoords(x=880, y=1045, width=140, height=45)
    LEVEL = ScreenCoords(x=80, y=1035, width=80, height=40)


SCREEN_SCALE = 1.0
