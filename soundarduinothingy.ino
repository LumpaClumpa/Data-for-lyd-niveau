#include "DFrobot_MSM261.h"
#include <WiFi.h>

// Sound setup stuff. Connect to correct pins. Prob don't touch sample rate. Data bit stays 16.
#define SAMPLE_RATE     (44100)
#define I2S_SCK_IO      (19)
#define I2S_WS_IO       (26)
#define I2S_DI_IO       (23)
#define DATA_BIT        (16)
#define MODE_PIN        (18)
DFRobot_Microphone microphone(I2S_SCK_IO, I2S_WS_IO, I2S_DI_IO);
char i2sReadrawBuff[100];

// WiFi variables
const char* ssid = "iPhone";
const char* password = "ztqzygzx";

void initWiFi() { // Function for connecting to WiFi
  WiFi.mode(WIFI_STA); // Starts in station mode. This means it will connect to an access point (WiFi)
  WiFi.begin(ssid, password); // Connects to the given access point
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println(WiFi.localIP());
}

void setup() {
  // Sound setup stuff
  Serial.begin(115200);
  pinMode(MODE_PIN,OUTPUT);
  digitalWrite(MODE_PIN,LOW);//Configure the Microphone to Receive Left Channel Data
  //digitalWrite(MODE_PIN,HIGH);//Configure the Microphone to Receive Right Channel Data
  while(microphone.begin(SAMPLE_RATE, DATA_BIT) != 0){
      Serial.println(" I2S init failed");
  }
  Serial.println("I2S init success");

  // WiFi connection
  initWiFi();
}

void loop() {
  microphone.read(i2sReadrawBuff,100);
  //Output Right Channel Data
  //Serial.println((int16_t)(i2sReadrawBuff[2]|i2sReadrawBuff[3]<<8));
  //Output Left Channel Data
  Serial.println((int16_t)(i2sReadrawBuff[0]|i2sReadrawBuff[1]<<8));
  delay(100);
}
