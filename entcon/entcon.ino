#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <SPI.h>
#include <MFRC522.h>

const int RST_PIN = 4; // Reset pin
const int SS_PIN = 15; // Slave select pin

MFRC522 mfrc522(SS_PIN, RST_PIN); // Create MFRC522 instance
ESP8266WiFiMulti WiFiMulti;

const int RED = 5;
const int GREEN = 3;
const int BLUE = 1;

void red() {
    digitalWrite(RED, LOW);
    digitalWrite(GREEN, HIGH);
    digitalWrite(BLUE, HIGH);
//    Serial.print("RED\n");
}

void green() {
    digitalWrite(RED, HIGH);
    digitalWrite(GREEN, LOW);
    digitalWrite(BLUE, HIGH);
//    Serial.print("GREEN\n");
 
}

void blue() {
    digitalWrite(RED, HIGH);
    digitalWrite(GREEN, HIGH);
    digitalWrite(BLUE, LOW);
  //  Serial.print("BLUE\n");
}

void note(int tonec, int duration){
  tone(D2, tonec, duration);
  delay(duration+10);
}

int param = 0;
void play(String s){
  int i = -1;
  do {
    int prev_i = i+1;
    i = s.indexOf(' ', prev_i);
    int ci = s.indexOf(',',prev_i);
    int f = s.substring(prev_i,ci).toInt();
    int d;
    
    if (i != -1) {
      d = s.substring(ci+1,i).toInt();
    } else {
      d = s.substring(ci+1).toInt();
    }
    
     note(f,d);
      Serial.print(f);
      Serial.print('\t');
      Serial.print(d);
      Serial.print('\n');
  } while (i != -1);
}


void setup() {
  pinMode(RED, OUTPUT);
  digitalWrite(RED, HIGH);
  pinMode(GREEN, OUTPUT);
  digitalWrite(GREEN, HIGH);
  pinMode(BLUE, OUTPUT);
  digitalWrite(BLUE, HIGH);
  red();
 // Serial.begin(9600); // Initialize serial communications with the PC
  SPI.begin(); // Init SPI bus
  mfrc522.PCD_Init(); // Init MFRC522
  mfrc522.PCD_DumpVersionToSerial(); // Show details of PCD - MFRC522 Card Reader details
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP("ssid", "password");
}



void loop() {
  if ((WiFiMulti.run() == WL_CONNECTED)) {
    blue();
    WiFiClient client;
    // Look for new cards
    if ( ! mfrc522.PICC_IsNewCardPresent()) {
      return;
    }

    // Select one of the cards
    if ( ! mfrc522.PICC_ReadCardSerial()) {
      return;
    }
/*      // Dump debug info about the card; PICC_HaltA() is automatically called
  mfrc522.PICC_DumpToSerial(&(mfrc522.uid));*/
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
      int httpCode = http.GET();
      if (httpCode == 200) {      
        green();
        play(http.getString());
        blue();
        delay(1000);
      } else {
        red();
        tone(D2, 220, 100);
        delay(1000);
        blue();
      }
      Serial.print("[HTTP] Send\n");
      // start connection and send HTTP header
    } else {
      Serial.print("[HTTP] BAD\n");
    }
  }  else {
    red();
  }

}
