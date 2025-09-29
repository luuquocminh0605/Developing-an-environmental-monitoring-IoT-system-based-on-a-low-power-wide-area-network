#include "LoRa_E32.h"
#include <DHT.h>
#include <avr/sleep.h>
#include <avr/interrupt.h>
#include <ArduinoJson.h>
#define M0 4   // PD4 tương ứng với chân 4 trên Mega 2560
#define M1 5   // PD5 tương ứng với chân 5
#define AUX 19  
#define DHTPIN 7
#define DHTTYPE DHT21
DHT dht(DHTPIN, DHTTYPE);
LoRa_E32 e32ttl1(&Serial2, AUX, M1, M0);
void setup() {
  Serial.begin(9600);
  Serial2.begin(9600);
  dht.begin();
  pinMode(M0, OUTPUT);
  pinMode(M1, OUTPUT);
  pinMode(AUX, INPUT);
  e32ttl1.begin();
  diachi();
  delay(50);
  digitalWrite(M0, LOW);   
  digitalWrite(M1, HIGH); 
  attachInterrupt(digitalPinToInterrupt(AUX), wakeUp, FALLING);
  analogReference(DEFAULT);
}
char temperature[8];
char humidity[8];
char buffer[20];  // Khai báo chuỗi buffer với kích thước đủ lớn
char buffer1[20];
void loop() {
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);  // Chọn chế độ Power-down
 sleep_enable();                   // Cho phép ngủ
  sleep_cpu();                      // CPU vào trạng thái ngủ
  sleep_disable();                  // Tắt chế độ ngủ
  String input = Serial2.readStringUntil('\n');
    Serial.println(input);
  tem_hum();
}
char xdong[] = "\n";
char buf[6];
void wakeUp() {}
void tem_hum() {
  e32ttl1.begin();
  float t = dht.readTemperature();  // Đọc nhiệt độ
  float h = dht.readHumidity();     // Đọc độ ẩm
  dtostrf(t, 5, 2, temperature);    // 5 ký tự tổng cộng, 2 chữ số thập phân
  dtostrf(h, 5, 2, humidity);
  StaticJsonDocument<128> doc;
  doc["i"] = 4;
  doc["t"] = temperature;
  doc["h"] = humidity;
  char buffer[128];
  serializeJson(doc, buffer);
  Serial.println(buffer);
  strcat(buffer,xdong);
  waitAUX();
  ResponseStatus rs = e32ttl1.sendFixedMessage(0, 3, 23, buffer, strlen(buffer));
  waitAUX();
  Serial.println(rs.getResponseDescription());
  delay(50);
}
void waitAUX() {
  unsigned long startTime = millis();
  while (digitalRead(AUX) == LOW && (millis() - startTime <= 5000)) {
   delay(100);// Chờ đến khi AUX HIGH hoặc hết 5 giây
  }
  delay(100);
}
void diachi() {
  e32ttl1.begin();
  ResponseStructContainer c;
  c = e32ttl1.getConfiguration();
  Configuration configuration = *(Configuration*)c.data;
  configuration.ADDL = 7;
  configuration.ADDH = 0;
  configuration.CHAN = 23;
  configuration.SPED.uartBaudRate = UART_BPS_9600;      // 9600 bps
  configuration.SPED.airDataRate = AIR_DATA_RATE_010_24;  // 2.4 kbps
  configuration.SPED.uartParity = MODE_00_8N1;      // 8N1
  configuration.OPTION.fixedTransmission = FT_FIXED_TRANSMISSION;
  configuration.OPTION.ioDriveMode = IO_D_MODE_PUSH_PULLS_PULL_UPS;  // Push-pull
  configuration.OPTION.wirelessWakeupTime = WAKE_UP_250;             // 250ms
  configuration.OPTION.fec = FEC_0_OFF;                              // Tắt FEC
  configuration.OPTION.transmissionPower = POWER_20;
  e32ttl1.setConfiguration(configuration, WRITE_CFG_PWR_DWN_SAVE);
  printParameters(configuration);
  c.close();
  // ---------------------------
}
void printParameters(struct Configuration configuration) {
  Serial.println("----------------------------------------");
  Serial.print(F("HEAD : "));
  Serial.print(configuration.HEAD, BIN);
  Serial.print(" ");
  Serial.print(configuration.HEAD, DEC);
  Serial.print(" ");
  Serial.println(configuration.HEAD, DEC);
  Serial.println(F(" "));
  Serial.print(F("AddH : "));
  Serial.println(configuration.ADDH, DEC);
  Serial.print(F("AddL : "));
  Serial.println(configuration.ADDL, DEC);
  Serial.print(F("Chan : "));
  Serial.print(configuration.CHAN, DEC);
  Serial.print(" -> ");
  Serial.println(configuration.getChannelDescription());
  Serial.println(F(" "));
  Serial.print(F("SpeedParityBit     : "));
  Serial.print(configuration.SPED.uartParity, BIN);
  Serial.print(" -> ");
  Serial.println(configuration.SPED.getUARTParityDescription());
  Serial.print(F("SpeedUARTDatte  : "));
  Serial.print(configuration.SPED.uartBaudRate, BIN);
  Serial.print(" -> ");
  Serial.println(configuration.SPED.getUARTBaudRate());
  Serial.print(F("SpeedAirDataRate   : "));
  Serial.print(configuration.SPED.airDataRate, BIN);
  Serial.print(" -> ");
  Serial.println(configuration.SPED.getAirDataRate());
  Serial.print(F("OptionTrans        : "));
  Serial.print(configuration.OPTION.fixedTransmission, BIN);
  Serial.print(" -> ");
  Serial.println(configuration.OPTION.getFixedTransmissionDescription());
  Serial.print(F("OptionPullup       : "));
  Serial.print(configuration.OPTION.ioDriveMode, BIN);
  Serial.print(" -> ");
  Serial.println(configuration.OPTION.getIODroveModeDescription());
  Serial.print(F("OptionWakeup       : "));
  Serial.print(configuration.OPTION.wirelessWakeupTime, BIN);
  Serial.print(" -> ");
  Serial.println(configuration.OPTION.getWirelessWakeUPTimeDescription());
  Serial.print(F("OptionFEC          : "));
  Serial.print(configuration.OPTION.fec, BIN);
  Serial.print(" -> ");
  Serial.println(configuration.OPTION.getFECDescription());
  Serial.print(F("OptionPower        : "));
  Serial.print(configuration.OPTION.transmissionPower, BIN);
  Serial.print(" -> ");
  Serial.println(configuration.OPTION.getTransmissionPowerDescription());
  Serial.println("----------------------------------------");
}
void printModuleInformation(struct ModuleInformation moduleInformation) {
  Serial.println("----------------------------------------");
  Serial.print(F("HEAD BIN: "));
  Serial.print(moduleInformation.HEAD, BIN);
  Serial.print(" ");
  Serial.print(moduleInformation.HEAD, DEC);
  Serial.print(" ");
  Serial.println(moduleInformation.HEAD, HEX);
  Serial.print(F("Freq.: "));
  Serial.println(moduleInformation.frequency, HEX);
  Serial.print(F("Version  : "));
  Serial.println(moduleInformation.version, HEX);
  Serial.print(F("Features : "));
  Serial.println(moduleInformation.features, HEX);
  Serial.println("----------------------------------------");
}
