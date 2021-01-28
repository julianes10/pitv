#include <stdio.h>
#include "SimpleTimer.h"
#include <Arduino.h>
#include "lsem.h"


//------------------------------------------------
//--- DEBUG  FLAGS     ---------------------------
//------------------------------------------------
// Check makefile

//------------------------------------------------
//--- GLOBAL VARIABLES ---------------------------
//------------------------------------------------


SimpleTimer mainTimers;

int  GLB_timerMisc=-1;
bool GLB_timerMisc_expired=false;

#define PIN_LED_STRIP  2
#define NUM_LEDS 16
CRGB GLBledStripBufferMem[NUM_LEDS];
LSEM GLBledStrip(GLBledStripBufferMem,NUM_LEDS);


#define PIN_BUTTON_RED     3
#define PIN_BUTTON_GREEN   4
#define PIN_BUTTON_BLUE    5


uint32_t RR=0;
uint32_t GG=0;
uint32_t BB=0;
uint32_t color=0;
bool bRedPressed   = false;
bool bGreenPressed = false;
bool bBluePressed  = false;

//------------------------------------------------
//--- GLOBAL FUNCTIONS ---------------------------
//------------------------------------------------

void display_idle();
bool display_welcome();
void display_button();

 

void STATE_welcome();
void STATE_idle();
void STATE_button();
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
//------------------------------------------------
//------------------------------------------------
//------------------------------------------------

void setup() { 
  // Serial to debug AND comunication protocolo with PI              
  Serial.begin(9600);
  Serial.println(F("BOOT"));

#ifdef SPTCD_DEBUG_STILLALIVE
  mainTimers.setInterval(2000,GLBcallbackLogging);
#endif 


#ifdef SPTCD_DEBUG_LS
  mainTimers.setInterval(10,GLBcallbackLoggingLedStrip);
#endif 



 FastLED.addLeds<WS2812B,PIN_LED_STRIP,GRB>(GLBledStripBufferMem,NUM_LEDS);



  resetTimerMisc();
  GLBptrStateFunc=STATE_welcome; 

  Serial.println(F("BD"));

}

//-------------------------------------------------
void goto_idle()
{
  #ifdef SPTCD_DEBUG_STATES
  Serial.print(F("NST_idle"));
  #endif
  resetTimerMisc();
  GLBptrStateFunc=STATE_idle; 
}


//-------------------------------------------------
void STATE_welcome()
{
    goto_idle();  
}

//-------------------------------------------------
void STATE_idle()
{
}


//-------------------------------------------------
//-------------------------------------------------
//-------------------------------------------------

void loop() { 
#ifdef SPTCD_DEBUG_LOOP  
  Serial.print("+");
#endif
  //------------- INPUT REFRESHING ----------------
  // Let use ugly global variables in those costly sensors to save ram...

    
  //--------- TIME TO THINK MY FRIEND -------------
  // State machine as main controller execution
#ifdef SPTCD_DEBUG_LOOP  
  Serial.print("S");
#endif
  GLBptrStateFunc();
#ifdef SPTCD_DEBUG_LOOP  
  Serial.print("T");
#endif
  mainTimers.run();

  bBluePressed = true;

  if (bRedPressed)     {
#ifdef SPTCD_DEBUG_COLOR  
    Serial.print("R"); 
#endif 
    RR+=8;
    if (RR>=0xFF){
      RR=0xFF;
      GG-=8; if (GG>0xFF) GG=0;
      BB-=8; if (BB>0xFF) BB=0;     
    }
  }
  if (bGreenPressed)   {
#ifdef SPTCD_DEBUG_COLOR 
    Serial.print("G");  
#endif 
    GG+=8;
    if (GG>=0xFF){
      GG=0xFF;
      RR-=8; if (RR>0xFF) RR=0;
      BB-=8; if (BB>0xFF) BB=0;
    }

  }
  if (bBluePressed)    {
#ifdef SPTCD_DEBUG_COLOR  
    Serial.print("B");  
#endif 
    BB+=8;
    if (BB>=0xFF){
      BB=0xFF;
      RR-=8; if (RR>0xFF) RR=0;
      GG-=8; if (GG>0xFF) GG=0;

    }
  }


  if (bBluePressed && bRedPressed){
    RR=0; GG=0; BB=0;
  }

#ifdef SPTCD_DEBUG_COLOR
  uint32_t colorBK=color;


  Serial.print("RGB:");
  Serial.print(RR,HEX);
  Serial.print(GG,HEX);
  Serial.println(BB,HEX);


  Serial.print("RGB UINT:");
  Serial.println(color,HEX);
#endif
  color=(RR<<16) | (GG<<8) | BB;


#ifdef SPTCD_DEBUG_COLOR
  Serial.println(color,HEX);
  if (colorBK!=color){
    Serial.println(color,HEX);
    colorBK=color;
  }
#endif
  GLBledStrip.setAllLeds(color);

  // ------------- OUTPUT REFRESHING ---------------
  // In state
  FastLED.show();
}

