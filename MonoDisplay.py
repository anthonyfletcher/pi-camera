import math
import threading
import datetime
import time
import cv2
import numpy as np

class MonoFontBase:
    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def has_char(self, code: int) -> bool:
        return False

    def get_char(self, code: int) -> np.ndarray:
        pass

class MonoFontASCIICapsBase(MonoFontBase):
    def __init__(self, font_array: list[list[list[int]]]):
        self._font_array = [np.array(glyph, dtype=np.uint8) for glyph in font_array]
        self._font_char_map = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                         26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                         51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 0, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                         44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 64, 65, 66, 67]
        super().__init__(len(font_array[0][0]), len(font_array[0]))

    def has_char(self, code: int) -> bool:
        return 32 <= code < 32 + len(self._font_char_map)

    def get_char(self, code: int) -> np.ndarray:
        if self.has_char(code):
            return self._font_array[self._font_char_map[code - 32]]
        return self._font_array[0]

class MonoFontASCIIBase(MonoFontBase):
    def __init__(self, font_array: list[list[list[int]]]):
        self._font_array = [np.array(glyph, dtype=np.uint8) for glyph in font_array]
        self._font_char_map = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
                               25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
                               48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 0, 64, 65, 66, 67, 68, 69, 70, 71,
                               72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93]
        super().__init__(len(font_array[0][0]), len(font_array[0]))

    def has_char(self, code: int) -> bool:
        return 32 <= code < 32 + len(self._font_char_map)

    def get_char(self, code: int) -> np.ndarray:
        if self.has_char(code):
            return self._font_array[self._font_char_map[code - 32]]
        return self._font_array[0]

class MonoFont57(MonoFontASCIIBase):
    def __init__(self):
        #MonoMinto
        #https://fontstruct.com/fontstructions/show/2161813/monominto
        super().__init__([[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0]],[[0,1,0,1,0],[0,1,0,1,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,1,0,1,0],[0,1,0,1,0],[1,1,1,1,1],[0,1,0,1,0],[1,1,1,1,1],[0,1,0,1,0],[0,1,0,1,0]],[[0,1,1,1,0],[1,0,1,0,1],[1,0,1,0,0],[0,1,1,1,0],[0,0,1,0,1],[1,0,1,0,1],[0,1,1,1,0]],[[1,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0],[1,0,0,0,1]],[[0,1,1,0,0],[1,0,0,1,0],[1,0,0,1,0],[0,1,1,0,0],[1,0,1,0,1],[1,0,0,1,0],[0,1,1,0,1]],[[0,0,1,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,0,1,0]],[[0,1,0,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,0,0,0]],[[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[1,1,1,1,1],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,1,1,1,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0]],[[0,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],[[0,1,1,1,0],[1,0,0,0,1],[1,0,0,1,1],[1,0,1,0,1],[1,1,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[0,0,1,0,0],[0,1,1,0,0],[1,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1]],[[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],[[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,1,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[0,0,0,1,1],[0,0,1,0,1],[0,1,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[0,0,0,0,1],[0,0,0,0,1]],[[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[1,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],[[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,1],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,1,0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,1,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,1,1,1,0],[0,0,0,0,0],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,1,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0]],[[0,1,1,1,0],[1,0,0,0,1],[1,0,1,0,1],[1,0,1,0,1],[1,0,1,1,1],[1,0,0,0,0],[1,1,1,1,1]],[[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],[[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],[[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,1],[0,1,1,1,0]],[[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],[[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],[[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],[[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,1]],[[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],[[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1]],[[0,0,1,1,1],[0,0,0,1,0],[0,0,0,1,0],[0,0,0,1,0],[0,0,0,1,0],[1,0,0,1,0],[0,1,1,0,0]],[[1,0,0,0,1],[1,0,0,1,0],[1,0,1,0,0],[1,1,0,0,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],[[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],[[1,0,0,0,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],[[1,0,0,0,1],[1,0,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,0,1],[1,0,0,0,1]],[[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],[[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[0,1,1,1,0]],[[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],[[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[0,1,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],[[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0]],[[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,1,0,1,1],[1,0,0,0,1]],[[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1],[1,0,0,0,1]],[[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],[[1,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],[[0,0,1,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,1,0]],[[1,0,0,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,1,0,0],[0,0,0,1,0],[0,0,0,0,1],[0,0,0,0,1]],[[0,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,0,0]],[[0,0,1,0,0],[0,1,0,1,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1]],[[0,0,0,0,0],[0,0,0,0,0],[0,1,1,1,0],[0,0,0,0,1],[0,1,1,1,1],[1,0,0,0,1],[0,1,1,1,1]],[[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,0,0,1],[0,1,1,1,0]],[[0,0,0,0,1],[0,0,0,0,1],[0,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,1]],[[0,0,0,0,0],[0,0,0,0,0],[0,1,1,1,0],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,0],[0,1,1,1,1]],[[0,0,0,1,1],[0,0,1,0,0],[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,1,1,1,1],[1,0,0,0,1],[0,1,1,1,1],[0,0,0,0,1],[0,1,1,1,0]],[[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],[[0,0,1,0,0],[0,0,0,0,0],[1,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1]],[[0,0,0,0,1],[0,0,0,0,0],[0,0,1,1,1],[0,0,0,0,1],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,1],[1,0,0,1,0],[1,1,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],[[1,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1]],[[0,0,0,0,0],[0,0,0,0,0],[1,1,0,1,0],[1,0,1,0,1],[1,0,1,0,1],[1,0,1,0,1],[1,0,1,0,1]],[[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],[[0,0,0,0,0],[0,0,0,0,0],[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,1,1,1,1],[1,0,0,0,1],[0,1,1,1,1],[0,0,0,0,1],[0,0,0,0,1]],[[0,0,0,0,0],[0,0,0,0,0],[1,0,1,1,0],[1,1,0,0,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,1,1,1,1],[1,0,0,0,0],[0,1,1,1,0],[0,0,0,0,1],[1,1,1,1,0]],[[0,1,0,0,0],[0,1,0,0,0],[1,1,1,1,0],[0,1,0,0,0],[0,1,0,0,0],[0,1,0,0,1],[0,0,1,1,0]],[[0,0,0,0,0],[0,0,0,0,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],[[0,0,0,0,0],[0,0,0,0,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[1,0,1,0,1],[1,0,1,0,1],[1,0,1,0,1],[1,0,1,0,1],[0,1,0,1,0]],[[0,0,0,0,0],[0,0,0,0,0],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1]],[[0,0,0,0,0],[0,0,0,0,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,1],[0,0,0,0,1],[0,1,1,1,0]],[[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,1,1,1,1]],[[0,0,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,0,1,0]],[[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],[[0,1,0,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,1,1,0,1],[1,0,0,1,0],[0,0,0,0,0],[0,0,0,0,0]]])

INSTANCE_MONOFONT57 = MonoFont57()

class MonoDisplayBase:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.animated_text_refresh_seconds = 0.5
        self.animated_text_start_buffer_seconds = 2
        self.animated_text_end_buffer_seconds = 2
        self.flush_cooldown_seconds = 0
        self._animated_text_register = {}
        self._animated_text_register_lock = threading.Lock()
        self._running = False
        self._flush_lock = threading.Lock()
        self._last_flush = datetime.datetime.min
        self._timer = None

    def power_on(self):
        pass

    def power_off(self):
        pass

    ## --- Pixels ----

    def get_size(self) -> tuple[int, int]:
        return self.width, self.height

    def set_pixel(self, x: int, y: int, col: int):
        pass

    def set_h_pixels(self, x: int, y: int, col_arr: list[int]):
        if y < 0 or y >= self.height or x >= self.width:
            return
        length = min(len(col_arr), self.width - x)
        if length <= 0:
            return

        col_vector = np.array([col_arr[:length]], dtype=np.uint8)
        self.set_pixels_vector(x, y, col_vector)

    def set_v_pixels(self, x: int, y: int, col_arr: list[int]):
        if x < 0 or x >= self.width or y >= self.height:
            return
        length = min(len(col_arr), self.height - y)
        if length <= 0:
            return

        col_vector = np.array([[col] for col in col_arr[:length]], dtype=np.uint8)
        self.set_pixels_vector(x, y, col_vector)

    def set_pixels_vector(self, x: int, y: int, col_vector):
        for dy, row in enumerate(col_vector):
            self.set_h_pixels(x, y + dy, row)

    def flush(self):
        with self._flush_lock:
            now = datetime.datetime.now()
            time_since_last = now - self._last_flush

            if time_since_last.total_seconds() >= self.flush_cooldown_seconds:
                self.do_flush()
                self._last_flush = now
            else:
                if self._timer is None or not self._timer.is_alive():
                    delay = self.flush_cooldown_seconds - time_since_last.total_seconds()
                    self._timer = threading.Timer(delay, self._scheduled_flush)
                    self._timer.start()

    def _scheduled_flush(self):
        with self._flush_lock:
            self.do_flush()
            self._last_flush = datetime.datetime.now()
            self._timer = None  # Reset timer

    def do_flush(self):
        pass

    ## --- Lines ----

    def draw_h_line(self, x: int, y: int, w: int, col: int):
        self.set_h_pixels(x, y, [col] * w)

    def draw_v_line(self, x: int, y: int, h: int, col: int):
        self.set_v_pixels(x, y, [col] * h)

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, col: int):
        if y1 == y2:
            self.draw_h_line(min(x1, x2), y1, abs(x2 - x1) + 1, col)
            return
        if x1 == x2:
            self.draw_v_line(x1, min(y1, y2), abs(y2 - y1) + 1, col)
            return

        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy
        while True:
            self.set_pixel(x1, y1, col)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    ## --- Circles ---

    def draw_circle(self, x0: int, y0: int, radius: int, col: int):
        x = radius
        y = 0
        err = 1 - x

        while x >= y:
            self.set_pixel(x0 + x, y0 + y, col)
            self.set_pixel(x0 + y, y0 + x, col)
            self.set_pixel(x0 - y, y0 + x, col)
            self.set_pixel(x0 - x, y0 + y, col)
            self.set_pixel(x0 - x, y0 - y, col)
            self.set_pixel(x0 - y, y0 - x, col)
            self.set_pixel(x0 + y, y0 - x, col)
            self.set_pixel(x0 + x, y0 - y, col)

            y += 1
            if err <= 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x + 1)

    def draw_circle_fill(self, x0: int, y0: int, radius: int, col: int):
        x = radius
        y = 0
        err = 1 - x

        while x >= y:
            self.draw_h_line(x0 - x, y0 + y, 2 * x + 1, col)
            self.draw_h_line(x0 - x, y0 - y, 2 * x + 1, col)
            self.draw_h_line(x0 - y, y0 + x, 2 * y + 1, col)
            self.draw_h_line(x0 - y, y0 - x, 2 * y + 1, col)

            y += 1
            if err <= 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x + 1)

    ## --- Rectangles ----

    def draw_rect(self, x: int, y: int, w: int, h: int, col: int):
        self.draw_h_line(x, y, w, col)
        self.draw_v_line(x, y, h, col)
        self.draw_v_line(x + w - 1, y, h, col)
        self.draw_h_line(x, y + h - 1, w, col)

    def draw_rect_fill(self, x: int, y: int, w: int, h: int, col: int):
        if w <= 0 or h <= 0:
            return
        if x >= self.width or y >= self.height:
            return

        max_w = min(w, self.width - x)
        max_h = min(h, self.height - y)
        if max_h <= 0 or max_w <= 0:
            return

        block = np.full((max_h, max_w), col, dtype=np.uint8)

        self.set_pixels_vector(x, y, block)

    ## --- Triangles ---

    def draw_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, col: int):
        self.draw_line(x1, y1, x2, y2, col)
        self.draw_line(x2, y2, x3, y3, col)
        self.draw_line(x3, y3, x1, y1, col)

    def draw_triangle_fill(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, col: int):
        pts: list[tuple[int, int]] = sorted([(x1, y1), (x2, y2), (x3, y3)], key=lambda p: p[1])
        (x1, y1), (x2, y2), (x3, y3) = pts

        def edge_interpolate(_y, _x1, _y1, _x2, _y2):
            if _y2 == _y1:
                return _x1
            return _x1 + (_x2 - _x1) * (_y - _y1) / (_y2 - _y1)

        y_start = max(int(math.floor(y1)), 0)
        y_end = min(int(math.ceil(y3)), self.height - 1)

        for y in range(y_start, y_end + 1):
            if y < y2:
                xa = edge_interpolate(y, x1, y1, x2, y2)
                xb = edge_interpolate(y, x1, y1, x3, y3)
            else:
                xa = edge_interpolate(y, x2, y2, x3, y3)
                xb = edge_interpolate(y, x1, y1, x3, y3)

            if xa > xb:
                xa, xb = xb, xa

            x_start = max(int(math.floor(xa)), 0)
            x_end = min(int(math.ceil(xb)), self.width - 1)

            if x_end >= x_start:
                self.draw_h_line(x_start, y, x_end - x_start + 1, col)

    ## --- Chart ---

    def draw_chart(self, values: list[float], x: int, y: int, w: int, h: int,
                   mode: str = "bar", reduce: str = "avg", col: int = 1,
                   zero_line: bool = False, fill: bool = False,
                   smooth: bool = False, border: bool = False):
        values = np.array(values, dtype=np.float32)
        if values.size == 0:
            return

        w = self.width - x if w is None else w
        h = self.height - y if h is None else h
        if w <= 1 or h <= 1:
            return

        n = len(values)

        if smooth and n > 3:
            kernel = np.ones(3) / 3
            values = np.convolve(values, kernel, mode="same")

        if n > w:
            bins = np.linspace(0, n, w + 1, dtype=int)
            if reduce == "sum":
                reduced = np.array([np.sum(values[bins[i]:bins[i + 1]]) for i in range(w)])
            else:  # avg
                reduced = np.array([
                    np.mean(values[bins[i]:bins[i + 1]]) if bins[i + 1] > bins[i] else 0
                    for i in range(w)
                ])
        else:
            xs = np.linspace(0, w - 1, n).astype(int)
            reduced = np.zeros(w, dtype=np.float32)
            reduced[xs] = values

        vmin, vmax = np.min(reduced), np.max(reduced)
        if np.isclose(vmax, vmin):
            vmax = vmin + 1.0
        norm = (reduced - vmin) / (vmax - vmin)

        chart = np.zeros((h, w), dtype=np.uint8)

        if zero_line and vmin < 0 < vmax:
            zero_y = int(h - 1 - ((0 - vmin) / (vmax - vmin)) * (h - 1))
            if 0 <= zero_y < h:
                chart[zero_y, :] = col

        if mode == "bar":
            heights = np.clip((norm * (h - 1)).astype(int), 0, h - 1)
            for i, bh in enumerate(heights):
                if bh > 0:
                    chart[h - bh:, i] = col

        elif mode == "line":
            yvals = np.clip((h - 1 - norm * (h - 1)).astype(int), 0, h - 1)
            last_y = yvals[0]
            for i in range(1, w):
                y0, y1 = last_y, yvals[i]
                step = 1 if y1 > y0 else -1
                for yy in range(y0, y1 + step, step):
                    chart[yy, i] = col
                last_y = y1

            if fill:
                for i, y_line in enumerate(yvals):
                    chart[y_line:, i] = col

        else:
            raise ValueError("mode must be 'bar' or 'line'")

        if border:
            chart[0, :] = col
            chart[-1, :] = col
            chart[:, 0] = col
            chart[:, -1] = col

        self.set_pixels_vector(x, y, chart)

    ## --- Bars ----

    def draw_h_bar(self, x: int, y: int, w: int, h: int, min_value: int, max_value: int, value_start: int, value_end: int, col: int, border: bool = False):
        if border:
            self.draw_rect(x, y, w, h, 1)
            x = x+1
            y = y+1
            w = w-2
            h = h-2

        value_start = value_start
        value_end = value_end
        sections = ((max_value - min_value) + 1)
        factor = w/sections

        start_off = abs(min_value - value_start)
        middle_on = abs((value_end - value_start) + 1)

        start_off_from = x
        start_off_to = start_off_from + math.floor(start_off * factor)
        middle_on_from = start_off_to
        middle_on_to = start_off_to + math.floor(middle_on * factor)
        end_off_from = middle_on_to
        end_off_to = x + w

        self.draw_rect_fill(start_off_from, y, start_off_to - start_off_from, h, 0 if col == 1 else 1)
        self.draw_rect_fill(middle_on_from, y, middle_on_to - middle_on_from, h, col)
        self.draw_rect_fill(end_off_from, y, end_off_to - end_off_from, h, 0 if col == 1 else 1)

    def draw_v_bar(self, x: int, y: int, w: int, h: int, min_value: int, max_value: int, value_start: int, value_end: int, col: int, border: bool = False):
        if border:
            self.draw_rect(x, y, w, h, 1)
            x = x + 1
            y = y + 1
            w = w - 2
            h = h - 2

        value_start = value_start
        value_end = value_end
        sections = ((max_value - min_value) + 1)
        factor = h/sections

        start_off = abs(min_value - value_start)
        middle_on = abs((value_end - value_start) + 1)

        start_off_from = y
        start_off_to = start_off_from + math.floor(start_off * factor)
        middle_on_from = start_off_to
        middle_on_to = start_off_to + math.floor(middle_on * factor)
        end_off_from = middle_on_to
        end_off_to = y + h

        self.draw_rect_fill(x, start_off_from, w, (start_off_to - start_off_from), 0 if col == 1 else 1)
        self.draw_rect_fill(x, middle_on_from, w, (middle_on_to - middle_on_from), col)
        self.draw_rect_fill(x, end_off_from, w, (end_off_to - end_off_from), 0 if col == 1 else 1)

    ## --- Images ----

    def _fix_image(self, image: np.ndarray, x: int, y: int, w: int, h: int, rotate: int=0):
        if not isinstance(image, np.ndarray):
            image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        elif image.ndim == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            image = image.copy()

        return self._fix_image_size(image, w, h, rotate)

    def _fix_image_size(self, image: np.ndarray, w: int, h: int, rotate: int=0):
        if rotate % 360 != 0:
            rot_map = {90: cv2.ROTATE_90_CLOCKWISE,
                       180: cv2.ROTATE_180,
                       270: cv2.ROTATE_90_COUNTERCLOCKWISE}
            image = cv2.rotate(cv2.resize(image, (w, h)), rot_map[rotate])
        else:
            image = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)

        return image

    @staticmethod
    def _floyd_steinberg_dither(img: np.ndarray) -> np.ndarray:
        img = img.astype(np.float32) / 255.0
        h, w = img.shape

        for y in range(h - 1):
            row = img[y]
            next_row = img[y + 1]
            old = row[1:-1]
            new = (old > 0.5).astype(np.float32)
            err = old - new
            row[1:-1] = new
            row[2:] += err * 7 / 16
            next_row[:-2] += err * 3 / 16
            next_row[1:-1] += err * 5 / 16
            next_row[2:] += err * 1 / 16
        img[-1] = (img[-1] > 0.5).astype(np.float32)
        return (img > 0.5).astype(np.uint8)

    @staticmethod
    def _atkinson_dither(img: np.ndarray) -> np.ndarray:
        img = img.astype(np.float32) / 255.0
        h, w = img.shape

        for y in range(h):
            row = img[y]
            new_row = (row > 0.5).astype(np.float32)
            err = (row - new_row) / 8.0
            row[:] = new_row

            if w > 2:
                row[1:-1] += err[:-2]
                row[2:] += err[:-2]

            if y + 1 < h:
                nxt = img[y + 1]
                nxt[:-2] += err[1:-1]
                nxt[1:-1] += err[1:-1]
                nxt[2:] += err[:-2]

            if y + 2 < h:
                img[y + 2, :] += np.pad(err, (0, 0))

        return (img > 0.5).astype(np.uint8)

    @staticmethod
    def _ordered_dither(img: np.ndarray, invert: bool = True) -> np.ndarray:
        img = img.astype(np.float32) / 255.0
        h, w = img.shape
        bayer = np.array([
            [0, 48, 12, 60, 3, 51, 15, 63],
            [32, 16, 44, 28, 35, 19, 47, 31],
            [8, 56, 4, 52, 11, 59, 7, 55],
            [40, 24, 36, 20, 43, 27, 39, 23],
            [2, 50, 14, 62, 1, 49, 13, 61],
            [34, 18, 46, 30, 33, 17, 45, 29],
            [10, 58, 6, 54, 9, 57, 5, 53],
            [42, 26, 38, 22, 41, 25, 37, 21]
        ], dtype=np.float32) / 64.0
        tiled = np.tile(bayer, (h // 8 + 1, w // 8 + 1))[:h, :w]
        out = (img > tiled).astype(np.uint8)
        return 1 - out if invert else out

    def draw_image(self, image: np.ndarray, x: int, y: int, w: int, h: int, rotate: int=0,
                   mode: str="floyd", method:str ="floyd", low_threshold: int=50, high_threshold: int=150):
        """
        mode = 'floyd', 'atkinson', 'ordered', 'lineart',
               'edge_dither', 'adaptive_dither'
        method = 'floyd', 'atkinson', 'ordered' (for edge/adaptive modes)
        """
        image = self._fix_image(image, x, y, w, h, rotate)
        mode = mode.lower()
        method = method.lower()

        dither_map = {
            "floyd": self._floyd_steinberg_dither,
            "atkinson": self._atkinson_dither,
            "ordered": self._ordered_dither
        }

        if mode in dither_map:
            mono = dither_map[mode](image)

        elif mode == "lineart":
            mono = (cv2.Canny(image, low_threshold, high_threshold) > 0).astype(np.uint8)

        elif mode == "edge_dither":
            edges_inv = cv2.bitwise_not(cv2.Canny(image, 100, 200))
            shaded = cv2.bitwise_and(image, image, mask=edges_inv)
            mono = dither_map[method](shaded)

        elif mode == "adaptive_dither":
            adapt = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            adapt = (adapt == 0).astype(np.uint8)
            mono = dither_map[method](adapt * 255)

        else:
            raise ValueError(f"Unknown mode: {mode}")

        self._draw_image_buffer(mono, x, y)

    def _draw_image_buffer(self, img:np.ndarray, x: int, y: int):
        h, w = img.shape
        h = min(h, self.height - y)
        w = min(w, self.width - x)
        if h <= 0 or w <= 0:
            return
        block = img[:h, :w].astype(np.uint8)
        self.set_pixels_vector(x, y, block)

    ## --- Text ----

    @staticmethod
    def _fit_text(text: str, width: int) -> str:
        text = str(text)
        if len(text) > width:
            return text[:width]
        return text

    def draw_centered_text(self, font: MonoFontBase, text: str, x: int, y: int, w: int, col: int, rotate: int=0):
        text = self._fit_text(text, w)
        text_length = len(text)

        add_beginning = math.floor((w - text_length) / 2)
        add_end = w - (add_beginning + text_length)

        full_text = (" " * add_beginning) + text + (" " * add_end)
        self.draw_text(font, full_text, x, y, col, rotate)

    def draw_padded_text(self, font: MonoFontBase, text: str, x: int, y: int, w: int, col: int, rotate: int=0):
        text = self._fit_text(text, w)
        text_length = len(text)

        add_end = w - text_length

        full_text = text + (" " * add_end)
        self.draw_text(font, full_text, x, y, col, rotate)

    def draw_right_aligned_text(self, font: MonoFontBase, text: str, x: int, y: int, w: int, col: int, rotate: int=0):
        text = self._fit_text(text, w)
        text_length = len(text)

        add_beginning = w - text_length

        full_text = (" " * add_beginning) + text
        self.draw_text(font, full_text, x, y, col, rotate)

    def draw_text(self, font: MonoFontBase, text: str, x: int, y: int, col: int, rotate: int=0):
        text = str(text)
        advance = font.width + 1
        width = len(text) * advance
        height = font.height

        buffer = np.zeros((height, width), dtype=np.uint8)
        buf_x = 0

        for ch in text:
            code = ord(ch)
            if font.has_char(code):
                font_char = font.get_char(code)
                glyph = font_char[:font.height, :font.width]
                h, w = glyph.shape
                buffer[0:h, buf_x:buf_x + w] = np.maximum(buffer[0:h, buf_x:buf_x + w], glyph)
            buf_x += advance

        # Apply rotation if needed
        rotate = rotate % 360
        if rotate == 90:
            buffer = cv2.rotate(buffer, cv2.ROTATE_90_CLOCKWISE)
        elif rotate == 180:
            buffer = cv2.rotate(buffer, cv2.ROTATE_180)
        elif rotate == 270:
            buffer = cv2.rotate(buffer, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Convert to display color and draw
        if col == 1:
            col_vector = buffer.astype(np.uint8)  # normal white text
        else:
            col_vector = (1 - buffer).astype(np.uint8)

        self.set_pixels_vector(x, y, col_vector)

    def add_animated_text(self, label: str, font, text: str, x: int, y: int, w: int, col: int):
        with self._animated_text_register_lock:
            if len(text) > w:
                self._animated_text_register[label] = [font, text, x, y, w, col, 0]
            else:
                self.draw_padded_text(font, text, x, y, w, col)

    def remove_animated_text(self, label: str):
        with self._animated_text_register_lock:
            if label in self._animated_text_register:
                del self._animated_text_register[label]

    def remove_all_animated_text(self):
        with self._animated_text_register_lock:
            self._animated_text_register = {}

    def start_animations(self):
        if self._running: return

        thread = threading.Thread(target=self.do_animations, daemon=True)

        self._running = True

        thread.start()

    def do_animations(self):
        while self._running:
            start_frames = math.ceil(self.animated_text_start_buffer_seconds/self.animated_text_refresh_seconds)
            end_frames = math.ceil(self.animated_text_end_buffer_seconds/self.animated_text_refresh_seconds)

            with self._animated_text_register_lock:
                updated = False

                for key, value in self._animated_text_register.items():
                    font, text, x, y, w, col, frame = value
                    max_frames = (len(text) - w) + start_frames + end_frames

                    if frame > max_frames:
                        value[6] = 0
                    else:
                        if frame == 0:
                            self.draw_padded_text(font, text, x, y, w, col)
                            updated = True
                        elif frame > start_frames and frame <= max_frames - end_frames:
                            self.draw_padded_text(font, text[frame-start_frames:], x, y, w, col)
                            updated = True

                        value[6] = frame + 1

                if updated: self.flush()

            time.sleep(self.animated_text_refresh_seconds)

    def stop_animations(self):
        if not self._running: return

        self._running = False

#===========================================================================
# IMPLEMENTATIONS
#===========================================================================

from DriverOLED1in32 import OLED_1in32, OLED_WIDTH, OLED_HEIGHT

class OLEDMonoDisplay1in3(MonoDisplayBase):
    def __init__(self):
        super().__init__(OLED_WIDTH, OLED_HEIGHT)

        self.oled = OLED_1in32()
        self.oled.Init()
        self.oled.clear()
        self.buffer = np.zeros((self.height, self.width), dtype=np.uint8)

    def power_on(self):
        width, height = self.get_size()
        self.draw_rect_fill(0,0, width, height, 0)
        self.flush()

    def power_off(self):
        self.power_on()

    def set_pixel(self, x: int, y: int, col: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y, x] = 1 if col else 0

    def set_h_pixels(self, x: int, y: int, col_arr: list[int]):
        if y < 0 or y >= self.height or x >= self.width:
            return
        w = min(len(col_arr), self.width - x)
        if w <= 0:
            return
        self.buffer[y, x:x + w] = col_arr[:w]

    def set_v_pixels(self, x: int, y: int, col_arr: list[int]):
        if x < 0 or x >= self.width or y >= self.height:
            return
        h = min(len(col_arr), self.height - y)
        if h <= 0:
            return
        self.buffer[y:y + h, x] = col_arr[:h]

    def set_pixels_vector(self, x: int, y: int, col_vector):
        h, w = col_vector.shape
        x_end = min(x + w, self.width)
        y_end = min(y + h, self.height)
        if x >= self.width or y >= self.height or x_end <= x or y_end <= y:
            return
        self.buffer[y:y_end, x:x_end] = col_vector[:y_end - y, :x_end - x]

    def draw_rect_fill(self, x: int, y: int, w: int, h: int, col: int):
        if x >= self.width or y >= self.height or w <= 0 or h <= 0:
            return
        x_end = min(x + w, self.width)
        y_end = min(y + h, self.height)
        self.buffer[y:y_end, x:x_end] = col

    def do_flush(self):
        super().do_flush()
        img = (self.buffer.astype(np.uint8) * 15).clip(0, 15)
        buf = (img[:, ::2] << 4) | img[:, 1::2]
        self.oled.ShowImage(buf.reshape(-1).tolist())

    def test(self):
        self.buffer.fill(1)
        self.flush()