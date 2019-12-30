#include <LiquidCrystal.h>
#include <DHT.h>
#include <SoftwareSerial.h>
 
#define DHTPIN 12
#define DHTTYPE DHT22
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);
DHT dht(DHTPIN, DHTTYPE);

#define BTN_UP   1
#define BTN_DOWN 2
#define BTN_LEFT 3
#define BTN_RIGHT 4
#define BTN_SELECT 5
#define BTN_NONE 10
int detectButton() {
  int keyAnalog =  analogRead(A0);
  if (keyAnalog < 100) {
    // Значение меньше 100 – нажата кнопка right
    return BTN_RIGHT;
  } else if (keyAnalog < 200) {
    // Значение больше 100 (иначе мы бы вошли в предыдущий блок результата сравнения, но меньше 200 – нажата кнопка UP
    return BTN_UP;
  } else if (keyAnalog < 400) {
    // Значение больше 200, но меньше 400 – нажата кнопка DOWN
    return BTN_DOWN;
  } else if (keyAnalog < 600) {
    // Значение больше 400, но меньше 600 – нажата кнопка LEFT
    return BTN_LEFT;
  } else if (keyAnalog < 800) {
    // Значение больше 600, но меньше 800 – нажата кнопка SELECT
    return BTN_SELECT;
  } else {
    // Все остальные значения (до 1023) будут означать, что нажатий не было
    return BTN_NONE;
  }
}
byte* buff;
void setup() {
  Serial.begin(115200);
  buff = new byte[9];
// mySerial.begin(9600);
  pinMode(11, OUTPUT);
  digitalWrite(11, LOW);
  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);
  pinMode(A1, OUTPUT);
//  pinMode(A2, OUTPUT);
  pinMode(A3, OUTPUT);
 //   digitalWrite(A2, HIGH);
  digitalWrite(A3, LOW);
  lcd.begin(16, 2);
   dht.begin();

      pinMode(3, OUTPUT);
tone(3, 440, 250);
delay(250);
tone(3, 880, 250);
delay(250);
tone(3, 1960, 250);
delay(250);
}
byte dim = 128;
int cycle = 3600;
bool showCycle = false;
int soil;
int cycleNo = 0;
float h;
float t;

size_t ix = 0;
void loop() {
  lcd.setCursor(0, 0);
  if (cycleNo%2 == 0) {
    h = dht.readHumidity();
    t = dht.readTemperature();
  }
  
  lcd.print("T");
  lcd.print(t);
    lcd.print("C   ");
  lcd.setCursor(9, 0);
  lcd.print("H");
  lcd.print(h);
  lcd.print("%         ");
  analogWrite(10, dim);
  int button = detectButton();
  switch (button) {
    case BTN_UP:
      if (dim < 255)
        ++dim;
      delay(10);
      break;
    case BTN_DOWN:
      if (dim > 0 )
        --dim;
      delay(10);
      break;
    case BTN_SELECT:
      cycleNo = 30;
      break;
    default:
      if (cycleNo == 0) {
        digitalWrite(A1, HIGH);
      }
    /*  if (cycleNo == 30) {
        
        digitalWrite(A2, HIGH);
      }
      if (cycleNo <= 30) {
        aq = cycleNo;
      }*/
      delay(1000);
      if (cycleNo == 0) {
        soil = analogRead(A5);
        digitalWrite(A1, LOW);
       // digitalWrite(A2, LOW);
        cycleNo = cycle;
      }

      --cycleNo;
      break;
  }
  if (soil > 900){
      tone(3, 440, 1000);
      delay(1000);
      cycleNo = 0;  
  }
        lcd.setCursor(0, 1);
      lcd.print("S ");
      lcd.print(soil);
      lcd.print("  ");
      lcd.setCursor(9, 1);
      lcd.print("REM");
      lcd.print(cycleNo);
      lcd.print("       ");


}
