import datetime
import threading
import time
import os
import MonoDisplay
from DeviceInterfaces import CameraInterface, RotaryInterface
from MonoDisplay import MonoDisplayBase
from MonoDisplayElements import MonoDisplayElement, MonoDisplayUIAccessMenu, MonoDisplayCameraFeed
from UIAccess import UIAccessInterface, UIAccessNumericField, UIAccessField, UIAccessItem, UIAccessFunction

class UIConfig(UIAccessInterface):
    DEFAULTS = {
        "ui_display_mode": 0,
    }

    TITLES = {
        "ui_display_mode": "Display Mode"
    }

    RANGES = {
        "ui_display_mode": (0, 9),
    }

    FORMATTERS = {
        "ui_display_mode": lambda value: ["Dither (Floyd)", "Dither (Atkinson)", "Dither (Ordered)", "Line art", "Edge Dither (Floyd)", "Edge Dither (Atkinson)", "Edge Dither (ordered)", "Adaptive Dither (Floyd)", "Adaptive Dither (Atkinson)", "Adaptive Dither (ordered)"][value],
    }

    def __init__(self):
        super().__init__()

        for name in self.TITLES:
            self._register_item(UIAccessNumericField(self, name, self.DEFAULTS[name], self.TITLES[name], self.RANGES[name], 1, self.FORMATTERS[name], True, True))

        self._register_item(UIAccessField(self, "ui_menu_fields", ["cam_iso", "cam_shutter_speed", "cam_focus", "cam_histogram", "cam_preset", "cam_brightness", "cam_exposure", "ui_display_mode", "ui_photos", "battery_level", "battery_status", "ui_shutdown"], "Menu Properties", True, True))
        self._register_item(UIAccessField(self, "ui_save_path", ".", "Save Path", False, True))

class UICore(MonoDisplayElement, UIAccessInterface):
    def __init__(self, config: UIConfig, mono_display: MonoDisplayBase, camera_interface: CameraInterface,
                 rotary_interface: RotaryInterface):
        self._config = config
        self._display_w, self._display_h = mono_display.get_size()

        MonoDisplayElement.__init__(self, mono_display, 0, 0, self._display_w, self._display_h)
        UIAccessInterface.__init__(self)

        self._register_item(UIAccessFunction(self, "ui_shutdown", self.shutdown, "Shutdown"))

        self._camera_interface = camera_interface
        self._rotary_interface = rotary_interface
        self._rotary_interface.subscribe(self._rotor_action)

        self._time_last_action = datetime.datetime.now()
        self._is_sleeping = False
        self._is_saving = False


    def shutdown(self, item: UIAccessFunction):
        self.stop()
        os.system('systemctl poweroff')

    def _rotor_action(self, mode: str, value: int):
        pass

    def sleep(self):
        self._is_sleeping = True
        self.stop()

    def wake(self):
        self.start()
        self._is_sleeping = False

    def start(self):
        super().start()

        self._time_last_action = datetime.datetime.now()

        self._mono_display.power_on()
        self._on_start()
        self._camera_interface.start()

        thread = threading.Thread(target=self.do_processing, daemon=True)

        thread.start()

    def _on_start(self):
        pass

    def do_processing(self):
        while self._is_running or self._is_sleeping:
            now = datetime.datetime.now()
            time_since_last = now - self._time_last_action

            if time_since_last.total_seconds() > 30 and not self._is_sleeping:
                self.sleep()
            else:
                self._on_do_processing()

            time.sleep(1)

    def _on_do_processing(self):
        pass

    def stop(self):
        super().stop()

        self._camera_interface.stop()

        time.sleep(0.25)

        self._on_stop()
        self._mono_display.power_off()

    def _on_stop(self):
        pass

class UIImplementation1in32(UICore):
    def __init__(self, config: UIConfig, mono_display: MonoDisplayBase, camera_interface: CameraInterface,
                 rotary_interface: RotaryInterface, access_interfaces: list[UIAccessInterface],
                 font=MonoDisplay.INSTANCE_MONOFONT57):

        super().__init__(config, mono_display, camera_interface, rotary_interface)

        self._camera_interface.subscribe_item_update("cam_snap", self._draw_snap)

        self._access_interfaces: list[UIAccessInterface] = [config, camera_interface, self]
        self._access_interfaces.extend(access_interfaces)
        self._menu = MonoDisplayUIAccessMenu(config.get_field("ui_menu_fields"), self._mono_display, self._access_interfaces, 0, 0, self._display_w, font)
        self._menu.y = self._display_h - self._menu.height
        self._camera = MonoDisplayCameraFeed(config.get_field("ui_display_mode"), self._mono_display, self._camera_interface, 0, 0, self._display_w, self._display_h - (self._menu.height + 1))

    def _on_start(self):
        self._draw_background()
        self._menu.start()
        self._camera.start()

    def _on_stop(self):
        self._camera.stop()
        self._menu.stop()

    def _rotor_action(self, mode: str, value: int):
        if self._is_sleeping:
            self.wake()
            return

        if not self._is_running: return
        if self._is_saving: return

        self._time_last_action = datetime.datetime.now()

        if mode == "rotate":
            if value > 0:
                self._menu.move_right()
            else:
                self._menu.move_left()
        elif mode == "press":
            if not self._menu.press():
                folder_path = str(self._config.get_field("ui_save_path").get()).rstrip("/")
                self._camera_interface.snap()
        elif mode == "long_press":
            self._menu.long_press()

    def _draw_background(self):
        self._mono_display.draw_h_line(0, self._camera.height, self._display_w, 1)

    def _draw_snap(self, field: UIAccessItem):
        if isinstance(field, UIAccessField):
            if field.get():
                self._menu.show_message("[ SNAP ]")
            else:
                self._menu.clear_message()
