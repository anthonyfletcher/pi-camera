import cv2
from picamera2 import Picamera2
import math
import threading
import time
import os
import fnmatch
import re
from typing import Optional
from datetime import datetime
from typing import Callable
import numpy as np
from gpiozero import RotaryEncoder, Button
from DriverINA219 import INA219
from UIAccess import UIAccessInterface, UIAccessField, UIAccessNumericField, UIAccessItem, UIAccessGraphField
from collections import deque


class BatteryInterface(UIAccessInterface):
    DEFAULTS = {
        "battery_load_voltage": 0,
        "battery_psu_voltage": 0,
        "battery_shunt_voltage": 0,
        "battery_current": 0,
        "battery_power": 0,
        "battery_level": 0,
        "battery_status": 0,
    }

    TITLES = {
        "battery_load_voltage": "Load Voltage",
        "battery_psu_voltage": "PSU Voltage",
        "battery_shunt_voltage": "Shunt Voltage",
        "battery_current": "Current",
        "battery_power": "Power",
        "battery_level": "Battery Level",
        "battery_status": "Battery Status",
    }

    RANGES = {
        "battery_load_voltage": (0, 99999),
        "battery_psu_voltage": (0, 99999),
        "battery_shunt_voltage": (0, 99999),
        "battery_current": (0, 99999),
        "battery_power": (0, 99999),
        "battery_level": (0, 1),
        "battery_status": (0, 1)
    }

    FORMATTERS = {
        "battery_load_voltage": lambda value: f"{value:.3f} V",
        "battery_psu_voltage": lambda value: f"{value:.3f} V",
        "battery_shunt_voltage": lambda value: f"{value:.3f} V",
        "battery_current": lambda value: f"{value/1000:.3f} A",
        "battery_power": lambda value: f"{value:.3f} W",
        "battery_level": lambda value: f"{value * 100:.0f}%",
        "battery_status": lambda value: "Charging" if value == 1 else "Discharging",
    }

    def __init__(self, battery: INA219):
        super().__init__()

        self._battery = battery
        self._is_running = False
        self._voltage_history = deque(maxlen=10)

        for name in self.TITLES:
            self._register_item(UIAccessNumericField(self, name, self.DEFAULTS[name], self.TITLES[name], self.RANGES[name], 0, self.FORMATTERS[name], False, False))

    def start(self):
        if self._is_running: return

        self._is_running = True

        thread = threading.Thread(target=self._do_processing, daemon=True)

        thread.start()

    def _do_processing(self):
        while self._is_running:
            bus_voltage = self._battery.getBusVoltage_V()
            self._voltage_history.append(bus_voltage)
            shunt_voltage = self._battery.getShuntVoltage_mV() / 1000  # voltage between V+ and V- across the shunt
            current = self._battery.getCurrent_mA()  # current in mA
            power = self._battery.getPower_W()  # power in W
            avg_voltage = sum(self._voltage_history) / len(self._voltage_history)
            battery = self._voltage_to_soc(avg_voltage)
            is_charging = 1 if (bus_voltage + shunt_voltage) > bus_voltage else 0

            for name, value in [
                ("battery_load_voltage", bus_voltage),
                ("battery_psu_voltage", bus_voltage + shunt_voltage),
                ("battery_shunt_voltage", shunt_voltage),
                ("battery_current", current),
                ("battery_power", power),
                ("battery_level", battery),
                ("battery_status", is_charging)
            ]:
                self.get_field(name).override_set(value)

            time.sleep(5)

    @staticmethod
    def _voltage_to_soc(voltage: float):
        if voltage >= 4.2:
            return 1.0
        elif voltage <= 3.0:
            return 0.0
        else:
            # Example linear interpolation (better to use a curve)
            return (voltage - 3.0) / (4.2 - 3.0)

    def stop(self):
        if not self._is_running: return

        self._is_running = False


class RotaryInterface:
    def __init__(self, gpio_sig_a, gpio_sig_b, gpio_button):
        self.rotor = RotaryEncoder(gpio_sig_a, gpio_sig_b, wrap=True)
        self.rotor.steps = 0

        self.last_rotor_steps = 0
        self.last_press_was_held = False

        self.button = Button(gpio_button, pull_up=True)
        self.button.hold_time = 0.5
        self.button.hold_repeat = False

        self.rotor.when_rotated = self.rotor_rotated
        self.button.when_released = self.rotor_short_press
        self.button.when_held = self.rotor_long_press

        self.subscribers = []

    def subscribe(self, func: Callable[[str, int], None]):
        self.subscribers.append(func)

    def unsubscribe(self, func: Callable[[str, int], None]):
        self.subscribers.remove(func)

    def broadcast(self, mode: str, value: int):
        for i in range(len(self.subscribers)):
            self.subscribers[i](mode, value)

    def rotor_rotated(self):
        self.broadcast("rotate", self.rotor.steps - self.last_rotor_steps)

        self.last_rotor_steps = self.rotor.steps

    def rotor_short_press(self):
        if self.last_press_was_held:
            self.last_press_was_held = False
            return

        self.broadcast("press",0)

    def rotor_long_press(self):
        self.last_press_was_held = True
        self.rotor.steps = 0
        self.last_rotor_steps = 0
        self.broadcast("long_press",0)


class CameraConfig(UIAccessInterface):
    DEFAULTS = {
        "cam_brightness": 0,
        "cam_sharpness": 1,
        "cam_contrast": 1,
        "cam_saturation": 1,
        "cam_exposure": 0,
        "cam_white_balance_mode": 0,
        "cam_ae_mode": 0,
        "cam_ae_metering_mode": 0,
        "cam_ae_constraint_mode": 0,
        "cam_noise_reduction_mode": 2,
        "cam_preset": 0
    }

    TITLES = {
        "cam_brightness": "Brightness",
        "cam_sharpness": "Sharpness",
        "cam_contrast": "Contrast",
        "cam_saturation": "Saturation",
        "cam_exposure": "Exposure",
        "cam_white_balance_mode": "White Balance Mode",
        "cam_ae_mode": "Auto Exposure Mode",
        "cam_ae_metering_mode": "Auto Exposure Metering Mode",
        "cam_ae_constraint_mode": "Auto Exposure Constraint Mode",
        "cam_noise_reduction_mode": "Noise Reduction",
        "cam_preset": "Preset",
    }

    RANGES = {
        "cam_brightness": (-1, 1),
        "cam_sharpness": (0, 10),
        "cam_contrast": (0, 10),
        "cam_saturation": (0, 10),
        "cam_exposure": (-3, 3),

        "cam_white_balance_mode": (0, 6),
        "cam_ae_mode": (0, 2),
        "cam_ae_metering_mode": (0, 2),
        "cam_ae_constraint_mode": (0, 2),
        "cam_noise_reduction_mode": (0, 3),
        "cam_preset": (0,7),
    }

    FORMATTERS = {
        "cam_brightness": lambda value: f"{value:+.2g}",
        "cam_sharpness": lambda value: f"{value:+.2g}",
        "cam_contrast": lambda value: f"{value:+.2g}",
        "cam_saturation": lambda value: f"{value:+.2g}",
        "cam_exposure": lambda value: f"{value:+.2g}EV",
        "cam_white_balance_mode": lambda value:
        ["Auto", "Incandescent", "Tungsten", "Fluorescent", "Indoor", "Daylight", "Cloudy"][value],
        "cam_ae_mode": lambda value: ["Normal", "Short", "Long"][value],
        "cam_ae_metering_mode": lambda value: ["Centre", "Spot", "Matrix"][value],
        "cam_ae_constraint_mode": lambda value: ["Normal", "Highlight", "Shadows"][value],
        "cam_noise_reduction_mode": lambda value: ["Off", "Fast", "High Quality", "Minimal"][value],
        "cam_preset": lambda value:
        ["Custom", "Default", "Portrait", "Landscape", "Low light", "Cinematic", "Vivid", "Black and White"][value],
    }

    PRESETS = [
        {
            "cam_brightness": 0,
            "cam_contrast": 1,
            "cam_saturation": 1,
            "cam_sharpness": 1,
            "cam_exposure": 0,
            "cam_white_balance_mode": 0,
            "cam_noise_reduction_mode": 0,
        },
        {
            "cam_brightness": 0.2,
            "cam_contrast": 0.8,
            "cam_saturation": 1.2,
            "cam_sharpness": 2,
            "cam_white_balance_mode": 4,
            "cam_noise_reduction_mode": 2,
        },
        {
            "cam_brightness": 0,
            "cam_contrast": 1.8,
            "cam_saturation": 1.8,
            "cam_sharpness": 4,
            "cam_exposure": 0.3,
            "cam_white_balance_mode": 5,
            "cam_noise_reduction_mode": 1,
        },
        {
            "cam_brightness": 0.4,
            "cam_contrast": 1.2,
            "cam_saturation": 0.8,
            "cam_sharpness": 2,
            "cam_exposure": 1.5,
            "cam_noise_reduction_mode": 2,
        },
        {
            "cam_brightness": -0.2,
            "cam_contrast": 2.5,
            "cam_saturation": 0.8,
            "cam_sharpness": 1,
            "cam_exposure": -0.3,
            "cam_white_balance_mode": 2,
            "cam_noise_reduction_mode": 3,
        },
        {
            "cam_brightness": 0.1,
            "cam_contrast": 2,
            "cam_saturation": 2,
            "cam_sharpness": 5,
            "cam_white_balance_mode": 5,
            "cam_noise_reduction_mode": 0,
        },
        {
            "cam_brightness": 0.1,
            "cam_contrast": 1.5,
            "cam_saturation": 0,
            "cam_sharpness": 3,
            "cam_white_balance_mode": 0,
            "cam_noise_reduction_mode": 0,
        },
    ]

    def __init__(self):
        super().__init__()
        # --- Increments ---
        self.increment_cam_brightness = 0.1
        self.increment_cam_sharpness = 0.5
        self.increment_cam_contrast = 0.5
        self.increment_cam_saturation = 0.5
        self.increment_cam_exposure = 0.25
        self.increment_cam_white_balance_mode = 1
        self.increment_cam_ae_mode = 1
        self.increment_cam_ae_metering_mode = 1
        self.increment_cam_ae_constraint_mode = 1
        self.increment_cam_noise_reduction_mode = 1
        self.increment_cam_preset = 1

        for name in self.TITLES:
            self._register_item(UIAccessNumericField(self, name, self.DEFAULTS[name], self.TITLES[name], self.RANGES[name], getattr(self, "increment_" + name), self.FORMATTERS[name], True, True))

    def _on_item_update(self, item: UIAccessItem):
        if not isinstance(item, UIAccessField): return

        value = item.get()

        if item.name == "cam_preset":
            preset_index = value - 1
            if preset_index >=0 and preset_index < len(self.PRESETS):
                for key, value in self.PRESETS[preset_index].items():
                    if self.has_item(key):
                        self.get_field(key).set_silently(value)
        else:
            self.get_field("cam_preset").set_silently(0)

        super()._on_item_update(item)


class CameraInterface(UIAccessInterface):
    SHUTTER_COUNT_FILE = "/var/cam_shutter_count.txt"

    DEFAULTS = {
        "cam_iso": 0,
        "cam_shutter_speed": 0,
        "cam_focus": 0,
        "cam_temperature": 0,
        "cam_lux": 0,
        "cam_digital_gain": 0,
        "cam_blacks": 0,
        "cam_shadows": 0,
        "cam_midtones": 0,
        "cam_highlights": 0,
        "cam_whites": 0,
        "cam_histogram_tone": 0,
        "cam_histogram_shape": 0,
        "cam_histogram_exposure": 0,
        "cam_histogram_contrast": 0,
    }

    TITLES = {
        "cam_iso": "ISO",
        "cam_shutter_speed": "Shutter Speed",
        "cam_focus": "Focus",
        "cam_temperature": "Temperature",
        "cam_lux": "Lux",
        "cam_digital_gain": "Digital Gain",
        "cam_blacks": "Blacks",
        "cam_shadows": "Shadows",
        "cam_midtones": "Midtones",
        "cam_highlights": "Highlights",
        "cam_whites": "Whites",
        "cam_histogram_tone": "Histogram Tone",
        "cam_histogram_shape": "Histogram Shape",
        "cam_histogram_exposure": "Histogram Exposure",
        "cam_histogram_contrast": "Histogram Contrast",
    }

    RANGES = {
        "cam_iso": (0, 512000),
        "cam_shutter_speed": (0, 60),
        "cam_focus": (0, 11),
        "cam_temperature": (0, 27000),
        "cam_lux": (0, 100000),
        "cam_digital_gain": (0, 1),
        "cam_blacks": (0,1),
        "cam_shadows": (0,1),
        "cam_midtones": (0,1),
        "cam_highlights": (0,1),
        "cam_whites": (0,1),
        "cam_histogram_tone": (0,3),
        "cam_histogram_shape": (0,5),
        "cam_histogram_exposure": (0,8),
        "cam_histogram_contrast": (0,1),
    }

    FORMATTERS = {
        "cam_iso": lambda value: f"{value:.0f}",
        "cam_shutter_speed": lambda value: f"1/{math.ceil(1 / value):.0f} s" if 1 > value > 0 else f"{math.floor(value):.0f} s",
        "cam_focus": lambda value: (
                "infinity" if value == 0 else
                f"{(1/value)*1000:.0f} mm" if (1/value) < 0.1 else
                f"{(1/value)*100:.0f} cm" if (1/value) < 1 else
                f"{(1/value):.2f} m"
            ),
        "cam_temperature": lambda value: f"{value:.0f} K",
        "cam_lux": lambda value: f"{value:.0f} lx",
        "cam_digital_gain": lambda value: f"{value:.2f}",
        "cam_blacks": lambda value: f"{value*100:.0f}%",
        "cam_shadows": lambda value: f"{value * 100:.0f}%",
        "cam_midtones": lambda value: f"{value * 100:.0f}%",
        "cam_highlights": lambda value: f"{value * 100:.0f}%",
        "cam_whites": lambda value: f"{value * 100:.0f}%",
        "cam_histogram": lambda value: "",
        "cam_histogram_tone": lambda value: ["Unknown", "Dark-toned scene", "Bright-toned scene", "Balanced tone"][value],
        "cam_histogram_shape": lambda value: ["Unknown", "U-shaped (bimodal)", "Left-weighted (dark peak)", "Right-weighted (bright peak)", "Mountain-shaped (midtone peak)", "Uniform (flat)"][value],
        "cam_histogram_exposure": lambda value: ["Unknown", "Clipping (blacks and whites)", "Clipping (highlights)", "Clipping (shadows)", "Underexposed", "Overexposed", "Low dynamic range", "Very high dynamic range", "Balanced"][value],
        "cam_histogram_contrast": lambda value: f"{value * 100:.0f}%",
    }

    def __init__(self, config: CameraConfig, camera: Picamera2, photo_file_path: str = "."):
        super().__init__()
        self._is_snapping = False
        self._config = config
        self._camera = camera
        self._photo_file_path = photo_file_path.rstrip("/")
        self._is_running = False
        self._last_shutter_count = None

        for name in self.TITLES:
            self._register_item(UIAccessNumericField(self, name, self.DEFAULTS[name], self.TITLES[name], self.RANGES[name], 0, self.FORMATTERS[name], False, False))

        self._register_item(UIAccessField(self, "cam_snap", False, "Snap", False, False))
        self._register_item(UIAccessGraphField(self, "cam_histogram", [], "Histogram"))
        self._register_item(UIAccessField(self, "cam_frame", [], "Camera Frame", False, False))
        self._register_item(UIAccessNumericField(self, "cam_photo_count", self.get_photo_count(), "Photo count", can_set = False, can_serialize = False))

        self.histogram = []

    def get_photo_count(self) -> int:
        return len(fnmatch.filter(os.listdir(self._photo_file_path), "PIC*.jpg"))

    def get_remaining_photo_space(self) -> int:
        jpg_files = fnmatch.filter(os.listdir(self._photo_file_path), "PIC*.jpg")

        total_size = sum(os.path.getsize(os.path.join(self._photo_file_path, f)) for f in jpg_files if os.path.isfile(os.path.join(self._photo_file_path, f)))

        average_size = total_size / len(jpg_files) if jpg_files else 0

        statvfs = os.statvfs(self._photo_file_path)
        available_space = statvfs.f_frsize * statvfs.f_bavail

        if average_size > 0:
            return int(available_space // average_size)
        else:
            return 0

    def get_shutter_count(self) -> int:
        if not self._last_shutter_count is None:
            return self._last_shutter_count

        count = self._get_shutter_count_from_config()
        if count is None:
            count = self._get_shutter_count_from_folder()

        self._last_shutter_count = count

        return count

    def _get_shutter_count_from_config(self) -> Optional[int]:
        if os.path.exists(CameraInterface.SHUTTER_COUNT_FILE):
            try:
                with open(CameraInterface.SHUTTER_COUNT_FILE, "r") as f:
                    return int(f.read().strip())
            except ValueError:
                pass
        return None

    def _get_shutter_count_from_folder(self):
        folder_path = self._photo_file_path

        pattern = re.compile(r"PIC(\d{7})\.jpg")
        max_number = 0

        for filename in os.listdir(folder_path):
            match = pattern.match(filename)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

        return max_number

    def _increment_shutter_count(self) -> int:
        count = self.get_shutter_count()
        count += 1
        self._set_shutter_count_to_config(count)
        self._last_shutter_count = count
        return count

    def _set_shutter_count_to_config(self, count: int):
        with open(CameraInterface.SHUTTER_COUNT_FILE, "w") as f:
            f.write(str(count))

    # --- Camera methods ---

    def snap(self):
        if not self._is_running: return

        self._is_snapping = True
        self.get_field("cam_snap").override_set(True)
        shutter_count = self._increment_shutter_count()

        time.sleep(0.2)

        self._camera.switch_mode_and_capture_file("still", f"{self._photo_file_path}/PIC{shutter_count:07d}.jpg")

        self.get_field("cam_photo_count").override_set(self.get_photo_count())
        self.get_field("cam_snap").override_set(False)
        self._is_snapping = False

    # --- Service methods ---
    CAMERA_CONTROL_MAP = {
        "cam_brightness": "Brightness",
        "cam_sharpness": "Sharpness",
        "cam_contrast": "Contrast",
        "cam_saturation": "Saturation",
        "cam_exposure": "ExposureValue",
        "cam_white_balance_mode": "AwbMode",
        "cam_ae_mode": "AeExposureMode",
        "cam_ae_metering_mode": "AeMeteringMode",
        "cam_ae_constraint_mode": "AeConstraintMode",
        "cam_noise_reduction_mode": "NoiseReductionMode",
    }

    def start(self):
        if self._is_running: return

        for field_name, camera_control_name in self.CAMERA_CONTROL_MAP.items():
            self._camera.set_controls({camera_control_name: self._config.get_field(field_name).get()})

        self._config.subscribe_item_update("*", self._camera_config_changed)

        self._is_running = True

        thread = threading.Thread(target=self._do_processing, daemon=True)

        thread.start()

    def _camera_config_changed(self, field: UIAccessItem):
        if isinstance(field, UIAccessNumericField) and field.name in self.CAMERA_CONTROL_MAP:
            self._camera.set_controls({self.CAMERA_CONTROL_MAP[field.name]: field.get()})

    def _do_processing(self):
        while self._is_running:
            if self._is_snapping:
                time.sleep(0.25)
                continue

            preview_metadata = self._camera.capture_metadata()

            this_iso = round((round(preview_metadata['AnalogueGain'],0) if preview_metadata['AnalogueGain'] >=1 else round(preview_metadata['AnalogueGain'],1)) * 100)
            this_colour_temperature = round(preview_metadata['ColourTemperature'])
            this_lux = round(preview_metadata['Lux'])
            this_digital_gain = round(preview_metadata['DigitalGain'], 2)
            this_shutter_speed = math.floor((preview_metadata['ExposureTime'] / 1000000) * 1000) / 1000
            this_focus = preview_metadata['LensPosition']

            # Set values
            for name, value in [
                ("cam_iso", this_iso),
                ("cam_temperature", this_colour_temperature),
                ("cam_lux", this_lux),
                ("cam_digital_gain", this_digital_gain),
                ("cam_shutter_speed", this_shutter_speed),
                ("cam_focus", this_focus),
            ]:
                self.get_field(name).override_set(value)

            this_frame = self._camera.capture_array()

            self.get_field("cam_frame").override_set(this_frame)

            this_frame_gray = cv2.cvtColor(this_frame, cv2.COLOR_BGR2GRAY)
            this_histogram = np.asarray(cv2.calcHist([this_frame_gray], [0], None, [256], [0, 256]),
                                        dtype=np.float32).flatten()
            this_histogram = np.clip(this_histogram, 0, np.percentile(this_histogram, 99))
            this_histogram_total: float = np.sum(this_histogram)

            self.get_field("cam_histogram").override_set(this_frame)

            if this_histogram_total > 0:
                this_histogram_percentages = this_histogram / this_histogram_total

                bins = len(this_histogram)

                # Split into tonal regions
                sections = np.array_split(this_histogram_percentages, 10)
                this_histogram_blacks = np.sum(sections[0])
                this_histogram_shadows = np.sum(np.concatenate(sections[1:3]))
                this_histogram_midtones = np.sum(np.concatenate(sections[3:7]))
                this_histogram_highlights = np.sum(np.concatenate(sections[7:9]))
                this_histogram_whites = np.sum(sections[9])

                # Contrast analysis
                this_histogram_contrast = np.std(this_histogram_percentages) / np.mean(this_histogram_percentages)

                # Tone analysis
                temp_weighted_mean = np.sum(this_histogram * np.arange(bins)) / this_histogram_total
                temp_normalized_mean = temp_weighted_mean / 255.0

                if temp_normalized_mean < 0.35:
                    this_histogram_tone = 1
                elif temp_normalized_mean > 0.65:
                    this_histogram_tone = 2
                else:
                    this_histogram_tone = 3

                # Shape analysis
                temp_hist_norm = this_histogram / np.max(this_histogram) if np.max(this_histogram) > 0 else this_histogram
                temp_smooth = np.convolve(temp_hist_norm, np.ones(11) / 11, mode="same")
                temp_samples = np.linspace(0, 1, bins)
                temp_mean_pos = np.sum(temp_hist_norm * temp_samples) / np.sum(temp_hist_norm)
                temp_std_dev = np.sqrt(np.sum(temp_hist_norm * (temp_samples - temp_mean_pos) ** 2) / np.sum(temp_hist_norm))
                temp_peaks = (np.diff(np.sign(np.diff(temp_smooth))) < 0).sum()

                if temp_peaks >= 2 and temp_smooth[0] > 0.2 and temp_smooth[-1] > 0.2:
                    this_histogram_shape = 1  # U-shape
                elif temp_peaks == 1:
                    this_histogram_shape = 2 if temp_mean_pos < 0.4 else 3 if temp_mean_pos > 0.6 else 4
                elif temp_std_dev < 0.1:
                    this_histogram_shape = 5  # Flat
                else:
                    this_histogram_shape = 0  # Unknown

                # Exposure / dynamic range
                temp_low_end = np.sum(this_histogram_percentages[:8])
                temp_high_end = np.sum(this_histogram_percentages[-8:])
                temp_nonzero = np.where(this_histogram_percentages > 0.001)[0]
                temp_mean_bin = np.sum(this_histogram_percentages * np.arange(bins)) / (bins * np.sum(this_histogram_percentages))

                if temp_high_end > 0.03 and temp_low_end > 0.03:
                    this_histogram_exposure = 1
                elif temp_high_end > 0.03:
                    this_histogram_exposure = 2
                elif temp_low_end > 0.03:
                    this_histogram_exposure = 3
                elif temp_mean_bin < 0.35:
                    this_histogram_exposure = 4
                elif temp_mean_bin > 0.65:
                    this_histogram_exposure = 5
                elif len(temp_nonzero) > 0:
                    dynamic_range_bins = temp_nonzero[-1] - temp_nonzero[0]
                    ratio = dynamic_range_bins / bins
                    if ratio < 0.3:
                        this_histogram_exposure = 6
                    elif ratio > 0.9:
                        this_histogram_exposure = 7
                    else:
                        this_histogram_exposure = 8
                else:
                    this_histogram_exposure = 0

                # Set values
                for name, value in [
                    ("cam_blacks", this_histogram_blacks),
                    ("cam_shadows", this_histogram_shadows),
                    ("cam_midtones", this_histogram_midtones),
                    ("cam_highlights", this_histogram_highlights),
                    ("cam_whites", this_histogram_whites),
                    ("cam_histogram_contrast", this_histogram_contrast),
                    ("cam_histogram_exposure", this_histogram_exposure),
                    ("cam_histogram_shape", this_histogram_shape),
                    ("cam_histogram_tone", this_histogram_tone)
                ]:
                    self.get_field(name).override_set(value)

            time.sleep(0.2)

    def stop(self):
        if not self._is_running: return

        self._is_running = False

        self._config.unsubscribe_item_update("*", self._camera_config_changed)
