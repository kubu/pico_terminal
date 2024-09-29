from machine import Pin
from utime import sleep
from WIFI_CONFIG import PASSWORD, SSID

from ota import OTAUpdater

firmware_url = "https://raw.githubusercontent.com/kubu/pico_terminal/master"

ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "main.py")
ota_updater.download_and_install_update_if_available()

pin = Pin("LED", Pin.OUT)

print("LED starts flashing...")
while True:
    try:
        pin.toggle()
        sleep(1)  # sleep 1sec
    except KeyboardInterrupt:
        break
pin.off()
print("Finished.")
