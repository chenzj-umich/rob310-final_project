from machine import Pin, ADC
import utime


class ReadIn:
    def __init__(self, pin_adc, alpha, size):
        self.adc_pin = Pin(pin_adc, mode=Pin.IN)
        self.adc = ADC(self.adc_pin)
        # Exponential Moving Average
        self.alpha = alpha
        self.ema = 0
        # General Average
        self.buffer_size = size
        self.readings = [0] * size
        self.readings_ema = [0] * size
        self.index = 0
        self.offset = 0

    def read(self):
        new_reading = self.adc.read_u16() * 3.3 / 65535 - self.offset
        self.ema = self.alpha * new_reading + (1 - self.alpha) * self.ema
        if new_reading < 0.15:
            new_reading = 0
        if self.ema < 0.15:
            self.ema = 0
        self.readings[self.index] = new_reading
        self.readings_ema[self.index] = self.ema
        self.index = (self.index + 1) % self.buffer_size
        
        average = sum(self.readings) / self.buffer_size
        average_ema = sum(self.readings_ema) / self.buffer_size
        voltage = average
        voltage_ema = average_ema
        return new_reading
        
    
    def calibrate(self):
        start = utime.ticks_ms()
        total = 0
        count = 0
        while utime.ticks_diff(utime.ticks_ms(), start) / 1000 < 1:
            total += self.adc.read_u16() * 3.3 / 65535
            count += 1
        self.offset = total / count
        #print(self.offset)
        
if __name__ == "__main__":
    emg_bi = ReadIn(26, 0.5, 10)
    emg_tri = ReadIn(27, 0.5, 10)
    
    sampling_period = 100 # Sampling period in milliseconds (2 samples per second)
    uart = UART(0,57600)
    uart.init(baudrate = 57600, bits = 8, parity = None, stop = 1)
    try:
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
            if volt_diff < 0.01 and volt_diff > -0.01:
                data = "0\n"
            elif volt_diff > 0:
                data = "-1\n"
            elif volt_diff < 0:
                data = "1\n"
            print(f"data sent: {data}")
            print(uart.write(data.encode('utf-8')))
            #uart.flush()
            
            time_spent = utime.ticks_diff(utime.ticks_ms(), start_time)
            utime.sleep_ms(max(0, sampling_period - time_spent))
        
        
    except KeyboardInterrupt:
        print('ctrl+c pressed')