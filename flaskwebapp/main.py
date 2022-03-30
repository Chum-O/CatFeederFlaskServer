import atexit
from crypt import methods
from flask import Flask, render_template, Response, request
import time
import threading
import os
import picamera

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from servoMotor import ServoMotor
from charLCD import charLCD
from apscheduler.schedulers.background import BackgroundScheduler

def update():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))
    return

scheduler = BackgroundScheduler()
scheduler.add_job(func = update, trigger="interval", seconds=60)
scheduler.start()

kit = MotorKit()
lcd = charLCD

feedingtime1 = ""
feedingtime2 = ""
feedingtime3 = ""

app = Flask(__name__)

@app.route("/", methods=['GET'])
def respond():
    return "Successfully called"

@app.route("/setFeeding/<time>", methods=['POST'])
def setTime(time):
    args = request.args
    print(args)
    print(time)
    print('Something')
    return "success"

@app.route("/getTimes", methods=['GET'])

@app.route("/feed")
def feed():
    camera = ServoMotor()
    camera.pointToBowl()
    lcd.setMessage(lcd,"  Feeding time!","       >x<")

    for i in range(250):
        kit.stepper1.onestep(direction = stepper.FORWARD, style=stepper.DOUBLE)
    for i in range(25):
        kit.stepper1.onestep(direction = stepper.BACKWARD, style=stepper.DOUBLE)
    kit.stepper1.release()
    
    lcd.clearLCDLeft(lcd)

    return "received"

@app.route("/randomJitter")
def randomJitter():
    lasertoy = ServoMotor()
    lasertoy.randomJitter()
    return "received"




if __name__ == "__main__":
    app.run(host="0.0.0.0", port = "5000", debug=True)

atexit.register(lambda: scheduler.shutdown())