#include <Arduino.h>

#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>

#include <ESP8266HTTPClient.h>

#include <WiFiClient.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

//#include <SPI.h>
//#define BME_SCK 14
//#define BME_MISO 12
//#define BME_MOSI 23
//#define BME_CS 15
Adafruit_BME280 bme;

ESP8266WiFiMulti WiFiMulti;
SoftwareSerial mySerial(D5, D6);
byte* buff;
void setup() {
  buff = new byte[9];
  Serial.begin(115200);
  // Serial.setDebugOutput(true);

  Serial.println();
  Serial.println();
  Serial.println();

  for (uint8_t t = 4; t > 0; t--) {
    Serial.printf("[SETUP] WAIT %d...\n", t);
    Serial.flush();
    delay(1000);
  }

  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP("ssid", "password");
  pinMode(0, OUTPUT);
  mySerial.begin(9600);

    bool status;

  // default settings
  // (you can also pass in a Wire library object like &Wire2)
  status = bme.begin();  
  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
   // while (1);
  }
}


void loop() {
  // wait for WiFi connection
  if ((WiFiMulti.run() == WL_CONNECTED)) {

    WiFiClient client;

    HTTPClient http;

    Serial.print("[HTTP] begin...\n");
    if (http.begin(client, "51.38.152.65",8080)) {  // HTTP


      Serial.print("[HTTP] GET...\n");
      // start connection and send HTTP header
      int httpCode = http.GET();

      // httpCode will be negative on error
      if (httpCode > 0) {
        // HTTP header has been send and Server response header has been handled
        Serial.printf("[HTTP] GET... code: %d\n", httpCode);
        
        // file found at server
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
          String payload = http.getString();
          Serial.println(payload);
          auto ix = payload.indexOf("LON");
          Serial.printf("%d\n",ix != -1);
          if (ix != -1){
            digitalWrite(0, LOW);
          } else {
            digitalWrite(0, HIGH);
          }
        }
      } else {
        Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
        
      }

      http.end();
    } else {
      Serial.printf("[HTTP} Unable to connect\n");
    }
  }
  mySerial.write(0xFF);
  mySerial.write(0x01);
  mySerial.write(0x86);
  mySerial.write((byte)0x00);
  mySerial.write((byte)0x00);
  mySerial.write((byte)0x00);
  mySerial.write((byte)0x00);
  mySerial.write((byte)0x00);
  mySerial.write(0x79);
  delay(1000);
  int aq = 0,ix=0;
  while (mySerial.available())
      {
          buff[ix++] = mySerial.read();
          if ((ix > 0 && buff[0] != 0xFF) ||
              (ix > 1 && buff[1] != 0x86))
              {
                ix = 0;
                continue;
              }
          if (ix > 8){
            aq = 256*buff[2]+buff[3];
            ix = 0;
          }


      }
int t = bme.readTemperature();
int p = bme.readPressure();
int h = bme.readHumidity();      
if ((WiFiMulti.run() == WL_CONNECTED)) {

    WiFiClient client;

    HTTPClient http;
    
      if (http.begin(client, "http://51.38.152.65:8080/meas?aq="+String(aq)+"&t="+String(t)+"&p="+String(p)+"&h="+String(h))) {  // HTTP


      Serial.print("[HTTP] Send\n");
      // start connection and send HTTP header
      int httpCode = http.GET();
    } else{
      Serial.print("[HTTP] BAD\n");
    }
}

  
  delay(9000);
}
