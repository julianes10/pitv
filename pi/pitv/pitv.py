#!/usr/bin/env python3
import argparse
import time
import datetime
import sys
import json
import subprocess
import os
import signal
import platform
import threading
import helper
from random import randint
import re
import random
import shutil
import requests 
from helper import *
from flask import Flask, render_template,redirect
from flask import Flask, jsonify,abort,make_response,request, url_for
from datetime import datetime

import requests






'''----------------------------------------------------------'''
'''----------------------------------------------------------'''

def format_datetime(value):
    aux="unknown"
    try:
      aux=time.ctime(value)
    except Exception as e:
      helper.internalLogger.critical("Error reading value date: {0}.".format(value))
      helper.einternalLogger.exception(e)
    return aux 




'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api",template_folder="templates",static_folder='static_pitv')
api.jinja_env.filters['datetime'] = format_datetime





'''----------------------------------------------------------'''
@api.route('/',methods=["GET", "POST"])
@api.route('/pitv/',methods=["GET", "POST"])
def pitv_home():
    if request.method == 'POST':
      helper.internalLogger.debug("Processing new request from a form...{0}".format(request.form))
      form2 = request.form.to_dict()
      helper.internalLogger.debug("TODO Processing new request from a form2...{0}".format(form2))   
    
    url={}

    cmd="/opt/pitv/pitv/getImages.sh"
    subprocess.run(['bash','-c',cmd])

    st=getStatus()

    rt=render_template('index.html', title="pitv Site",status=st,randomhack=randint(0,100000))
    return rt

'''----------------------------------------------------------'''
@api.route('/api/v1.0/pitv/status', methods=['GET'])
def get_pitv_status():  
    return json.dumps(getStatus())

def getStatus():
    rt={}
    rt['btnWhite']=GLB_bWhite
    rt['btnRed']=GLB_bRed
    rt['pir']=GLB_PIR
    return rt


'''----------------------------------------------------------'''
@api.route('/clean/<name>',methods=["GET"])
@api.route('/pitv/clean/<name>',methods=["GET"])
def pitv_gui_clean(name):
   helper.internalLogger.debug("GUI clean {0}...".format(name))
   #TODO cleanProject(name)
   return redirect(url_for('pitv_home'))



'''----------------------------------------------------------'''
def  getDHT():
  # Create blank image for drawing.  
  rtt = 0.0
  rth = 0.0

  try:
    response = requests.get(GLB_configuration["dht-query"])
    helper.internalLogger.debug("getTemperature response {0}...".format(response.json()))
   
    rth=float(response.json()[0]["humidity"])
    rtt=float(response.json()[0]["temperature"])
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.warning('Error: Exception getting dht data properly')
    helper.einternalLogger.exception(e)  


  return rtt,rth


'''----------------------------------------------------------'''
def  sendEvent(event,txt):
  try:
    d = {"name": event, "text": txt} 
    r = requests.post(GLB_configuration["telegram-event-query"],json = d)
    helper.internalLogger.debug("sendEvent {0} response {1}...".format(d,r.json())) 
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.warning('Error: Exception sending event')
    helper.einternalLogger.exception(e)  




'''----------------------------------------------------------'''
def  display_clock(oled):
  # Create blank image for drawing.

  if amIaPi():
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    
  image = Image.new("1", (oled.width, oled.height))
  draw = ImageDraw.Draw(image)
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
  # Draw the text
  text = time.strftime(" %H:%M")

  draw.text((0, 0),text, font=font, fill=255)
  # Display image
  oled.image(image)

  if GLB_PIR:
    oled.pixel(0, 31, 1)
    oled.pixel(0, 30, 1)
    oled.pixel(1, 31, 1)
    oled.pixel(1, 30, 1)


  oled.show()

'''----------------------------------------------------------'''
def  display_temp(oled,t):
  # Create blank image for drawing.
  if amIaPi():
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    
    
  image = Image.new("1", (oled.width, oled.height))
  draw = ImageDraw.Draw(image)
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
  # Draw the text
  text = "{:.1f}".format(t) + chr(176)+"C"
  draw.text((0, 0),text, font=font, fill=255)
  # Display image
  oled.image(image)

  if GLB_PIR:
    oled.pixel(0, 31, 1)
    oled.pixel(0, 30, 1)
    oled.pixel(1, 31, 1)
    oled.pixel(1, 30, 1)

  oled.show()

'''----------------------------------------------------------'''
def  display_hum(oled,h):
  # Create blank image for drawing.
  if amIaPi():
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    
    
  image = Image.new("1", (oled.width, oled.height))
  draw = ImageDraw.Draw(image)
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
  # Draw the text
  text = " {:.1f} %".format(h)

  draw.text((0, 0),text, font=font, fill=255)
  # Display image
  oled.image(image)

  if GLB_PIR:
    oled.pixel(0, 31, 1)
    oled.pixel(0, 30, 1)
    oled.pixel(1, 31, 1)
    oled.pixel(1, 30, 1)

  oled.show()

'''----------------------------------------------------------'''
def  display_text(oled,text):
  # Create blank image for drawing.
  if amIaPi():
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    
  image = Image.new("1", (oled.width, oled.height))
  draw = ImageDraw.Draw(image)
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
  # Draw the text
  draw.text((0, 0),text, font=font, fill=255)
  # Display image
  oled.image(image)
  oled.show()

'''----------------------------------------------------------'''
def setupDisplay():

  if amIaPi():
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
  RESET_PIN = digitalio.DigitalInOut(board.D4)
  i2c = board.I2C()
  oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c, reset=RESET_PIN)

  oled.fill(0)
  oled.show()

  return oled



'''----------------------------------------------------------'''
def runCmdBackground(cmd):
  subprocess.Popen(['bash','-c',cmd])
  helper.internalLogger.debug("Just. Executed {0} ".format(cmd))
  return "Action Executed in background"


'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''
def main(configfile):
  print('pitv-start -----------------------------')
  
  
  if amIaPi():
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306

  # Loading config file,
  # Default values
  cfg_log_debugs="pitv.log"
  cfg_log_exceptions="pitve.log"

  global GLB_configuration
  
  GLB_configuration={}
  with open(configfile) as json_data:
      GLB_configuration = json.load(json_data)
  #Get log names
  if "log" in GLB_configuration:
      if "logTraces" in GLB_configuration["log"]:
        cfg_log_debugs = GLB_configuration["log"]["logTraces"]
      if "logExceptions" in GLB_configuration["log"]:
        cfg_log_exceptions = GLB_configuration["log"]["logExceptions"]
  helper.init(cfg_log_debugs,cfg_log_exceptions)

  print('See logs debugs in: {0} and exeptions in: {1}-----------'.format(cfg_log_debugs,cfg_log_exceptions))  
  helper.internalLogger.critical('pitv-start -------------------------------')  
  helper.einternalLogger.critical('pitv-start -------------------------------')


  try:    
    logging.getLogger("requests").setLevel(logging.DEBUG) 

    helper.internalLogger.debug("Starting restapi...")
    apiRestTask=threading.Thread(target=apirest_task,name="restapi")
    apiRestTask.daemon = True
    apiRestTask.start()

    if amIaPi():
      import RPi.GPIO as GPIO
      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(GLB_configuration["PIR"]["pin"], GPIO.IN) 
      GPIO.setup(GLB_configuration["white-button"]["pin"], GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
      GPIO.setup(GLB_configuration["red-button"]["pin"], GPIO.IN,pull_up_down=GPIO.PUD_DOWN)


     
      oled=setupDisplay()


    global GLB_PIR
    global GLB_bWhite
    global GLB_bRed


    GLB_PIR=False
    GLB_bWhite=False
    GLB_bRed=False

    helper.internalLogger.debug("Start pooling...")  

    st = 0
    latestSecProcessed=0
    PIRBk = False
    bWhiteBk = False
    bRedBk = False
    while (True):
     if not amIaPi():
      time.sleep(5)
     else:
      sec=int(time.time())
      GLB_PIR    = GPIO.input(GLB_configuration["PIR"]["pin"])==1
      GLB_bWhite = GPIO.input(GLB_configuration["white-button"]["pin"])==1
      GLB_bRed   = GPIO.input(GLB_configuration["red-button"]["pin"])==1

      if GLB_bWhite != bWhiteBk and bWhiteBk==False:  
        # Falling edge  
        runCmdBackground(GLB_configuration["white-button"]["cmd"])
        sendEvent("button","White button pressed")

      if GLB_bRed != bRedBk and bRedBk==False: 
        # Falling edge         
        runCmdBackground(GLB_configuration["red-button"]["cmd"])
        sendEvent("button","Red button pressed")

      PIRBk = GLB_PIR
      bWhiteBk = GLB_bWhite
      bRedBk = GLB_bRed


      try:
        if GLB_bWhite and GLB_bRed:
          display_text(oled,"ROJ-BLA")  
          #TODO 
          continue     
        if GLB_bWhite:
          display_text(oled,"BLANCO")  
          continue
        if GLB_bRed:
          display_text(oled,"ROJO")  

          continue
      except Exception as e:
        e = sys.exc_info()[0]
        helper.internalLogger.debug('Error: Exception unprocessed properly. Exiting')
        helper.einternalLogger.exception(e)  


      # simple display control  
      if (sec%10 == 0):          
        if latestSecProcessed != sec:
          latestSecProcessed=sec  
          #time to change state
          t,h=getDHT()
          st=st+1
          if st > 2:
            st=0
      
      if st==0:  
        display_clock(oled)
      elif st==1:
        display_temp(oled,t)
      elif st==2:
        display_hum(oled,h)
      else:
        display_text(oled,"KO-------------OK")
  

      print(round(time.time()))
      time.sleep(0.1)
 
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('pitv-General exeception captured. See log:{0}',format(cfg_log_exceptions))   
    if not pt==None:
      pt.join()
    loggingEnd()

'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():

  api.run(debug=True, use_reloader=False,port=GLB_configuration["port"],host=GLB_configuration["host"])


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('pitv-end -----------------------------')        
  print('pitv-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='pitv software')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/pitv.conf',
                        help='Config file for the service')
    return parser.parse_args()

'''----------------------------------------------------------'''
'''----------------    printPlatformInfo  -------------------'''
def printPlatformInfo():
    print("Running on OS '{0}' release '{1}' platform '{2}'.".format(os.name,platform.system(),platform.release()))
    print("Uname raw info: {0}".format(os.uname()))
    print("Arquitecture: {0}".format(os.uname()[4]))
    print("Python version: {0}".format(sys.version_info))

'''----------------------------------------------------------'''
'''----------------       '__main__'      -------------------'''
if __name__ == '__main__':
    printPlatformInfo()
    args = parse_args()
    main(configfile=args.configfile)

