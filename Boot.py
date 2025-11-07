# == Imports for camera system ==
from PixelFonts import PixelFonts

from picamera2 import Picamera2, Preview
from libcamera import controls, Transform

from DeviceInterfaces import BatteryInterface, RotaryInterface, CameraConfig, CameraInterface
from DriverINA219 import INA219
from UI import UIConfig, UIImplementation1in32
from MonoDisplay import OLEDMonoDisplay1in3

# == Setup Mono Display ==

mono_display = OLEDMonoDisplay1in3()

# == Setup PiCamera ==

camera = Picamera2()
camera.preview_configuration.main.size = (1280, 720)
camera.preview_configuration.sensor.output_size = (1280, 720)
camera.preview_configuration.main.format = "RGB888"
camera.preview_configuration.transform = Transform(vflip=True, hflip=True)
camera.still_configuration.size = (4624, 3472)
camera.still_configuration.transform = Transform(vflip=True, hflip=True)
camera.start_preview(Preview.NULL)
camera.start()
camera.set_controls({"AfSpeed": 1})
camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})

# == Setup Camera Interface ==
ui_config = UIConfig()
ui_config.load_fields("./ui.cfg", True)

camera_config = CameraConfig()
camera_config.load_fields("./camera.cfg", True)
camera_interface = CameraInterface(camera_config, camera, ui_config.get_field("ui_save_path").get())

# == Setup Rotary Interface ==

rotary_interface = RotaryInterface(19,26,21)

# == Setup Battery Interface ==

battery_interface = BatteryInterface(INA219(addr=0x43))
battery_interface.start()

# == Setup UI ==

ui = UIImplementation1in32(ui_config, mono_display, camera_interface, rotary_interface, [battery_interface, camera_config])

ui.start()

input("")

ui.stop()
battery_interface.stop()
camera.stop()

mono_display.power_off()



