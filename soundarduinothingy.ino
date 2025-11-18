#include "DFrobot_MSM261.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <math.h>

#define SAMPLE_RATE (44100)
#define I2S_SCK_IO (19)
#define I2S_WS_IO (26)
#define I2S_DI_IO (23)
#define DATA_BIT (16)
#define MODE_PIN (18)
DFRobot_Microphone microphone(I2S_SCK_IO, I2S_WS_IO, I2S_DI_IO);
char i2sReadrawBuff[100];

const char* ssid = "iPhone";
const char* password = "ztqzygzx";
// Set this to the machine running Flask (your PC IP) and port 5000
const char* serverURL = "http://192.168.1.100:5000/arduino";

const char* room = "2221";

void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println();
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

float convert_i2s(float rawData) {
  // crude conversion to dB (requires calibration)
  float reference_reading = 1000.0; // adjust to calibrate
  float v = fabs(rawData);
  if (v < 1.0) v = 1.0; // avoid log(0)
  float measured_dB = 20.0 * log10(v / reference_reading) + 90.0; // offset if needed
  return measured_dB;
}

void sendData(float data) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String httpRequestData = String("{\"lokale\":") + String(room) + String(",\"db\":") + String(data, 2) + String("}");
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(httpRequestData);
    Serial.print("POST ");
    Serial.print(serverURL);
    Serial.print(" -> ");
    Serial.println(httpResponseCode);
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(MODE_PIN, OUTPUT);
  digitalWrite(MODE_PIN, LOW);
  while (microphone.begin(SAMPLE_RATE, DATA_BIT) != 0) {
    Serial.println("I2S init failed");
    delay(500);
  }
  Serial.println("I2S init success");
  initWiFi();
}

void loop() {
  microphone.read(i2sReadrawBuff, 100);
  float rawData = (int16_t)(i2sReadrawBuff[0] | (i2sReadrawBuff[1] << 8));
  float dB = convert_i2s(rawData);
  Serial.print("dB: ");
  Serial.println(dB);
  sendData(dB);
  delay(250);
}
