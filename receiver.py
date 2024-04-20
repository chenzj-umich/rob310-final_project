from machine import UART,Pin
import time

class Receiver:
    def __init__(self):
        self.uart = UART (0, 57600)
        self.uart.init (baudrate = 57600, bits = 8 , parity = None, stop = 1) #rx = Pin (1), tx = Pin (0))

    def read(self):
        print("Reading...")
        if (self.uart.any()):
            data = self.uart.readline()
            print(f"Received: {data.decode('ascii')}")
            return data.decode('ascii')
    
    def send(self):
        self.uart.write("1")

if __name__ == "__main__":
    rec = Receiver()
    while True:
        rec.send()

            
