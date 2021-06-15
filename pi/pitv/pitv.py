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
import queue



class RotarySwitch:
  def __init__(self,config):
    self.timestamp = 0
    self.q = queue.Queue()
    self.config=config
    self.setMenu("root")
    self.latestActivity = 0
          
  def setMenu(self,m):
    try:
      self.currentMenu=m
      self.currentMenuOption=self.config["menu"][self.currentMenu]["options"][0]
    except Exception as e:
      helper.internalLogger.debug("Error setting menu: {0}, fallback to root".format(m))
      helper.einternalLogger.exception(e)
      self.currentMenu="root"
      self.currentMenuOption=self.config["menu"][self.currentMenu]["options"][0]

  def switchOn(self):
    ev={}
    ev["switch"]=True
    self.q.put(ev)

  def left(self,value):
    ev={}
    ev["left"]=value
    self.q.put(ev)

  def right(self,value):
    ev={}
    ev["right"]=value
    self.q.put(ev)

  def doSwitchOn(self):
    if self.currentMenuOption == "..":
      self.setMenu("root")  #TODO better recall history
      display_menu(oled,self.currentMenu,self.currentMenuOption)
      return
    item=self.config["menu"][self.currentMenuOption]
    helper.internalLogger.debug("Switching On for {0}...".format(self.currentMenuOption))
    try:
      #Execute associated command
      if "cmd" in item:
         runCmdBackground(item["cmd"])
      #Show display
      if "display" in item:
         display_text(oled,item["display"])
      #Show display
      if "options" in item:
         self.setMenu(self.currentMenuOption)
         display_menu(oled,self.currentMenu,self.currentMenuOption)
    except Exception as e:
      helper.internalLogger.debug("Error processing rotary event...")
      helper.einternalLogger.exception(e)
          
    return False

  def doRight(self,value):
    maxlen=len(self.config["menu"][self.currentMenu]["options"])
    currentPos=self.config["menu"][self.currentMenu]["options"].index(self.currentMenuOption)
    newPos=currentPos + 1
    if (newPos) >= (maxlen):
      newPos=0
    self.currentMenuOption=self.config["menu"][self.currentMenu]["options"][newPos]
    display_menu(oled,self.currentMenu,self.currentMenuOption)

  def doLeft(self,value):
    maxlen=len(self.config["menu"][self.currentMenu]["options"])
    currentPos=self.config["menu"][self.currentMenu]["options"].index(self.currentMenuOption)
    newPos=currentPos - 1
    if (currentPos) <= 0:
      newPos=maxlen-1
    self.currentMenuOption=self.config["menu"][self.currentMenu]["options"][newPos]
    display_menu(oled,self.currentMenu,self.currentMenuOption)

  def refresh(self):
    now = time.time()
    rt=False
    try:
      #helper.internalLogger.debug("Checking queue...")
      while not self.q.empty():       
        self.latestActivity=now
        rt=True
        helper.internalLogger.debug("Processing event...")
        ev=self.q.get()
        helper.internalLogger.debug("Event {0}".format(ev))
        if (now - self.latestActivity) > self.config["timeout"]:
          helper.internalLogger.debug("Waking from standby event ignored, just display legacy menu")
          display_menu(oled,self.currentMenu,self.currentMenuOption)
          continue
        
        if "switch" in ev:
          helper.internalLogger.debug("EV SWITCH ON") 
          self.doSwitchOn()   
        elif "left" in ev:
          helper.internalLogger.debug("EV LEFT: {0}".format(ev["left"]))
          self.doLeft(ev["left"])
        elif "right" in ev:
          helper.internalLogger.debug("EV RIGHT: {0}".format(ev["right"]))
          self.doRight(ev["right"])
        else:
          helper.internalLogger.debug("Unknown event...")
    except Exception as e:
      helper.internalLogger.debug("Error processing rotary event...")
      helper.einternalLogger.exception(e)

    if (now - self.latestActivity) < self.config["timeout"]:
      rt=True #Forcing showing menu for a while    

    return rt


'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
def my_callback(scale_position):
    helper.internalLogger.debug("ROTARY scale position is {0}".format(scale_position))
def rs_cb_dec(scale_position):
    helper.internalLogger.debug("ROTARY dec {0}".format(scale_position))
    #filtering out odds
    if scale_position%2==0:
      rs.right(scale_position)
def rs_cb_inc(scale_position):
    helper.internalLogger.debug("ROTARY inc {0}".format(scale_position))
    #filtering out odds
    if scale_position%2==0:
      rs.left(scale_position)
def rs_cb_sw():
    helper.internalLogger.debug("ROTARY switch on")
    rs.switchOn()

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
    return rt


'''----------------------------------------------------------'''
@api.route('/clean/<name>',methods=["GET"])
@api.route('/pitv/clean/<name>',methods=["GET"])
def pitv_gui_clean(name):
   helper.internalLogger.debug("GUI clean {0}...".format(name))
   #TODO cleanProject(name)
   return redirect(url_for('pitv_home'))

@api.route('/pitv/rs/left/<value>',methods=["GET"])
def pitv_rs_left(value):
   helper.internalLogger.debug("REST rs left {0}...".format(value))
   rs.left(value)
   return "ok"
@api.route('/pitv/rs/right/<value>',methods=["GET"])
def pitv_rs_right(value):
   helper.internalLogger.debug("REST rs right {0}...".format(value))
   rs.right(value)
   return "ok"
@api.route('/pitv/rs/switchOn',methods=["GET"])
def pitv_rs_switch():
   helper.internalLogger.debug("REST rs switchOn ...")
   rs.switchOn()
   return "ok"


class DHT:
  def __init__(self):
    self.t = 0
    self.h = 0

  def  refresh(self):
    # Create blank image for drawing.  
    rtt = 0.0
    rth = 0.0
    try:
     if not "dht-query" in GLB_configuration:
       return
     response = requests.get(GLB_configuration["dht-query"])
     helper.internalLogger.debug("getTemperature response {0}...".format(response.json()))
   
     rth=float(response.json()[0]["humidity"])
     rtt=float(response.json()[0]["temperature"])
    except Exception as e:
     e = sys.exc_info()[0]
     helper.internalLogger.warning('Error: Exception getting dht data properly')
     helper.einternalLogger.exception(e)  
    self.t=rtt
    self.h=rth
  def getTemp(self):
    return self.t
  def getHum(self):
    return self.h

class DHTremote:
  def __init__(self,name):
    self.t = 0
    self.h = 0
    self.id=name

  def  refresh(self,tt,hh):
    self.t = tt
    self.h = hh

  def getTemp(self):
    return self.t
  def getHum(self):
    return self.h



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
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
  font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 44)
  # Draw the text
  text = time.strftime("%H:%M")
  draw.text((0, 0),"HORA", font=font, fill=255)  
  draw.text((0, 20),text, font=font2, fill=255)
  # Display image
  oled.image(image)

  oled.show()

'''----------------------------------------------------------'''
def  display_temp(oled,msg,t):
  # Create blank image for drawing.
  if amIaPi():
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    
    
  image = Image.new("1", (oled.width, oled.height))
  draw = ImageDraw.Draw(image)
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
  font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 56)
  font3 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
  # Draw the text
  text = "{:.1f}".format(t)
  text2 = chr(176)
  #text = "{:.1f}".format(t)
  draw.text((0, 0),msg, font=font, fill=255)  
  draw.text((0, 8),text, font=font2, fill=255)
  draw.text((116, 11),text2, font=font3, fill=255)
  # Display image
  oled.image(image)



  oled.show()





'''----------------------------------------------------------'''
def  display_hum(oled,msg,h):
  # Create blank image for drawing.
  if amIaPi():
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    
    
  image = Image.new("1", (oled.width, oled.height))
  draw = ImageDraw.Draw(image)
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
  font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 49)
  font3 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
  # Draw the text
  text = "{:.1f}".format(h)
  text2 = "%"
  draw.text((0, 0),msg, font=font, fill=255)  
  draw.text((0, 15),text, font=font2, fill=255)
  draw.text((110, 44),text2, font=font3, fill=255)
  # Display image
  oled.image(image)


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
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)
  # Draw the text
  draw.text((0, 0),text, font=font, fill=255)
  # Display image
  oled.image(image)
  oled.show()



'''----------------------------------------------------------'''
def  display_menu(oled,menu,item):
  # Create blank image for drawing.
  if amIaPi():
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    
  image = Image.new("1", (oled.width, oled.height))
  draw = ImageDraw.Draw(image)
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
  # Draw the text
  draw.text((0, 0),menu, font=font, fill=255)  

  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
  draw.text((0, 15),item, font=font, fill=255)
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
  global dht
  global dhtRemote
  global rs
  global oled

  dht = DHT()
  dhtRemote = DHTremote("DHT1")
  


  
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


  rs  = RotarySwitch(GLB_configuration["rs"])

  try:    
    logging.getLogger("requests").setLevel(logging.DEBUG) 

    helper.internalLogger.debug("Starting restapi...")
    apiRestTask=threading.Thread(target=apirest_task,name="restapi")
    apiRestTask.daemon = True
    apiRestTask.start()

    helper.internalLogger.debug("Starting DHTRestTask...")
    DHTRestTask=threading.Thread(target=DHTrest_task,name="DHTrest")
    DHTRestTask.daemon = True
    DHTRestTask.start()


    helper.internalLogger.debug("Starting DHTRemoteTask...")
    DHTRemoteTask=threading.Thread(target=DHTremote_task,name="DHTremote")
    DHTRemoteTask.daemon = True
    DHTRemoteTask.start()

    if amIaPi():
      import RPi.GPIO as GPIO
      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BCM)
      oled=setupDisplay()
      from pyky040 import pyky040
      my_encoder = pyky040.Encoder(CLK=5, DT=6, SW=13)
      my_encoder.setup(scale_min=0, scale_max=100, step=1,inc_callback=rs_cb_inc,dec_callback=rs_cb_dec,sw_callback=rs_cb_sw)
      my_thread = threading.Thread(target=my_encoder.watch)
      my_thread.start()

    helper.internalLogger.debug("Start pooling...")  
    st = 0
    latestSecProcessed=0

    display_text(oled,"PITV!")  
    time.sleep(2)
    
    while (True):
     if not amIaPi():
      time.sleep(5)
     else:
      sec=int(time.time())

      # simple display control  
      if (sec%5 == 0):          
        if latestSecProcessed != sec:
          latestSecProcessed=sec  
          st=st+1
          if st > 6:
            st=0

      if rs.refresh() == False: 
	      if st==0:  
		      display_clock(oled)
	      elif st==1 or st==2:
		      display_temp(oled,"SALON",dht.getTemp())
	      elif st==3:
		      display_hum(oled,"SALON",dht.getHum())
	      elif st==4 or st==5:
		      display_temp(oled,"         TERRAZA",dhtRemote.getTemp())
	      elif st==6:
		      display_hum(oled,"         TERRAZA",dhtRemote.getHum())
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
'''----------------     DHTrest_task      -------------------'''
def DHTrest_task():
  while (True):
    dht.refresh();
    if "dht-query-interval" in GLB_configuration:
      time.sleep(GLB_configuration["dht-query-interval"])
    else:
      time.sleep(60)


'''----------------------------------------------------------'''
'''----------------     DHTremote_task      -------------------'''
def DHTremote_task():
  import socket
  UDP_IP = "0.0.0.0"
  UDP_PORT = 3000

  try:
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    while True:
      data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
      print("Receive message {0} ".format(data))
      try:
        s=data.decode('utf-8').split(',')
        sensor=s[0]
        temp=float(s[1])
        hum=float(s[2])
        helper.internalLogger.debug("Sensor id {0}, temp {1}, hum {2} ".format(sensor,temp,hum))
        #TODO select right dht
        dhtRemote.refresh(temp,hum)
      except Exception as e:
        e = sys.exc_info()[0]
        helper.internalLogger.debug('Error: Exception receiving dht remote data')
        helper.einternalLogger.exception(e)  
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.warning('Error: Exception listening at dht remote socket')
    helper.einternalLogger.exception(e)  



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

