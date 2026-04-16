#include <DHT.h>

#define DHTPIN D3
#define DHTTYPE DHT11
#define ACS_PIN A0
#define BUZZER D5

DHT dht(DHTPIN, DHTTYPE);

// 🔥 Thresholds (only for labeling, NOT buzzer)
float tempThreshold = 35.0;
float lowRiskMin = 1.0;
float highRiskMin = 2.0;

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);
}

void loop() {

  // 🌡️ Read temperature
  float temp = dht.readTemperature();
  if (isnan(temp)) temp = 25.0;

  // 🔌 Read current
  int adcValue = analogRead(ACS_PIN);
  float voltage = adcValue * (1.0 / 1023.0);
  float current = voltage * 5.0;

  // 📊 STATUS (for dataset only)
  String status;

  if (current > highRiskMin) {
    status = "HIGH";
  }
  else if (current >= lowRiskMin) {
    status = "LOW";
  }
  else {
    status = "NORMAL";
  }

  // 🔥 🔴 ML-BASED BUZZER CONTROL (FROM PYTHON)
  if (Serial.available()) {
    char signal = Serial.read();

    if (signal == '1') {
      digitalWrite(BUZZER, HIGH);  // ML says anomaly
    } 
    else if (signal == '0') {
      digitalWrite(BUZZER, LOW);   // ML says normal
    }
  }

  // 📊 SEND DATA TO PYTHON
  Serial.print(temp);
  Serial.print(",");
  Serial.print(current);
  Serial.print(",");
  Serial.println(status);

  delay(2000);
}