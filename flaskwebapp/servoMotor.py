from adafruit_servokit import ServoKit
import time
from random import randint

kit = ServoKit(channels=16,address=0x41)

kit.servo[13].fraction = None

class ServoMotor():

    def turnOnLaser(self):
        kit.servo[13].fraction = 1.0

    def toggleLaser(self):
        if(kit.servo[13].fraction == None):
            kit.servo[13].fraction = 1.0
        else:
            kit.servo[13].fraction=None
    
    def turnOffMotor(self):
        kit.servo[13].fraction = None

    def setX(self, xfrac):
        maxX = 180
        xangle = int((xfrac/100)*maxX)
        kit.servo[15].angle = xangle
        time.sleep(.1)
        kit.servo[14].angle = None
        kit.servo[15].angle = None

    def setY(self, yfrac):
        maxY = 90
        yangle = 90 + int((yfrac/100)*maxY)
        kit.servo[14].angle = yangle
        time.sleep(.1)
        kit.servo[14].angle = None
        kit.servo[15].angle = None

    def randomJitter(self):
        kit.servo[13].fraction = 1
        for i in range(20):
            a1 = randint(60,120)
            kit.servo[15].angle = a1
            a2 = randint(120,150)
            kit.servo[14].angle = a2
            s = (randint(6,12))/10
            time.sleep(s)
        kit.servo[13].fraction = None
        kit.servo[14].angle = None
        kit.servo[15].angle = None

    def fullpan(self, n = 1):
        kit.servo[13].fraction = 1
        for i in range(n):
            kit.servo[15].angle = 0
            kit.servo[14].angle = 0
            for j in range(180):
                kit.servo[15].angle = j
                time.sleep(.02)
            for j in range(180):
                kit.servo[14].angle = j
                time.sleep(.02)
            for j in reversed(range(180)):
                kit.servo[15].angle = j
                time.sleep(.02)
            for j in reversed(range(180)):
                kit.servo[14].angle = j
                time.sleep(.02)
        kit.servo[13].fraction = None
        kit.servo[14].angle = None
        kit.servo[15].angle = None  

    def pointToBowl(self):
        kit.servo[13].fraction = None
        kit.servo[15].angle = 90
        kit.servo[14].angle = 180
        time.sleep(.5)
        kit.servo[15].angle = None
        kit.servo[14].angle = None  
    


