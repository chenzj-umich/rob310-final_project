from machine import Pin, ADC, UART
import utime
from readVoltage import ReadIn


if __name__ == "__main__":
    emg_bi = ReadIn(26, 0.5, 10)
    emg_tri = ReadIn(27, 0.5, 10)
    
    sampling_period = 100 # Sampling period in milliseconds (2 samples per second)
    try:
        emg_bi.calibrate()
        emg_tri.calibrate()
        
        while True:
            start_time = utime.ticks_ms()
            
            volt_bi = emg_bi.read()
            volt_tri = emg_tri.read()
            volt_diff = volt_bi - volt_tri
            print(f"EMA_bi: {round(volt_bi, 4)} EMA_tri: {round(volt_tri, 4)}")
            print(f"volt_diff: {volt_diff}")
            
            
            time_spent = utime.ticks_diff(utime.ticks_ms(), start_time)
            utime.sleep_ms(max(0, sampling_period - time_spent))
        
        
    except KeyboardInterrupt:
        print('ctrl+c pressed')