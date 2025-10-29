#include "DFrobot_MSM261.h"
#include <WiFi.h>
#include <HTTPClient.h>

// Sound setup stuff. Connect to correct pins. Prob don't touch sample rate. Data bit stays 16.
#define SAMPLE_RATE (44100)
#define I2S_SCK_IO (19) // sck on arduino
#define I2S_WS_IO (26) // ws on arduino
#define I2S_DI_IO (23)
#define DATA_BIT (16)
#define MODE_PIN (18) // Sel on arduino
DFRobot_Microphone microphone(I2S_SCK_IO, I2S_WS_IO, I2S_DI_IO);
char i2sReadrawBuff[100];

// WiFi variables
const char* ssid = "iPhone";
const char* password = "ztqzygzx";

// Something
const char* room = "2221";

void initWiFi() {              // Function for connecting to WiFi
  WiFi.mode(WIFI_STA);         // Starts in station mode. This means it will connect to an access point (WiFi)
  WiFi.begin(ssid, password);  // Connects to the given access point
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
}

void sendData(float data) {  // This function will send the measured data to the web server using HTTPClient
  if (WiFi.status() == WL_CONNECTED) {
    // Do the data sending
    HTTPClient http;                                     // Initiates the http library I think?
    WiFiClient client;                                   // Is this needed?
    http.begin(client, serverURL); 
    
    // Make a check to see if it actually is connected to the server before requesting to send
                          // Is client needed?
    http.addHeader("Content-Type", "application/json");  // I think this is like a note that specifies the data
    String httpRequestData = "{\"" + String(room) + "\":" + String(data, 2) +"";
     // This is json format. It has some name(idk what), and a decibel value. Decibel value should actively change in the loop.
    int httpResponseCode = http.POST(httpRequestData);
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    http.end();  // This probably ends something..?
    delay(250);
  } else {
    Serial.println("WiFi is not connected, cannot send data");
  }
}

void setup() {
  // Sound setup stuff
  Serial.begin(115200);
  pinMode(MODE_PIN, OUTPUT);
  digitalWrite(MODE_PIN, LOW);  //Configure the Microphone to Receive Left Channel Data
  //digitalWrite(MODE_PIN,HIGH);//Configure the Microphone to Receive Right Channel Data
  while (microphone.begin(SAMPLE_RATE, DATA_BIT) != 0) {
    Serial.println(" I2S init failed");
  }
  Serial.println("I2S init success");

  // WiFi connection
  initWiFi();
  Serial.println(WiFi.localIP());
}
/*
void convert_i2s(rawData) { // variable or  field 'convert_i2s' declared void???
  float sample_rate = 44.1;
  float reference_reading = 1000;
  float reference_dB = 90;
  measured_dB = 20*log(rawData/reference_reading);
  data = measured_dB;
  return data;
}
*/


void loop() {
  microphone.read(i2sReadrawBuff, 100);
  // Output Right Channel Data
  //Serial.println((int16_t)(i2sReadrawBuff[2]|i2sReadrawBuff[3]<<8));
  // Output Left Channel Data
  float rawData = (int16_t)(i2sReadrawBuff[0]|i2sReadrawBuff[1]<<8);
  //Serial.println((int16_t)(i2sReadrawBuff[0]|i2sReadrawBuff[1]<<8));
  convert_i2s(rawData); // I don't know what's wrong here
  Serial.println(data); // I don't know what's wrong here
  delay(250);
  //sendData(data);
}
