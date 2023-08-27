# Import necessary modules
from machine import Pin 
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import neopixel
import time

class Pattern:
    def __init__(self, name, pattern):
        self.name = name
        self.pattern = pattern
        self.frameNumber = 0
        
    def update(self, neopixel):
        neopixel.fill((0, 0, 0))
        self.frameNumber += 1
        if self.frameNumber == len(self.pattern):
            self.frameNumber = 0
        frame = self.pattern[self.frameNumber]
        for pixel in frame:
            index = pixel[0]
            color = pixel[1]
            neopixel[index] = color
        neopixel.write()
        time.sleep(0.1)
            
rainbow_pattern = [
    [
        (0, (148, 0, 211)),   # Violet
        (1, (75, 0, 130)),    # Indigo
        (2, (0, 0, 255)),     # Blue
        (3, (0, 255, 0)),     # Green
        (4, (255, 255, 0)),   # Yellow
        (5, (255, 127, 0)),   # Orange
        (6, (255, 0, 0)),     # Red
        (7, (148, 0, 211)),
        (8, (75, 0, 130)),
        (9, (0, 0, 255)),
        (10, (0, 255, 0)),
        (11, (255, 255, 0)),
        (12, (255, 127, 0)),
        (13, (255, 0, 0))
    ],
    [
        (0, (255, 0, 0)),     # Red
        (1, (148, 0, 211)),   # Violet
        (2, (75, 0, 130)),    # Indigo
        (3, (0, 0, 255)),     # Blue
        (4, (0, 255, 0)),     # Green
        (5, (255, 255, 0)),   # Yellow
        (6, (255, 127, 0)),   # Orange
        (7, (255, 0, 0)),
        (8, (148, 0, 211)),
        (9, (75, 0, 130)),
        (10, (0, 0, 255)),
        (11, (0, 255, 0)),
        (12, (255, 255, 0)),
        (13, (255, 127, 0))
    ],
    # Add more frames here as needed
]

# Create a Pattern instance with the rainbow pattern
rainbow = Pattern("Rainbow", rainbow_pattern)

bounce_pattern = [
    [
        (0, (255, 0, 0)),  # Red (LED 1)
        (13, (0, 0, 255))  # Blue (LED 14)
    ],
    [
        (1, (255, 0, 0)),  # Red (LED 2)
        (12, (0, 0, 255))  # Blue (LED 13)
    ],
    [
        (2, (255, 0, 0)),  # Red (LED 3)
        (11, (0, 0, 255))  # Blue (LED 12)
    ],
    [
        (3, (255, 0, 0)),  # Red (LED 4)
        (10, (0, 0, 255))  # Blue (LED 11)
    ],
    [
        (4, (255, 0, 0)),  # Red (LED 5)
        (9, (0, 0, 255))   # Blue (LED 10)
    ],
    [
        (5, (255, 0, 0)),  # Red (LED 6)
        (8, (0, 0, 255))   # Blue (LED 9)
    ],
    [
        (6, (255, 0, 0)),  # Red (LED 7)
        (7, (0, 0, 255))   # Blue (LED 8)
    ],
    [
        (8, (0, 0, 255)),  # Blue (LED 9)
        (5, (255, 0, 0))   # Red (LED 6)
    ],
    [
        (9, (0, 0, 255)),  # Blue (LED 10)
        (4, (255, 0, 0))   # Red (LED 5)
    ],
    [
        (10, (0, 0, 255)),  # Blue (LED 11)
        (3, (255, 0, 0))    # Red (LED 4)
    ],
    [
        (11, (0, 0, 255)),  # Blue (LED 12)
        (2, (255, 0, 0))    # Red (LED 3)
    ],
    [
        (12, (0, 0, 255)),  # Blue (LED 13)
        (1, (255, 0, 0))    # Red (LED 2)
    ],
]

# Create a Pattern instance with the bouncing pattern
bounce = Pattern("Bounce", bounce_pattern)

off = Pattern("Off", [
    [(i, (0, 0, 0)) for i in range(14)]  # All LEDs off
])

idle = Pattern("Idle", [[(0, (0, 255, 0))]])

fade_pattern = []

# Define the gradient colors (e.g., from red to blue)
start_color = (255, 0, 0)  # Red
end_color = (0, 0, 255)    # Blue

# Create frames for the fade pattern
for step in range(14):
    # Calculate the interpolated color for each step
    r = int((start_color[0] * (14 - step) + end_color[0] * step) / 14)
    g = int((start_color[1] * (14 - step) + end_color[1] * step) / 14)
    b = int((start_color[2] * (14 - step) + end_color[2] * step) / 14)
    
    frame = [(i, (r, g, b)) for i in range(14)]  # Set all LEDs to the interpolated color
    fade_pattern.append(frame)
    
for frame in reversed(fade_pattern):
    fade_pattern.append(frame)

# Create a Pattern instance with the fade pattern
fade = Pattern("Fade", fade_pattern)


strip = [
    "0a", "0b",
    "1a", "1b",
    "2a", "2b",
    "3a", "3b",
    "4a", "4b",
    "5a", "5b",
    "6a", "6b"
    ]

def toLEDNumber(code):
    if code.find("a") != -1:
        return int(code[0])*2
    return int(code[0])*2+1



# Create a Bluetooth Low Energy (BLE) object
ble = bluetooth.BLE()

# Create an instance of the BLESimplePeripheral class with the BLE object
sp = BLESimplePeripheral(ble)

pixels = neopixel.NeoPixel(Pin(2, Pin.OUT), 14)

oldData = ""

currentPattern = None

def on_rx(data):
    global oldData, currentPattern
    data = str(data)[2:]
    print("Recieved: ", data, type(data))
    if data != oldData:
        if "rainbow" in data:
            currentPattern = rainbow
        elif "bounce" in data:
            currentPattern = bounce
        elif "off" in data:
            currentPattern = off
        elif "fade" in data:
            currentPattern = fade
        elif "exit" in data:
            currentPattern = -1
        else:
            oldData = data
            red = int(data[0:2], 16)
            green = int(data[2:4], 16)
            blue = int(data[4:6], 16)
            print(red, green, blue)
            pixels.fill((red, green, blue))
            pixels.write()
            
def updatePixels():
    if currentPattern == None:
        return
    currentPattern.update(pixels)
        
while True:
    
    if sp.is_connected():
        if currentPattern == None:
            currentPattern = idle
        sp.on_write(on_rx)
        
    updatePixels()
    


