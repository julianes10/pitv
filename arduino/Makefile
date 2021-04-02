BOARD_TAG    = nano
MCU = atmega328p

ARDUINO_PORT = /dev/ttyUSB0
ARDUINO_LIBS = FastLed
USER_LIB_PATH = $(realpath ../SCS/arduino)

#AVRDUDE_ARD_BAE = 115200
AVRDUDE_ARD_BAUDRATE = 57600

ARDUINO_DIR=/home/jes/arduino-1.8.13
ARDMK_DIR=/usr/share/arduino


#Cheatsheet 
#CPPFLAGS -c pre procesor-, should be on for any compilation C or C++. Not for linking
#CXXFLAGS compiling and linking c++
#CFLAGS   compiling and linking c
#Some flags: -Os optimized in size, setup by default 
#Some flags: -O3 optimized in speed (others 1,2 available also)

############## CONDITIONAL COMPILATION
#DEBUG_FPS
#CLEAR_ON_START
#DEBUG_LED
############## 
CPPFLAGS+= -DLIGHT_ON_START
#CPPFLAGS+=  -DSPTCD_DEBUG_COLOR -DSPTCD_DEBUG_STATES #-DSPTCD_DEBUG_LOOP #-DSPTCD_DEBUG_HCSR04   #-DSPTCD_DEBUG_STILLALIVE  #
#CPPFLAGS+= -DSIMPLETIMER_ENABLE_5  


include $(ARDMK_DIR)/Arduino.mk



