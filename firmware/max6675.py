import time
import machine

class MAX6675:
    def __init__(self, sck, cs, so):
        self.sck = machine.Pin(sck, machine.Pin.OUT)
        self.cs = machine.Pin(cs, machine.Pin.OUT)
        self.so = machine.Pin(so, machine.Pin.IN)
        self.cs.value(1)
        self.sck.value(0)

    def readCelsius(self):
        self.cs.value(0)
        time.sleep_us(10)
        
        data = 0
        for i in range(16):
            self.sck.value(1)
            time.sleep_us(10)
            if self.so.value():
                data |= (1 << (15 - i))
            self.sck.value(0)
            time.sleep_us(10)
            
        self.cs.value(1)
        
        if data & 0x4: # Bit 2 is high if thermocouple is open
            return float('nan')
            
        # Bits 3-14 are the temperature data
        temp = (data >> 3) & 0xFFF
        return temp * 0.25
