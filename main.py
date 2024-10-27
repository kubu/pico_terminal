import sys
from random import random, seed

import network
import requests
from machine import I2C, Pin
from utime import sleep, sleep_us, ticks_cpu, ticks_diff, ticks_us  # type: ignore

from ota import OTAUpdater
from WIFI_CONFIG import PASSWORD, SSID

sys.path.insert(1, "./micropython-ssd1309")
from ssd1309 import Display
from xglcd_font import XglcdFont

firmware_url = "https://raw.githubusercontent.com/kubu/pico_terminal/master/"
ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "main.py")
try:
    ota_updater.download_and_install_update_if_available()
except:
    print("github connection error")

pin = Pin("LED", Pin.OUT)
pin7 = Pin(7, Pin.IN)

pin.on()
sleep(1)
pin.off()

i2c = I2C(0, freq=400000, scl=Pin(5), sda=Pin(4))  # Pico I2C bus 1
display = Display(i2c=i2c, rst=Pin(2), flip=True)

# Connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
sleep(1)

# Connect to your network
wlan.connect(SSID, PASSWORD)
sleep(7)

pin.on()
sleep(1)
pin.off()

#                    'http://localhost:8000/light/stol/on',
#                   'http://localhost:8000/light/stol/off

# Make GET request

STOL_OFF = "http://192.168.8.242:8000/light/przedp/off"
STOL_ON = "http://192.168.8.242:8000/light/przedp/on"

STORAGE = "http://192.168.8.242:8000/storage/"

# response = requests.get(STORAGE)

# #print (response.json())

# res = response.json()

# POWER = res['power']
# ENERGY = res['energy']
# VOLTAGE = res['voltage']
# TEMP = res['temp']
# CURRENT = res['current']
# SWITCH = res['switch']

# #print (f"{power=} {voltage=} {switch=} {current=} {temp=} {energy=}")


############################


def mainmenu():
    global POWER, ENERGY, VOLTAGE, TEMP, CURRENT, SWITCH
    # print("Loading fonts.  Please wait.")

    # font = XglcdFont("/micropython-ssd1309/fonts/Wendy7x8.c", 7, 8)
    # font = XglcdFont("/micropython-ssd1309/fonts/Bally7x9.c", 7, 9)
    # font = XglcdFont("/micropython-ssd1309/fonts/ArcadePix9x11.c", 9, 11)
    # font = XglcdFont("/micropython-ssd1309/fonts/Broadway17x15.c", 17, 15)
    # font = XglcdFont("/micropython-ssd1309/fonts/Robotron7x11.c", 7, 11)
    # font = XglcdFont("/micropython-ssd1309/fonts/Neato5x7.c", 5, 7)
    # font = XglcdFont("/micropython-ssd1309/fonts/NeatoReduced5x7.c", 5, 7)
    font = XglcdFont("/micropython-ssd1309/fonts/FixedFont5x8.c", 5, 8)

    # print("Drawing")

    # display.draw_text(

    # display.present()

    switch = False
    lock = 0
    LOCK_LIMIT = 10
    read = 50
    READ_LIMIT = 50

    while True:
        try:
            if read == READ_LIMIT:
                read = 0
                response = requests.get(STORAGE)

                # print (read, response.json())

                res = response.json()

                POWER = res["power"]
                ENERGY = res["energy"] / 100
                VOLTAGE = res["voltage"] // 10
                TEMP = res["temp"]
                CURRENT = res["current"]
                SWITCH = res["switch"]

            read += 1

            if lock < LOCK_LIMIT:
                lock += 1

            if pin7.value():
                if lock == LOCK_LIMIT:
                    switch = not switch
                    if switch == 0:
                        response = requests.get(STOL_OFF)
                    else:
                        response = requests.get(STOL_ON)
                    lock = 0

            display.draw_text(
                0,
                0,  # display.height // 2 - text_width // 2,
                f"Switch:        {switch} ",
                font,
                rotate=0,
                invert=True,
            )

            # text_width = font.measure_text(t_power)
            line_height = 12
            text_vpos = 0

            text_vpos += line_height

            display.draw_text(
                0,
                text_vpos,  # display.height // 2 - text_width // 2,
                "Temp (C):",
                font,
                rotate=0,
                invert=False,
            )

            display.draw_text(
                90,
                text_vpos,  # display.height // 2 - text_width // 2,
                str(f"{TEMP:.1f}"),
                font,
                rotate=0,
                invert=False,
            )

            text_vpos += line_height + 5

            display.draw_text(
                0,
                text_vpos,  # display.height // 2 - text_width // 2,
                "Power (W):",
                font,
                rotate=0,
                invert=False,
            )

            display.draw_text(
                90,
                text_vpos,  # display.height // 2 - text_width // 2,
                str(POWER) + "  ",
                font,
                rotate=0,
                invert=False,
            )

            text_vpos += line_height
            display.draw_text(
                0,
                text_vpos,  # display.height // 2 - text_width // 2,
                "Voltage (V):",
                font,
                rotate=0,
                invert=False,
            )

            display.draw_text(
                90,
                text_vpos,  # display.height // 2 - text_width // 2,
                str(VOLTAGE),
                font,
                rotate=0,
                invert=False,
            )

            text_vpos += line_height
            display.draw_text(
                0,
                text_vpos,  # display.height // 2 - text_width // 2,
                "Energy (kWh):",
                font,
                rotate=0,
                invert=False,
            )

            display.draw_text(
                90,
                text_vpos,  # display.height // 2 - text_width // 2,
                str(f"{ENERGY:.1f}"),
                font,
                rotate=0,
                invert=False,
            )

            # text_vpos += line_height

            # display.draw_text(
            #     0,
            #     text_vpos,  # display.height // 2 - text_width // 2,
            #     "Current [A]:",
            #     font,
            #     rotate=0,
            #     invert=False,
            # )

            # display.draw_text(
            #     70,
            #     text_vpos,  # display.height // 2 - text_width // 2,
            #     str(CURRENT/1000),
            #     font,
            #     rotate=0,
            #     invert=False,
            # )

            if read == 1 or lock == 1:
                # print ("disp")
                display.present()

            sleep(0.05)  # sleep
        except KeyboardInterrupt:
            break
    pin.off()
    pin7.off()

    display.cleanup()
    # print("Done.")


##
# client.message_callback_add("meter_kom/6/get", on_message_energy)
# client.message_callback_add("meter_kom/7/get", on_message_voltage)
# client.message_callback_add("meter_kom/8/get", on_message_power)
# client.message_callback_add("meter_kom/9/get", on_message_current)
###########################


def blink():
    print("LED starts flashing...")
    while True:
        try:
            pin.toggle()
            sleep(1)  # sleep 1sec
        except KeyboardInterrupt:
            break
    pin.off()
    print("Finished.")


def shapes():
    """Test code."""
    # spi = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(13))
    # display = Display(spi, dc=Pin(4), cs=Pin(5), rst=Pin(2))

    display.draw_rectangle(1, 1, 30, 30)
    display.fill_rectangle(6, 6, 20, 20)

    display.fill_circle(50, 16, 14)
    display.draw_circle(50, 16, 10, invert=True)

    coords = [[106, 0], [106, 60], [70, 11], [127, 30], [70, 49], [106, 0]]
    display.draw_lines(coords)

    display.fill_ellipse(16, 48, 15, 8)
    display.draw_ellipse(16, 48, 8, 15)

    display.fill_polygon(5, 50, 48, 8)
    display.draw_polygon(7, 50, 48, 15)

    display.draw_line(117, 63, 127, 53)
    display.draw_vline(127, 53, 10)
    display.draw_hline(117, 63, 10)

    display.present()

    sleep(10)
    display.cleanup()
    print("Done.")


######################## FONTS


def fonts():
    print("Loading fonts.  Please wait.")
    # bally = XglcdFont("/micropython-ssd1309/fonts/Bally7x9.c", 7, 9)
    rototron = XglcdFont("/micropython-ssd1309/fonts/Robotron13x21.c", 13, 21)
    unispace = XglcdFont("/micropython-ssd1309/fonts/Unispace12x24.c", 12, 24)
    wendy = XglcdFont("/micropython-ssd1309/fonts/Wendy7x8.c", 7, 8)

    print("Drawing fonts")

    text_width = rototron.measure_text("ROTOTRON")
    display.draw_text(display.width // 2 - text_width // 2, 0, "ROTOTRON", rototron)

    text_width = unispace.measure_text("Unispace")
    text_height = unispace.height
    display.draw_text(
        display.width // 2 - text_width // 2,
        display.height - text_height,
        "Unispace",
        unispace,
        invert=True,
        rotate=180,
    )

    text_width = wendy.measure_text("Wendy")
    display.draw_text(
        0, display.height // 2 - text_width // 2, "Wendy", wendy, rotate=90
    )

    display.present()

    sleep(10)
    display.cleanup()
    print("Done.")


#####


class Box(object):
    """Bouncing box."""

    def __init__(self, screen_width, screen_height, size, display):
        """Initialize box.
        Args:
            screen_width (int): Width of screen.
            screen_height (int): Width of height.
            size (int): Square side length.
            display (SSD1351): OLED display object.
        """
        self.size = size
        self.w = screen_width
        self.h = screen_height
        self.display = display

        # Generate non-zero random speeds between -5.0 and 5.0
        seed(ticks_cpu())
        r = random() * 10.0
        self.x_speed = 5.0 - r if r < 5.0 else r - 10.0
        r = random() * 10.0
        self.y_speed = 5.0 - r if r < 5.0 else r - 10.0

        self.x = self.w / 2.0
        self.y = self.h / 2.0
        self.prev_x = self.x
        self.prev_y = self.y

    def update_pos(self):
        """Update box position and speed."""
        x = self.x
        y = self.y
        size = self.size
        w = self.w
        h = self.h
        x_speed = abs(self.x_speed)
        y_speed = abs(self.y_speed)
        self.prev_x = x
        self.prev_y = y

        if x + size >= w - x_speed:
            self.x_speed = -x_speed
        elif x - size <= x_speed + 1:
            self.x_speed = x_speed

        if y + size >= h - y_speed:
            self.y_speed = -y_speed
        elif y - size <= y_speed + 1:
            self.y_speed = y_speed

        self.x = x + self.x_speed
        self.y = y + self.y_speed

    def draw(self):
        """Draw box."""
        x = int(self.x)
        y = int(self.y)
        size = self.size
        prev_x = int(self.prev_x)
        prev_y = int(self.prev_y)
        self.display.fill_rectangle(
            prev_x - size, prev_y - size, size, size, invert=True
        )
        self.display.fill_rectangle(x - size, y - size, size, size)
        self.display.present()


def boxes():
    """Bouncing box."""
    try:

        display.clear()

        sizes = [12, 11, 10, 9, 8, 7]
        boxes = [Box(128, 64, sizes[i], display) for i in range(6)]

        while True:
            timer = ticks_us()
            for b in boxes:
                b.update_pos()
                b.draw()
            # Attempt to set framerate to 30 FPS
            timer_dif = 33333 - ticks_diff(ticks_us(), timer)
            if timer_dif > 0:
                sleep_us(timer_dif)

    except KeyboardInterrupt:
        display.cleanup()


######################### BOUNCING SPRITE


class BouncingSprite(object):
    """Bouncing Sprite."""

    def __init__(self, path, w, h, screen_width, screen_height, speed, display):
        """Initialize sprite.
        Args:
            path (string): Path of sprite image.
            w, h (int): Width and height of image.
            screen_width (int): Width of screen.
            screen_height (int): Width of height.
            size (int): Square side length.
            speed(int): Initial XY-Speed of sprite.
            display (SSD1351): OLED display object.
            color (int): RGB565 color value.
        """
        self.buf = display.load_sprite(path, w, h, invert=True)
        self.w = w
        self.h = h
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.display = display
        self.x_speed = speed
        self.y_speed = speed
        self.x = self.screen_width // 2
        self.y = self.screen_height // 2
        self.prev_x = self.x
        self.prev_y = self.y

    def update_pos(self):
        """Update sprite speed and position."""
        x = self.x
        y = self.y
        w = self.w
        h = self.h
        x_speed = abs(self.x_speed)
        y_speed = abs(self.y_speed)

        if x + w + x_speed >= self.screen_width:
            self.x_speed = -x_speed
        elif x - x_speed < 0:
            self.x_speed = x_speed

        if y + h + y_speed >= self.screen_height:
            self.y_speed = -y_speed
        elif y - y_speed <= 0:
            self.y_speed = y_speed

        self.prev_x = x
        self.prev_y = y

        self.x = x + self.x_speed
        self.y = y + self.y_speed

    def draw(self):
        """Draw sprite."""
        x = self.x
        y = self.y
        prev_x = self.prev_x
        prev_y = self.prev_y
        w = self.w
        h = self.h
        x_speed = abs(self.x_speed)
        y_speed = abs(self.y_speed)

        # Determine direction and remove previous portion of sprite
        if prev_x > x:
            # Left
            self.display.fill_rectangle(x + w, prev_y, x_speed, h, invert=True)
        elif prev_x < x:
            # Right
            self.display.fill_rectangle(x - x_speed, prev_y, x_speed, h, invert=True)
        if prev_y > y:
            # Upward
            self.display.fill_rectangle(prev_x, y + h, w, y_speed, invert=True)
        elif prev_y < y:
            # Downward
            self.display.fill_rectangle(prev_x, y - y_speed, w, y_speed, invert=True)

        self.display.draw_sprite(self.buf, x, y, w, h)
        self.display.present()


def sprite():
    """Bouncing sprite."""
    try:
        display.clear()

        # Load sprite
        saucer = BouncingSprite(
            "micropython-ssd1309/images/saucer_48x26.mono", 48, 26, 128, 64, 1, display
        )

        while True:
            timer = ticks_us()
            saucer.update_pos()
            saucer.draw()
            # Attempt to set framerate to 30 FPS
            timer_dif = 33333 - ticks_diff(ticks_us(), timer)
            if timer_dif > 0:
                sleep_us(timer_dif)

    except KeyboardInterrupt:
        display.cleanup()


#########################


def images():
    display.draw_bitmap(
        "micropython-ssd1309/images/eyes_128x42.mono",
        0,
        display.height // 2 - 21,
        128,
        42,
    )
    display.present()
    sleep(5)

    display.clear_buffers()
    display.draw_bitmap(
        "micropython-ssd1309/images/doggy_jet128x64.mono", 0, 0, 128, 64, invert=True
    )
    display.present()
    sleep(5)

    display.clear_buffers()
    display.draw_bitmap(
        "micropython-ssd1309/images/invaders_48x36.mono", 0, 14, 48, 36, rotate=90
    )
    display.draw_bitmap(
        "micropython-ssd1309/images/invaders_48x36.mono", 40, 14, 48, 36
    )
    display.draw_bitmap(
        "micropython-ssd1309/images/invaders_48x36.mono", 92, 14, 48, 36, rotate=270
    )
    display.present()

    sleep(10)
    display.cleanup()
    print("Done.")


mainmenu()
