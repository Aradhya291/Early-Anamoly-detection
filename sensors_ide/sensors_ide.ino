#include <DHT.h>

#define DHTPIN D3
#define DHTTYPE DHT11
#define GAS_PIN A0

DHT dht(DHTPIN, DHTTYPE);

void setup() {

  Serial.begin(9600);
  dht.begin();

}

void loop() {

  float temperature = dht.readTemperature();

  int gas_value = analogRead(GAS_PIN);

  Serial.print(temperature);
  Serial.print(",");
  Serial.println(gas_value);

  delay(5000);

}

