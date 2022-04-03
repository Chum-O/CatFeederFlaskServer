import atexit
from crypt import methods
import string
from turtle import delay
from flask import Flask, render_template, Response, request
from time import time,sleep
import time
import threading
import os
import picamera
import sqlite3 as sql
from datetime import datetime, timedelta

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from servoMotor import ServoMotor
from charLCD import charLCD

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "petfeederplus.db")

motor = MotorKit()
lcd = charLCD

feedingtime1 = ""
feedingtime2 = ""
feedingtime3 = ""
connection = sql.connect(db_path)
cur = connection.cursor()
feedsize = cur.execute("SELECT SIZE FROM scheduledfeeds WHERE feed_id = 1").fetchall()
connection.close()
feedsize = float(feedsize[0][0])      
feedSize = "0.5"
feedSizeTemp = "0.5"

def update():
    while True:
        connection = sql.connect(db_path)
        cur = connection.cursor()
        times = cur.execute("SELECT TIME FROM SCHEDULEDFEEDS").fetchall()
        connection.close()
        print("Current feed times: "+times[0][0]+", "+times[1][0]+", "+times[2][0])
        t1 = None
        t2 = None
        t3 = None
        if (times[0][0] != ""):
            t1 = datetime.strptime(times[0][0],"%H:%M")
        if (times[1][0] != ""):
            t2 = datetime.strptime(times[1][0],"%H:%M")
        if (times[2][0] != ""):
            t3 = datetime.strptime(times[2][0],"%H:%M")
        if(t1!=None):
            t1s = t1.strftime("%I:%M%p")
        else:
            t1s = ""
        if(t2!=None):
            t2s = t2.strftime("%I:%M%p")
        else:
            t2s = ""
        if(t3!=None):
            t3s = t3.strftime("%I:%M%p")
        else:
            t3s = ""

        m1 = "Times: " + t1s
        m2 = t2s + " " + t3s

        threading.Thread(target=lcd.setMessage, args = (lcd,m1,m2)).start()

        if(checkIfFeedTime()):
            time.sleep(80)
        else:
            time.sleep(40)

def dispenseFood(t):
    motor.motor1.throttle = 1
    time.sleep(t)
    motor.motor1.throttle = 0
    motor.motor1.throttle = -.5
    time.sleep(.5)
    motor.motor1.throttle = 0


def checkIfFeedTime():
    connection =sql.connect(db_path)
    cur = connection.cursor()
    scheduledfeeds = cur.execute("select * from scheduledfeeds").fetchall()
    currentTime = time.strftime("%H:%M")
    if (currentTime[0] == "0"):
        currentTime = currentTime[1:]
    for x in scheduledfeeds:
        if x[1] == currentTime:
            t = .75 + float(x[2])
            dispenseFood(t)
            connection = sql.connect(db_path)
            connection.cursor().execute("INSERT INTO FEEDINGLOG (date,time,status) VALUES (?,?,?)",(time.strftime("%Y-%m-%d"),time.strftime("%I:%M:%S %p"),"automatic"))
            connection.commit()
            print("Automatic feed checker: Feed Triggered! "+time.strftime("%A, %d. %B %Y %I:%M:%S %p"))
            threading.Thread(target=lcd.tempMessage, args = (lcd,"Automatic feed","triggered! >X<",45)).start()
            return True
        else:
            print("Automatic feed checker: No feed; "+x[1])
    connection.close()    
    return False
        


app = Flask(__name__)

@app.route("/", methods=['GET'])
def respond():
    return "received"

@app.route("/setFeeding/<time>", methods=['POST'])
def setTime(time):
    t1 = time.find(".")
    t2 = time.find(":")
    feednumber = time[0:t1]
    feedtime = time[t1+1:]
    print("Update feedingtime"+feednumber+" = "+feedtime)

    if feednumber == "1":
        feedingtime1 = feedtime
    elif feednumber =="2":
        feedingtime2 = feedtime
    elif feednumber == "3":
        feedingtime3 = feedtime

    feednumberint = int(feednumber)
    
    connection = sql.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE SCHEDULEDFEEDS SET TIME = ? WHERE FEED_ID = ?",(feedtime,feednumberint))
    connection.commit()
    connection.close()
    t = datetime.strptime(feedtime,"%H:%M")
    feedtime12hr = t.strftime("%I:%M %p")
    l1 = "Feed time "+feednumber+" set"
    l2 = "to: "+feedtime12hr
    
    threading.Thread(target=lcd.tempMessage, args=(lcd,l1,l2,5)).start()

    return "success"

@app.route("/deleteFeeding/<feedID>", methods=['POST'])
def deleteFeeding(feedID):
    feedIDInt = int(feedID)
    connection = sql.connect(db_path)
    connection.cursor().execute("UPDATE SCHEDULEDFEEDS SET TIME = ? WHERE FEED_ID = ?",("",feedIDInt))
    connection.commit()
    connection.close()
    return "success"

@app.route("/setFeedSizeTemp/<size>", methods=['POST'])
def setFeedSizeTemp(size):
    connection = sql.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE SCHEDULEDFEEDS SET SIZE = ? WHERE FEED_ID = 99",(size,))
    connection.commit()
    connection.close()
    return "success"

@app.route("/setFeedSize/<size>", methods = ['POST'])
def setFeedSize(size):
    t1 = size.find(":")
    t2 = size.find(".")
    feed_id = size[0:t1]
    feed_id_int = int(feed_id)
    feedsize = size[t1+1:]
    connection = sql.connect(db_path)
    connection.cursor().execute("UPDATE SCHEDULEDFEEDS SET SIZE = ? WHERE FEED_ID = ?",(feedsize,feed_id_int))
    connection.commit()
    connection.close()
    print(size)
    return "success"

@app.route("/setServo/<ratio>", methods=['POST'])
def setServo(ratio):
    mid = int(ratio.find(':'))
    xarg = ratio[0:mid]
    yarg = ratio[mid+1:]
    laserToy = ServoMotor()
    laserToy.setX((100-int(xarg)))
    laserToy.setY(int(yarg))
    return "success"

@app.route("/toggleLaser", methods=['GET'])
def toggleLaser():
    laserToy = ServoMotor()
    laserToy.toggleLaser()
    return "success"

@app.route("/getTimes", methods=['GET'])
def getTimes():
    connection = sql.connect(db_path)
    cur = connection.cursor()
    data = cur.execute("SELECT * FROM feedinglog").fetchall()
    connection.close()
    return render_template('feedinglog.html', data = data)

@app.route("/feed")
def feed():
    camera = ServoMotor()
    camera.setX(11)
    camera.setY(74) 
    connection = sql.connect(db_path)
    feedSizeT = connection.cursor().execute("SELECT SIZE FROM SCHEDULEDFEEDS WHERE FEED_ID = 99").fetchall()
    print(.75+float(feedSizeT[0][0]))
    dispenseFood(.75 + float(feedSizeT[0][0]))
    connection.cursor().execute("INSERT INTO FEEDINGLOG (date,time,status) VALUES (?,?,?)",(time.strftime("%Y-%m-%d"),time.strftime("%I:%M:%S %p"),"manual"))
    connection.commit()
    connection.close()
    threading.Thread(target=lcd.tempMessage, args=(lcd,"Manual Feeding","Triggered!  >X<",5)).start()
    return "received"

@app.route("/randomJitter")
def randomJitter():
    threading.Thread(target=lcd.tempMessage, args=(lcd,"   Play time!","      >x<",15)).start()
    lasertoy = ServoMotor()
    lasertoy.randomJitter()
    return "received"

if __name__ == "__main__":
    threading.Thread(target=update).start()
    app.run(host="0.0.0.0", port = "5000", debug=False)
