from machine import Pin, ADC, UART
import utime
from readVoltage import ReadIn
from motor_class import Motor
from encoder import Encoder

class Control:
    def __init__(self):
        self.emg_bi = ReadIn(26, 0.5, 10)
        self.emg_tri = ReadIn(27, 0.5, 10)
        
        
        sampling_period = 100 # Sampling period in milliseconds (2 samples per second)

if __name__ == "__main__":
    emg_bi = ReadIn(26, 0.5, 10)
    emg_tri = ReadIn(27, 0.5, 10)
    enc1 = Encoder(6,7)
    motor1 = Motor(2,14)
    
    sampling_period = 100 # Sampling period in milliseconds (2 samples per second)
    uart = UART(0,57600)
    uart.init(baudrate = 57600, bits = 8, parity = None, stop = 1)
    try:
        print("Welcome using EMG controlled Mbot!")
        print("initializing...1/2")
        emg_bi.calibrate()
        print("initializing...2/2")
        emg_tri.calibrate()
        print("initialization done\n")
        
        while True:
            start_time = utime.ticks_ms()
            volt_bi = emg_bi.read()
            volt_tri = emg_tri.read()
            volt_diff = volt_bi - volt_tri
            #print(f"EMA_bi: {round(volt_bi, 4)} EMA_tri: {round(volt_tri, 4)}")
            print(f"volt_diff: {volt_diff}")
            if volt_diff < 0.1 and volt_diff > -0.1:
                data = "0\n"
                print(f"Stop")
                motor1.set(0)
            elif volt_diff > 0:
                data = "-1\n"
                print(f"Forward")
                motor1.set(0.25)
                #motor1.set(volt_diff/0.5*0.25)
            elif volt_diff < 0:
                data = "1\n"
                print(f"Backward")
                motor1.set(-0.25)
                #motor1.set(volt_diff/0.5*(-0.25))
            #print(f"data sent: {data}")
            #print(uart.write(data.encode('utf-8')))
            #uart.flush()
            time_spent = utime.ticks_diff(utime.ticks_ms(), start_time)
            utime.sleep_ms(max(0, sampling_period - time_spent))
        
        
    except KeyboardInterrupt:
        print('ctrl+c pressed')