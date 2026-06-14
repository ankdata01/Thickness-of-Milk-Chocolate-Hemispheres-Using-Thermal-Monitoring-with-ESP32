# ... (previous imports)
import time
from machine import Pin
from max6675 import MAX6675

# Pin Configuration
SCK_PIN = 18
CS_PIN = 5
SO_PIN = 19
RELAY_PIN = 4

sensor = MAX6675(SCK_PIN, CS_PIN, SO_PIN)
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(1) # Start with relay OFF

while True:
    try:
        temp = sensor.readCelsius()
        if str(temp) != "nan":
            print("Temperature: {:.2f} C".format(temp))
    except Exception as e:
        pass
    time.sleep(0.5) # Faster sampling for the host to catch

