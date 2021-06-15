BOARD_TAG    = nano
MCU = atmega328p

ARDUINO_PORT = /dev/ttyUSB0
ARDUINO_LIBS = SoftwareSerial Adafruit_Sensor DHT-sensor-library SimpleTimer FastLed lsem

USER_LIB_PATH = $(realpath ../SCS/arduino)

AVRDUDE_ARD_BAUDRATE = 57600
#AVRDUDE_ARD_BAUDRATE = 38400

#ARDMK_DIR     = /home/jes/arduino-1.8.13
#AVR_TOOLS_DIR = /home/jes/arduino-1.8.13
#ARDUINO_DIR  = /home/jes/arduino-1.8.13
#ARDUINO_DIR   = /usr/share/arduino


ARDUINO_DIR=/home/jes/arduino-1.8.13
#AVR_TOOLS_DIR=/home/jes/arduino-1.8.13/hardware/tools/avr
#AVR_TOOLS_DIR=/usr/share/arduino/hardware/tools/avr

#ARDUINO_LIB_PATH = /home/jes/arduino-1.8.13/libraries
#ARDUINO_PLATFORM_LIB_PATH = /home/jes/arduino-1.8.13/hardware/arduino/avr/libraries



#Cheatsheet 
#CPPFLAGS -c pre procesor-, should be on for any compilation C or C++. Not for linking
#CXXFLAGS compiling and linking c++
#CFLAGS   compiling and linking c
#Some flags: -Os optimized in size, setup by default 
#Some flags: -O3 optimized in speed (others 1,2 available also)

############## CONDITIONAL COMPILATION
# As the code and ram is at limit of nano, i must play with ugly ifdefs...
# DHTWLAN_ENABLE_LSLIB
# DHTWLAN_ENABLE_EXTRAMUSIC
# DHTWLAN_ENABLE_DISPLAY
# DHTWLAN_ENABLE_RTTTL
# DHTWLAN_ENABLE_RTC
# DHTWLAN_ENABLE_HCSR04
# DHTWLAN_ENABLE_DHT
# DHTWLAN_ENABLE_ALARM

# DHTWLAN_DEBUG_LOOP
# DHTWLAN_DEBUG_STATES
# DHTWLAN_DEBUG_HCSR04_MEDIAN
# DHTWLAN_DEBUG_RTC
# DHTWLAN_DEBUG_DHT
# DHTWLAN_DEBUG_HCSR04
# DHTWLAN_DEBUG_LS
# DHTWLAN_DEBUG_STILLALIVE

# HCSR04_ENABLE_MEDIANFILTER --->dangerous even with 77% ram may cause problems!
# SIMPLETIMER_ENABLE_10/5/...1 
# DHTSENSOR_ENABLE_LOWCOST22
# NONBLOCKINGRTTTL_ENABLE_MINBUFFER
# NONBLOCKINGRTTTL_ENABLE_NOTES_FLASH
# LSEM_ENABLE_PROTOCOL_LIGHT
# LSEM_ENABLE_PROTOCOL
# LSEM_DEBUG
# STRINGQUEUE_ENABLE_3/10/1
# RTTTLTRACKERLIST_ENABLE_RANDOM
############## 
CPPFLAGS+= -DDHTWLAN_ENABLE_LSLIB 
CPPFLAGS+= -DDHTWLAN_DEBUG_STATES -DDHTWLAN_DEBUG_DHT
#CPPFLAGS+=  -DDHTWLAN_DEBUG_COLOR -DDHTWLAN_DEBUG_STATES #-DDHTWLAN_DEBUG_LOOP #-DDHTWLAN_DEBUG_HCSR04   #-DDHTWLAN_DEBUG_STILLALIVE  #
CPPFLAGS+= -DSIMPLETIMER_ENABLE_5  


#   AVR_TOOLS_DIR = /usr
ARDMK_DIR=/usr/share/arduino
include $(ARDMK_DIR)/Arduino.mk


