from machine import Pin
from utime import sleep
from WIFI_CONFIG import PASSWORD, SSID

from ota import OTAUpdater

token = "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"
firmware_url = "https://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@raw.githubusercontent.com/kubu/pico_terminal/master"

ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "main.py")
ota_updater.download_and_install_update_if_available()

pin = Pin("LED", Pin.OUT)

print("LED starts flashing...")
while True:
    try:
        pin.toggle()
        sleep(3)  # sleep 1sec
    except KeyboardInterrupt:
        break
pin.off()
print("Finished.")
