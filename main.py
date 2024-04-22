from receiver import Receiver
from pid_controller import PID
from encoder import Encoder
from motor_class import Motor
from wheel_speed import WheelSpeedCalculator as wsc
from ganggang import Ganggang as gg
from readVoltage import ReadIn

import utime

# Wheel speed PID parameters
K_P = 0.1      ## TUNE THESE VALUES !!!!
K_I = 0.001
K_D = 0.001

LEFT_MOTOR_POLARITY = -1 
RIGHT_MOTOR_POLARITY = -1

LEFT_ENC_POLARITY = -1
RIGHT_ENC_POLARITY = 1

ALPHA = 0.7 # smoothing parameter

CONV = 1/(20.0 * 78.0)   # GEAR RATIO / ENCODER CPR CONVERZAION FACTOR; converts from encoder counts to motor output revs

if __name__ == "__main__":

    # initialize motors, encoders, controllers, add other initialization variables and class objects
    motorL = Motor(2, 14)
    motorR = Motor(3, 15)
    encL = Encoder(6, 7)
    encR = Encoder(8, 9)
    read_bi = ReadIn(26, 0.5, 10)
    read_tri = ReadIn(27, 0.5, 10)
    encL_read = 0
    encR_read = 0
    setpoint = 0
    pidL = PID(P=K_P, I=K_I, D=K_D, setpoint=setpoint)
    pidR = PID(P=K_P, I=K_I, D=K_D, setpoint=setpoint)
    sampling_period = 150
    
    try:
        print("Welcome using EMG controlled Mbot!")
        print("initializing...1/2")
        read_bi.calibrate()
        print("initializing...2/2")
        read_tri.calibrate()
        print("initialization done\n")
        while True:
            ## sleep the loop to allow encoders to create tick delta
            start_time = utime.ticks_ms()
            volt_bi = read_bi.read()
            volt_tri = read_tri.read()
            volt_diff = volt_bi - volt_tri
            calcL = wsc(encL_read, start_time)
            calcR = wsc(encR_read, start_time)
            utime.sleep_ms(50)
            ##
            ## calculate time delta between loop start and present time
            current_time = utime.ticks_ms()
            dt = utime.ticks_diff(current_time, start_time)/1000
            ##
            
            ## calculate left and right wheel speeds using encoder tick delta and time delta
            ## you might need some code to handle the loop initialization when dt = 0
            encL_read = encL.read() * LEFT_ENC_POLARITY
            speedL = calcL.calculateSpeed(encL_read, current_time)
            encR_read = encR.read() * RIGHT_ENC_POLARITY
            speedR = calcR.calculateSpeed(encR_read, current_time)
            ##
            
            ## update the controller and set the left and right wheel speed setpoints
            print(f"volt_bi: {volt_bi}")
            print(f"volt_tri: {volt_tri}")
            print(f"volt_diff: {volt_diff}")
            if volt_diff < 0:
                setpoint += 0.3
            elif volt_diff == 0:
                setpoint = setpoint
            elif volt_diff > 0:
                setpoint -= 0.4
            ##
            
            ## set the PID controller wheel speed setpoints
            pidL.set_speed(setpoint)
            pidR.set_speed(setpoint)
            ##
            
            ## calculate the wheel speed errors
            errorL = setpoint - speedL
            errorR = setpoint - speedR
            ##
            
            ## update the PID controller and return the left and right motor duty cycles
            pid_inputL = pidL.update(errorL, dt)
            pid_inputR = pidR.update(errorR, dt)
            ##
            
            ## IMPORTANT: ADD SATURATION LIMIT TO MOTOR DUTY CYCLES
            
            if pid_inputL > 1:
                pid_inputL = 0.99
            elif pid_inputL < -1:
                pid_inputL = -0.99
            
            if pid_inputR > 1:
                pid_inputR = 0.99
            elif pid_inputR < -1:
                pid_inputR = -0.99
            ##
            
            ## set saturation limited PID duty cycle output to motor PWM duty cycle
            print(pid_inputL)
            print(pid_inputR)
            motorL.set(pid_inputL * LEFT_MOTOR_POLARITY)
            motorR.set(pid_inputR * RIGHT_MOTOR_POLARITY)
            
            time_spent = utime.ticks_diff(utime.ticks_ms(), start_time)
            utime.sleep_ms(max(0, sampling_period - time_spent))
            ##
            
    except KeyboardInterrupt:
        left_motor.set(0) 
        right_motor.set(0)
        print("Loop interrupted by Ctrl+C")    