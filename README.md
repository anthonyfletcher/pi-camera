# Introduction



# Components

* PI: Raspberry Pi Zero 2 W
* Camera module: 64MP Hawk-eye Autofocus Camera Module (B0399)
* Rotor: WaveShare Rotation Sensor (WAV-9533)
* Battery: WaveShare Uninterruptible Power Supply UPS HAT (WAV-19739)
* Display: WaveShare 1.32" OLED Display Module 128x96 (WAV-24777)
* Filter: Kood 27mm UV Filter
* Knob: Anodized Aluminium Machined Knob 20mm

# Models

* Camera_Body.stl: The body of the camera.
* Camera_Front.stl: The front panel of the camera - fixed with 4xM2*6 screws.
* Camera_Button.stl: The power switch of the camera - to be fitted onto the battery hat before installation of the frame
* Camera_Frame.stl: The frame that holds all the components.  After joining the battery hat to the pi (connecting them using the supplied connection bars at the bottom), the frame slips over the top of both (angled from the button side first).  The frame is fixed by 4xM3*6 screws.  The camera is then fixed using 3xM2*4 screws, the rotor is fixed using 2xM2*6 screws and the display is pushed into the top fixings.  The frame is then slid into the camera body.
* Camera_Filler.stl: A filler piece to cover the hole where the rotor is pushed into the camera body.
* Camera_Cover.stl: The cover for the charging port and SD card access.

# Pin Setup
* [GPIO PIN]: [DEVICE]: [DEVICE OUTPUT]
* 1: Display: VCC
* 6: Display: GND
* 13: Display: RES
* 17: Rotor: VCC
* 19: Display: DIN
* 22: Display: DC
* 23: Display: CLK
* 24: Display: CS
* 35: Rotor: SIA
* 37: Rotor: SIB
* 39: Rotor: GND
* 40: Rotor: SW

# SD Setup
* Setup your SD card using Raspberry Pi Imager, installing the lite version of the OS.
* Configure your WIFI connection using raspi-config and follow the instructions
```
sudo raspi-config
```
* Update your OS
```
sudo apt update && sudo apt upgrade -y
```
* Install components
```
sudo apt-get install python3-pip
sudo apt install -y python3-opencv
sudo apt install -y opencv-data
sudo apt-get install -y python3-smbus
sudo apt-get install -y i2c-tools
sudo apt install -y python3-picamera2
```
* Install the drivers for the camera - for the camera above the following code was used:
```
wget -O install_pivariety_pkgs.sh https://github.com/ArduCAM/Arducam-Pivariety-V4L2-Driver/releases/download/install_script/install_pivariety_pkgs.sh
chmod +x install_pivariety_pkgs.sh
./install_pivariety_pkgs.sh -p libcamera_dev
./install_pivariety_pkgs.sh -p libcamera_apps
```
```
sudo nano /boot/firmware/config.txt 
#Find the line: [all], add the following item under it:
dtoverlay=arducam-64mp
```
* Install the drivers for the screen - for the screen above the following code was used:
```
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz 
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
```
* Speed up boot time by disabling some services (you may not have all these services):
```
sudo systemctl disable avahi-daemon.service
sudo systemctl disable triggerhappy.service
```
* Speed up boot time by tuning your config:
```
sudo nano /boot/firmware/config.txt
# Paste the following into your file
# Disable the rainbow splash screen
disable_splash=1
# Set the bootloader delay to 0 seconds. The default is 1s if not specified.
boot_delay=0
# Overclock the SD Card from 50 to 100MHz
# This can only be done with at least a UHS Class 1 card
dtoverlay=sdtweak,overclock_50=100
```
* Speed up boot time after you're done with your camera setup (including disabling wifi):
```
sudo systemctl disable ssh.service
sudo systemctl disable NetworkManager.service
sudo systemctl disable Bluetooth
sudo systemctl disable ModemManager.service
sudo systemctl disable systemd-timesyncd.service
sudo systemctl disable wpa_supplicant.service
sudo systemctl disable sshswitch.service
sudo systemctl disable apparmor.service
sudo systemctl disable cron.service
sudo touch /etc/cloud/cloud-init.disabled
```

# Code

* UIAccess.py: This provides base classes that allow information and functionality to be exposed to the UI.
* DeviceInterfaces.py: This provides friendlier interfaces to the battery, rotor and camera devices.  The battery interface supports INA219 implementations (but could be re-worked for other battery drivers).  The rotor interface supports gpio rotors which have a/b signal for rotation and a signal for pressing the rotor.  The camera interface supports all cameras supported by the PiCamera2 library.
* MonoDisplay.py: This provides a base object for drawing to black and white devices as well as an implementation for the display above.  Support for other displays can be implemented by inheriting the base class and, at minimum overriding the set_pixel and do_flush methods - but for best results implementations should override set_pixels_vector.  Fonts can be created by inheriting one of the MonoFontBase classes - MonoFontASCIIBase and MonoFontASCIICapsBase support outputs from the included FontScraper.exe windows application.
* MonoDisplayElements.py: This provides some basic UI elements including a black and white video feed of a camera and a menu system that can display and adjust information exposed by objects inheriting the UIAccess base classes.
* UI.py: This provides a base class for implementing a camera UI plus an implementation that stacks a video feed on top of a menu system.
* Boot.py: This pulls all the different aspects above together into a working camera.

# Installing

* If you're using the components listed above, you should be able to copy the code files to a folder and launch it:
```
sudo python Boot.py
```
* If not:
  * If you've changed the display, you'll have to create an implementation of the MonoDisplay base class.  You can likely get ChatGPT to do this by providing the MonoDisplay.py file and the source code for the driver.
  * If you've changed the camera, you'll have to change the initialisation of PiCamera2 in the Boot.py file to ensure you're using supported resolutions.
  * If you've changed the rotor, you'll have to change the initialisation of the RotorInterface in the Boot.py file to ensure you're connecting to the correct pins, or you might have to edit the RotorInterface implementation.
  * If you've changed the battery, you'll have to edit the BatteryInterface implementation - or alternatively remove it from the Boot.py if you don't need it.
