from machine import Pin, PWM

# all the PWM values for LED duty cycle

# 0 = off
# 32768 = 50%
# 65535 = 100%


boardLed = Pin("LED", Pin.OUT)
gp16 = Pin(16, Pin.OUT)
gp16pwm = PWM(gp16)
gp16pwm.freq(8000)
gp16pwm.duty_u16(65535)

gp17 = Pin(17, Pin.OUT)
gp17.off()

gp18 = Pin(17, Pin.OUT)
gp18.off()

x = 0
while x < 5:
    x += 1
    print("LED on")
    gp16pwm.duty_u16(15000)
    sleep(.5)
    gp16pwm.duty_u16(1500)
    sleep(.5)