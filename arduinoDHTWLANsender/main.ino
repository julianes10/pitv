#include <SoftwareSerial.h>
#include <Adafruit_Sensor.h>
#include "DHT.h"
#include <stdio.h>
#include "SimpleTimer.h"
#include <Arduino.h>
#include "lsem.h"


//------------------------------------------------
//--- DEBUG  FLAGS     ---------------------------
//------------------------------------------------
// Check makefile


#define DHTPIN 7        // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321

#define PIN_LED_STRIP             6

#define NUM_LEDS 22

//------------------------------------------------
//--- GLOBAL VARIABLES ---------------------------
//------------------------------------------------
SimpleTimer mainTimers;
int  GLB_timerMisc=-1;
bool GLB_timerMisc_expired=false;
int GLB_ledTest = 0;
#define TIMEOUT_SEND_DHT    5000
#define TIMEOUT_LS_TEST    250


CRGB GLBledStripBufferMem[NUM_LEDS];
LSEM GLBledStrip(GLBledStripBufferMem,NUM_LEDS);


SoftwareSerial ESPserial(3, 4); // RX | TX

DHT GLBsensorDHT(DHTPIN, DHTTYPE);

float GLBsensorDHTTemp=0.0;
float GLBsensorDHTHum=0.0;




//------------------------------------------------
//--- GLOBAL FUNCTIONS ---------------------------
//------------------------------------------------
 

void STATE_welcome();
void STATE_idle();
void STATE_sendingData();
void goto_idle();
// State pointer function
void (*GLBptrStateFunc)();


//------------------------------------------------
//-------    TIMER CALLBACKS     -----------------
//------------------------------------------------


//------------------------------------------------
void GLBcallbackLogging(void)
{
  Serial.println(F("DEBUG: still alive from timer logging..."));
}

//------------------------------------------------

//------------------------------------------------
void GLBcallbackTimeoutMisc(void)
{
  if (GLB_timerMisc != -1)     
    mainTimers.deleteTimer(GLB_timerMisc);
  GLB_timerMisc=-1;
  GLB_timerMisc_expired=true;
}


//------------------------------------------------
void resetTimerMisc(void)
{
  GLBcallbackTimeoutMisc();
  GLB_timerMisc_expired=false;
}

void GLBcallbackLoggingLedStrip(void)
{
  Serial.println(F("DEBUG: Led strip..."));
  GLBledStrip.setAllLeds(0xAABBCC);
}


//-------------------------------------------------
void sendDHTData(){

  return;
  Serial.println("send data...");
  ESPserial.print("AT+CIPMUX=1\r\n");
  delay(1000);
  ESPserial.print("AT+CIPSTART=4,\"UDP\",\"192.168.1.55\",3000,1112,0\r\n");
  delay(1000);
  ESPserial.print("AT+CIPSEND=4,14\r\n"); //TODO NOT SURE LENGHT
  delay(1000);
  ESPserial.print("DHT1,");
  ESPserial.print(GLBsensorDHTTemp,1);
  ESPserial.print(",");
  ESPserial.print(GLBsensorDHTHum,1);
  ESPserial.print(",000\r\n");
  delay(1000);
  ESPserial.print("AT+CIPCLOSE=4\r\n");

#ifdef DHTWLAN_DEBUG_DHT  
  Serial.print(F("\nTEMP:"));
  Serial.print(GLBsensorDHTTemp,1);
  Serial.print(F("HUM:"));
  Serial.println(GLBsensorDHTHum,1);
#endif


}
//------------------------------------------------
//------------------------------------------------
//------------------------------------------------

void setup() { 
  // Serial to debug AND comunication protocolo with PI              
  Serial.begin(9600);
  Serial.println(F("BOOT"));

#ifdef DHTWLAN_DEBUG_STILLALIVE
  mainTimers.setInterval(2000,GLBcallbackLogging);
#endif 


#ifdef DHTWLAN_DEBUG_LS
  mainTimers.setInterval(10,GLBcallbackLoggingLedStrip);
#endif 



/*
  FastLED.addLeds<WS2812B,PIN_LED_STRIP,GRB>(GLBledStripBufferMem,NUM_LEDS);

  pinMode(PIN_BUTTON_RED, INPUT_PULLUP);
  pinMode(PIN_BUTTON_GREEN, INPUT_PULLUP);
  pinMode(PIN_BUTTON_BLUE, INPUT_PULLUP);

*/

  resetTimerMisc();
  GLBptrStateFunc=STATE_welcome; 


  // Start the software serial for communication with the ESP8266
  ESPserial.begin(9600);  


  GLBsensorDHT.begin();

  FastLED.addLeds<WS2812B,PIN_LED_STRIP,GRB>(GLBledStripBufferMem,NUM_LEDS);


  Serial.println(F("BD"));

}

//-------------------------------------------------
void goto_idle()
{
  
  #ifdef DHTWLAN_DEBUG_STATES
  Serial.print(F("NST_idle"));
  #endif
  resetTimerMisc();
  GLBptrStateFunc=STATE_idle; 
}


//-------------------------------------------------
void STATE_welcome()
{
 // TODO    goto_idle();  
  if   (GLB_timerMisc == -1)
  {
    GLB_timerMisc=mainTimers.setTimeout(TIMEOUT_LS_TEST,GLBcallbackTimeoutMisc);
  }
  else if (GLB_timerMisc_expired){
    GLB_timerMisc_expired=false;
    resetTimerMisc();
    //goto_idle(); 
    GLBledStrip.setAllLeds(0x0);  
    GLBledStrip.setLed(((GLB_ledTest++)%NUM_LEDS),0xAAAAAA);  
    GLB_timerMisc=mainTimers.setTimeout(TIMEOUT_LS_TEST,GLBcallbackTimeoutMisc);
    Serial.print(F("x"));
  }
}

//-------------------------------------------------
void STATE_idle()
{
  //TODO 
  if   (GLB_timerMisc == -1)
  {
    GLB_timerMisc=mainTimers.setTimeout(TIMEOUT_SEND_DHT,GLBcallbackTimeoutMisc);
  }

  if (GLB_timerMisc_expired){
    GLB_timerMisc_expired=false;
    #ifdef DHTWLAN_DEBUG_STATES
    Serial.print(F("NST_sendingData"));
    #endif
    resetTimerMisc();
    GLBptrStateFunc=STATE_sendingData; 
    return;
  }
}

//-------------------------------------------------
void STATE_sendingData()
{
  //TODO 
  sendDHTData();
  goto_idle();  
}



//-------------------------------------------------
//-------------------------------------------------
//-------------------------------------------------

void loop() { 
#ifdef DHTWLAN_DEBUG_LOOP  
  Serial.print("+");
#endif
  //------------- INPUT REFRESHING ----------------
  // Let use ugly global variables in those costly sensors to save ram...
  GLBsensorDHTTemp = GLBsensorDHT.readTemperature();
  GLBsensorDHTHum  = GLBsensorDHT.readHumidity();
    
  //--------- TIME TO THINK MY FRIEND -------------
  // State machine as main controller execution
#ifdef DHTWLAN_DEBUG_LOOP  
  Serial.print("S");
#endif
  GLBptrStateFunc();
#ifdef DHTWLAN_DEBUG_LOOP  
  Serial.print("T");
#endif
  mainTimers.run();

  // listen for communication from the ESP8266 and then write it to the serial monitor
  if ( ESPserial.available() )   {
      unsigned char aux=ESPserial.read();
      if (aux!=0) {
        Serial.write(aux);  
        /*Serial.print("[");
        Serial.print(aux, HEX);
        Serial.print("]");*/
      }
  }

  // listen for user input 
  if ( Serial.available() )       {
      //Serial.println("");
      char aux=Serial.read();
      //Serial.print("TX:");
      //Serial.print(aux);
      //Serial.print("[");
      //Serial.print(aux, HEX);
      //Serial.print("]");      
      //ESPserial.write(aux);
      if (aux == 'p')   {
        Serial.println("Ping");
        ESPserial.print("AT\r\n");
      }      
      if (aux == 'c')   {
        Serial.println("Set mode as client");
        ESPserial.print("AT+CWMODE=1\r\n");
      }      
      if (aux == 'l')   {
        Serial.println("List access points");
        ESPserial.print("AT+CWLAP\r\n");
      }  
      if (aux == 't')   {
        Serial.println("test...");
        ESPserial.print("AT+CWJAP?\r\n");
      }                
      if (aux == 's')   {
        Serial.println("status...");
        ESPserial.print("AT+CIPSTATUS\r\n");
      }   
      if (aux == 'x')   {
        sendDHTData();
      }  
      if (aux == 'w')   {
        GLBledStrip.setAllLeds(0x0);  
        GLBledStrip.setLed(((GLB_ledTest++)%NUM_LEDS),0xAAAAAA);  
      }  
  }

  // Prepare digits to show
  //GLBledStrip.setAllLeds(0xAAAAAA);  

 
  // ------------- OUTPUT REFRESHING ---------------
  // In state
  FastLED.show();
}


