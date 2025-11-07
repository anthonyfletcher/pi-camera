import math
import threading
from logging import exception
from typing import Optional

from DeviceInterfaces import CameraInterface
from MonoDisplay import MonoDisplayBase
from PixelFonts import PixelFonts
from UIAccess import UIAccessNumericField, UIAccessItem, UIAccessField, UIAccessInterface, UIAccessFunction, \
    UIAccessGraphField, UIAccessListField, UIAccessListFieldPossibleValue


class MonoDisplayElement:
    def __init__(self, mono_display: MonoDisplayBase, x:int, y:int, width:int, height:int):
        self._mono_display = mono_display
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._is_running = False
        self._is_paused = False

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = value
        self._on_moved()

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = value
        self._on_moved()

    @property
    def location(self):
        return self._x, self._y
    @location.setter
    def location(self, value):
        self._x, self._y = value
        self._on_moved()

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, value):
        self._width = value
        self._on_resized()

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, value):
        self._height = value
        self._on_resized()

    @property
    def size(self):
        return self._width, self._height
    @size.setter
    def size(self, value):
        self._width, self._height = value
        self._on_resized()

    def _on_moved(self):
        pass

    def _on_resized(self):
        pass

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def start(self):
        self._is_running = True

    def stop(self):
        self._is_running = False
        self._mono_display.draw_rect_fill(self._x, self._y, self._width, self._height, 0)
        self._mono_display.flush()


class MonoDisplayCameraFeed(MonoDisplayElement):
    def __init__(self, access_display_mode: UIAccessNumericField, mono_display: MonoDisplayBase, camera_interface: CameraInterface, x: int,
                 y: int, width: int, height: int):
        super().__init__(mono_display, x, y, width, height)
        self._access_display_mode = access_display_mode
        self._camera_interface = camera_interface
        self._camera_interface.subscribe_item_update("cam_frame", self._frame_received)
        self._do_recalc()

    def _on_resized(self):
        self._do_recalc()

    def _do_recalc(self):
        self._video_input_w, self._video_input_h = self._camera_interface._camera.preview_configuration.main.size
        self._video_input_h_ratio = self._video_input_h / self._video_input_w
        self._video_input_w_ratio = self._video_input_w / self._video_input_h

        if self.width * self._video_input_h_ratio > self.height:
            self._video_w = int(math.floor(self.height * self._video_input_w_ratio))
            self._video_h = self.height
            self._video_y = 0
            self._video_x = int(math.floor((self.width - self._video_w) / 2))
        else:
            self._video_w = self.width
            self._video_h = int(math.floor(self.width * self._video_input_h_ratio))
            self._video_y = int(math.floor((self.height - self._video_h) / 2))
            self._video_x = 0

    def _frame_received(self, field: UIAccessItem):
        if not self._is_running: return
        if self._is_paused: return
        if not isinstance(field, UIAccessField): return

        display_mode_index = int(self._access_display_mode.get())

        mode = ["floyd", "atkinson", "ordered", "lineart", "edge_dither", "edge_dither", "edge_dither", "adaptive_dither",
         "adaptive_dither", "adaptive_dither"][display_mode_index]
        method = ["", "", "", "", "floyd", "atkinson", "ordered", "floyd", "atkinson", "ordered"][
            display_mode_index]
        self._mono_display.draw_image(field.get(), self._x + self._video_x, self._y + self._video_y, self._video_w, self._video_h, mode=mode,
                                      method=method)
        self._mono_display.flush()


class MonoDisplayUIAccessMenu(MonoDisplayElement):
    def __init__(self, access_menu_items: UIAccessField, mono_display: MonoDisplayBase, access_interfaces: list[UIAccessInterface], x: int,
                 y: int, width: int, font = PixelFonts.sans_serif_57):
        self._font = font
        self._text_gap_h = math.ceil(self._font.height // 5)
        self._scroll_bar_h = 2

        height = (self._text_gap_h * 3) + (self._font.height * 2) + self._scroll_bar_h

        super().__init__(mono_display, x, y, width, height)

        self._access_interfaces: list[UIAccessInterface] = access_interfaces
        self._access_menu_items = access_menu_items
        self._access_menu_items_editor = None
        self._menu_items: list = []
        self._selected_menu_item_index = 0
        self._is_editing = False
        self._function_confirm_selected = False
        self._list_possible_values_selected_index = 0

        self._timer_lock = threading.Lock()
        self._timer = None

        self._menu_items_changed = False
        self._menu_items = self._build_menu_items()
        self._access_menu_items_editor = self._build_menu_item_to_control_items()

        if self._access_menu_items_editor is not None:
            self._menu_items.append(self._access_menu_items_editor)

        if len(self._menu_items) == 0: raise exception(
                "No menu items found. Please define at least one menu item.")

        self._do_recalc()

    def _refresh_menu_items(self):
        self._menu_items.clear()
        self._menu_items = self._build_menu_items()

        if self._access_menu_items_editor is not None:
            self._menu_items.append(self._access_menu_items_editor)

    def _build_menu_items(self):
        menu_items = []

        for name in self._access_menu_items.get():
            for access_interface in self._access_interfaces:
                if access_interface.has_item(name):
                    menu_item = access_interface.get_item(name)
                    if not menu_item == self._access_menu_items:
                        menu_items.append(menu_item)

        return menu_items

    def _build_menu_item_to_control_items(self) -> Optional[UIAccessListField]:
        if self._access_menu_items.can_set:
            menu_possible_values = []
            for access_interface in self._access_interfaces:
                for menu_item in access_interface.get_items():
                    if not menu_item == self._access_menu_items:
                        menu_possible_values.append(UIAccessListFieldPossibleValue(menu_item.name, menu_item.title))
            return UIAccessListField(self._access_menu_items.data_accessor, "int_menu_items", self._access_menu_items.get(), self._access_menu_items.title, menu_possible_values, True, False)
        return None

    def _on_moved(self):
        self._do_recalc()

    def _on_resized(self):
        self._do_recalc()

    def _do_recalc(self):
        self._char_w = math.floor(self.width // (self._font.width + 1)) - 2
        self._arrow_left_x = self.x + 0
        self._arrow_right_x = self.x + (self.width - self._font.width)
        self._text_w = self._width - ((self._font.width + 1) * 2)
        self._text_x = self.x + self._font.width + 1 + math.floor((self._text_w - (self._char_w * (self._font.width + 1))) // 2)
        self._line_1_y = self.y + self._scroll_bar_h + self._text_gap_h
        self._line_2_y = self._line_1_y + self._font.height + self._text_gap_h

    def show_message(self, text:str, time_sec: int = 0):
        self.pause()

        text_w = (self._font.width + 1) * len(text)
        text_x = math.ceil((self.width - text_w) // 2)
        text_y = self.x + math.ceil((self.height - self._font.height) // 2)
        border = 4

        self._mono_display.draw_rect_fill(self.x + text_x - border, self.y + text_y - border, text_w + border + border, self._font.height + border + border, 1)
        self._mono_display.draw_text(self._font, text, self.x + text_x, self.y + text_y, 0)
        self._mono_display.flush()

        if time_sec > 0:
            with self._timer_lock:
                if self._timer is None or not self._timer.is_alive():
                    self._timer = threading.Timer(time_sec, self.clear_message)
                    self._timer.start()

    def clear_message(self):
        self.resume()
        with self._timer_lock:
            self._timer = None

    def move_right(self) -> bool:
        if self._is_editing:
            self._change_value(1)
        else:
            if self._selected_menu_item_index < len(self._menu_items) - 1:
                self._change_selected_menu_item(self._selected_menu_item_index + 1)

        return True

    def move_left(self) -> bool:
        if self._is_editing:
            self._change_value(-1)
        else:
            if self._selected_menu_item_index > 0:
                self._change_selected_menu_item(self._selected_menu_item_index - 1)

        return True

    def press(self) -> bool:
        if self._is_editing:
            menu_item = self._menu_items[self._selected_menu_item_index]

            if isinstance(menu_item, UIAccessFunction):
                if self._function_confirm_selected:
                    menu_item.run()
                self._change_edit_mode(False)
            elif isinstance(menu_item, UIAccessListField):
                self._change_value(0)
            else:
                self._change_edit_mode(False)

            return True
        else:
            return False

    def long_press(self) -> bool:
        menu_item = self._menu_items[self._selected_menu_item_index]

        if self._is_editing:
            if menu_item == self._access_menu_items_editor:
                self._menu_items_changed = True
                self._change_selected_menu_item(0)
            else:
                self._change_edit_mode(False)

            return True
        elif isinstance(menu_item, UIAccessFunction):
            if menu_item.is_enabled():
                self._change_edit_mode(True)

                return True
        elif isinstance(menu_item, UIAccessListField):
            if menu_item.has_possible_values():
                self._change_edit_mode(True)

                return True
        elif isinstance(menu_item, UIAccessNumericField):
            if menu_item.can_set:
                self._change_edit_mode(True)

                return True

        return False

    def start(self):
        super().start()

        self._mono_display.start_animations()
        self._change_selected_menu_item(self._selected_menu_item_index)

    def stop(self):
        super().stop()

        self._mono_display.stop_animations()
        self._change_edit_mode(False)

    def pause(self):
        super().pause()

        self._mono_display.stop_animations()

    def resume(self):
        super().resume()
        self._mono_display.start_animations()
        self._change_selected_menu_item(self._selected_menu_item_index)

    def _change_selected_menu_item(self, value: int):
        if value < 0 or value >= len(self._menu_items): return;

        menu_item = self._menu_items[self._selected_menu_item_index]

        if isinstance(menu_item, UIAccessField):
            menu_item.unsubscribe(self._flush_new_value)

        if self._menu_items_changed:
            self._menu_items_changed = False
            self._refresh_menu_items()

        self._selected_menu_item_index = value
        self._is_editing = False
        self._function_confirm_selected = False
        self._list_possible_values_selected_index = 0

        menu_item = self._menu_items[self._selected_menu_item_index]

        self._draw_background()
        self._draw_title(menu_item)
        self._draw_arrows(self._line_1_y, self._selected_menu_item_index, len(self._menu_items), not self._is_editing)
        self._draw_scroll_bar(self._selected_menu_item_index, len(self._menu_items))

        if isinstance(menu_item, UIAccessGraphField):
            menu_item.subscribe(self._flush_new_value)
        elif isinstance(menu_item, UIAccessField):
            self._draw_item_value(menu_item)
            menu_item.subscribe(self._flush_new_value)

        self._mono_display.flush()

    def _change_edit_mode(self, edit_mode: bool):
        menu_item = self._menu_items[self._selected_menu_item_index]

        if self._is_editing and edit_mode:
            self._clear_arrows(self._line_2_y)

        self._is_editing = edit_mode
        self._draw_arrows(self._line_1_y, self._selected_menu_item_index, len(self._menu_items), not self._is_editing)

        if edit_mode:
            if isinstance(menu_item, UIAccessNumericField):
                if menu_item.has_value_range:
                    value = menu_item.get()
                    self._draw_arrows(self._line_2_y, value - menu_item.value_range[0],
                                      (menu_item.value_range[1] - menu_item.value_range[0]) + 1, True)
            if isinstance(menu_item, UIAccessListField):
                if menu_item.has_possible_values():
                    self._draw_arrows(self._line_2_y, self._list_possible_values_selected_index,
                                      len(menu_item.possible_values), True)
            elif isinstance(menu_item, UIAccessFunction):
                self._draw_confirm(self._function_confirm_selected)
                self._draw_arrows(self._line_2_y, 0 if not self._function_confirm_selected else 1, 2, True)
        else:
            if isinstance(menu_item, UIAccessFunction):
                self._clear_confirm()
            self._clear_arrows(self._line_2_y)

        self._mono_display.flush()

    def _change_value(self, direction: int):
        menu_item = self._menu_items[self._selected_menu_item_index]

        if isinstance(menu_item, UIAccessNumericField):
            if menu_item.has_value_range:
                menu_item.adjust(direction)
                value = menu_item.get()
                self._draw_arrows(self._line_2_y, value - menu_item.value_range[0],
                                  (menu_item.value_range[1] - menu_item.value_range[0]) + 1, True)
        elif isinstance(menu_item, UIAccessFunction):
            self._function_confirm_selected = not self._function_confirm_selected
            self._draw_confirm(self._function_confirm_selected)
            self._draw_arrows(self._line_2_y, 0 if not self._function_confirm_selected else 1, 2, True)
        elif isinstance(menu_item, UIAccessListField):
            if direction == 0:
                print("TOGGLE")
                possible_value = menu_item.possible_values[self._list_possible_values_selected_index]
                menu_item.toggle_possible_value(possible_value)
            elif direction == 1 and self._list_possible_values_selected_index < len(menu_item.possible_values) - 1:
                self._list_possible_values_selected_index += 1
            elif direction == -1 and self._list_possible_values_selected_index > 0:
                self._list_possible_values_selected_index -= 1

            self._draw_arrows(self._line_2_y, self._list_possible_values_selected_index, len(menu_item.possible_values), True)
            self._draw_item_value(menu_item)

        self._mono_display.flush()

    def _flush_new_value(self, item: UIAccessItem):
        self._draw_item_value(item)
        self._mono_display.flush()

    def _draw_background(self):
        self._mono_display.draw_rect_fill(self._x, self._y, self._width, self._height, 0)

    def _draw_title(self, item: UIAccessItem):
        if not self._is_running: return
        if self._is_paused: return

        self._mono_display.remove_animated_text("title")
        self._mono_display.remove_animated_text("value")

        title = item.title + ":"

        if len(title) > self._char_w:
            self._mono_display.add_animated_text("title", self._font, title, self._text_x, self._line_1_y,
                                                 self._char_w, 1)
        else:
            self._mono_display.draw_padded_text(self._font, title, self._text_x, self._line_1_y,
                                                 self._char_w, 1)

    def _draw_scroll_bar(self, index, length):
        if not self._is_running: return
        if self._is_paused: return

        self._mono_display.draw_h_bar(self._x, self._y, self._width, self._scroll_bar_h, 0,
                                      length - 1, index,
                                      index, 0)

    def _draw_item_value(self, item: UIAccessItem):
        if not self._is_running: return
        if self._is_paused: return

        self._mono_display.remove_animated_text("value")

        if isinstance(item, UIAccessGraphField):
            self._mono_display.draw_chart(item.get(), self._text_x, self._line_2_y, self._text_w,
                                          self._font.height, "bar", "avg", 1, border=False)
        elif isinstance(item, UIAccessListField):
            possible_value = item.possible_values[self._list_possible_values_selected_index]

            text = ("[X] " if item.has_possible_value(possible_value) else "[ ] ") + possible_value.title

            if len(text) > self._char_w:
                self._mono_display.add_animated_text("value", self._font, text, self._text_x, self._line_2_y,
                                                     self._char_w, 1)
            else:
                self._mono_display.draw_padded_text(self._font, text, self._text_x, self._line_2_y,
                                                    self._char_w, 1)
        elif isinstance(item, UIAccessField):
            text = item.get_formatted()

            if len(text) > self._char_w:
                self._mono_display.add_animated_text("value", self._font, text, self._text_x, self._line_2_y,
                                                         self._char_w, 1)
            else:
                self._mono_display.draw_padded_text(self._font, text, self._text_x, self._line_2_y,
                                                          self._char_w,1)

    def _draw_arrows(self, y, index, length, active):
        if not self._is_running: return
        if self._is_paused: return

        if index > 0:
            self._draw_arrow(self._arrow_left_x, y, self._font.width, self._font.height, True, active)
        else:
            self._mono_display.draw_rect_fill(self._arrow_left_x, y, self._font.width, self._font.height, 0)

        if index < (length - 1):
            self._draw_arrow(self._arrow_right_x, y, self._font.width, self._font.height, False, active)
        else:
            self._mono_display.draw_rect_fill(self._arrow_right_x, y, self._font.width, self._font.height, 0)

    def _clear_arrows(self, y):
        if not self._is_running: return
        if self._is_paused: return

        self._mono_display.draw_rect_fill(self._arrow_left_x, y, self._font.width, self._font.height, 0)
        self._mono_display.draw_rect_fill(self._arrow_right_x, y, self._font.width, self._font.height, 0)

    def _draw_arrow(self, x, y, w, h, left, active):
        self._mono_display.draw_rect_fill(x, y, w, h, 1 if active else 0)

        inner_x = x + 1
        inner_y = y + 1
        inner_w = w - 2
        inner_h = h - 2

        if left:
            tx1 = inner_x
            ty1 = inner_y + inner_h // 2
            tx2 = inner_x + inner_w - 1
            ty2 = inner_y
            tx3 = inner_x + inner_w - 1
            ty3 = inner_y + inner_h - 1
        else:
            tx1 = inner_x
            ty1 = inner_y
            tx2 = inner_x + inner_w - 1
            ty2 = inner_y + inner_h // 2
            tx3 = inner_x
            ty3 = inner_y + inner_h - 1

        # Draw triangle
        self._mono_display.draw_triangle_fill(tx1, ty1, tx2, ty2, tx3, ty3, 0 if active else 1)

    def _draw_confirm(self, selected: bool):
        if not self._is_running: return
        if self._is_paused: return

        text = ("[N]" if not selected else " N ") + ("[Y]" if selected else " Y ")
        self._mono_display.draw_padded_text(self._font, text, self._text_x, self._line_2_y,
                                            self._char_w, 1)

    def _clear_confirm(self):
        if not self._is_running: return
        if self._is_paused: return

        self._mono_display.draw_padded_text(self._font, "", self._text_x, self._line_2_y,
                                            self._char_w, 1)


