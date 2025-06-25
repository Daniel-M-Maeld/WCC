#include <Wire.h>
#include <Adafruit_BME280.h>
#include <SoftwareSerial.h>

SoftwareSerial BT(2, 3); // RX, TX (можно выбрать другие пины)
Adafruit_BME280 bme;

void setup() {
  BT.begin(9600);
  bme.begin(0x76);

}

void loop() {
  float temp = bme.readTemperature();
  float humidity = bme.readHumidity();
  float pressure = bme.readPressure() / 100.0F;

  // Отправка по Bluetooth
 BT.print(temp); BT.print(' '); BT.print(humidity); BT.print(' '); BT.println(pressure);

  delay(2000);
}