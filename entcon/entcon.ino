#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <SPI.h>
#include <MFRC522.h>

const int RST_PIN = 5; // Reset pin
const int SS_PIN = 15; // Slave select pin

MFRC522 mfrc522(SS_PIN, RST_PIN); // Create MFRC522 instance
ESP8266WiFiMulti WiFiMulti;

void setup() {
  Serial.begin(9600); // Initialize serial communications with the PC
  SPI.begin(); // Init SPI bus
  mfrc522.PCD_Init(); // Init MFRC522
  mfrc522.PCD_DumpVersionToSerial(); // Show details of PCD - MFRC522 Card Reader details
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP("ssid", "password");
}



void loop() {
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    return;
  }
  if ((WiFiMulti.run() == WL_CONNECTED)) {

    WiFiClient client;

    HTTPClient http;
    unsigned long uidDec, uidDecTemp;
    uidDec = 0;
    // Выдача серийного номера метки.
    for (byte i = 0; i < mfrc522.uid.size; i++)
    {
      uidDecTemp = mfrc522.uid.uidByte[i];
      uidDec = uidDec * 256 + uidDecTemp;
    }
    if (http.begin(client, "http://51.38.152.65:8080/scud?id=" + String(uidDec))) { // HTTP

      tone(D2, 440, 100);
      delay(100);
      Serial.print("[HTTP] Send\n");
      // start connection and send HTTP header
      int httpCode = http.GET();
    } else {
      Serial.print("[HTTP] BAD\n");
    }
  }


  // Dump debug info about the card; PICC_HaltA() is automatically called
  mfrc522.PICC_DumpToSerial(&(mfrc522.uid));
}
