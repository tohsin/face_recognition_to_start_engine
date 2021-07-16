#include <LiquidCrystal.h>
int Contrast = 75;
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = { 0, -1 };
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void setup() {
  analogWrite(6, Contrast);
  lcd.begin(16, 2);
  Serial.begin(115200);
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readString();
    writeLcd(getValue(data, ':', 0), getValue(data, ':', 1));
  }
}
  void writeLcd(String line1, String line2) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(line1);
    lcd.setCursor(0, 1);
    lcd.print(line2);
    delay(500);
  }
