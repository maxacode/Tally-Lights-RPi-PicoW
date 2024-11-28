from machine import Pin, PWM
pin = Pin(44)


def setPWM(dutyNum: int)-> None:
    """
    Generates a PWM signal with a high output for 1 second.
    
    Parameters:
    -dutyNum 1-10 - 10 highest - 1 is low buzz - 0 is off
    
    Returns:
        None
        
    """
    # Initialize PWM on the specified pin
    if dutyNum > 10:
        dutyNum = 10
        
        
    freq = 2400
    duty = int(100 + (dutyNum - 0) * (903 - 1) / (10 - 0))
    
    if dutyNum == 0:
            # Turn off PWM (set duty to 0)
        pwm = PWM(pin, freq=100, duty=100)

       # print('Turnign off')
        pwm.duty(0)
       # pwm.deinit()  # Disable the PWM channel
    else:
        pwm = PWM(pin, freq=freq, duty=duty)
    
    
    # Keep the PWM output high for 1 second
    #time.sleep(1)
    

    

if __name__ == "__main__":
#     from time import sleep
#     for x in range(0, 11):
#         setPWM(x)
#         print(x)
#         sleep(.5)
    setPWM(12)
        

