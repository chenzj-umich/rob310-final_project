from receiver import Receiver
from encoder import Encoder
from motor_class import Motor

import utime

class Ganggang:
    def __init__(self, rec):
        self.rec = rec
    
    def update(self, setpoint):
        signal = self.rec.read()
        print(f"Updating: {signal}")
        if signal == "1\n":
            setpoint += 0.01
        elif signal == "0\n":
            setpoint = setpoint
        elif signal == "-1\n":
            setpoint -= 0.01
        print(f"Current setpoint: {setpoint}")
        return setpoint
        

