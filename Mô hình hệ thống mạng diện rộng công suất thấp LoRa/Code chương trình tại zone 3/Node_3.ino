#include "LoRa_E32.h"
#include <DHT.h>
#include <avr/sleep.h>
#include <avr/interrupt.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include "DFRobot_BME280.h"
#include <LiquidCrystal_I2C.h>
#include <Adafruit_MAX31865.h>
#define TdsSensorPin A5        // Chân analog kết nối cảm biến TDS
#define VREF 5.0               // Điện áp tham chiếu của ADC (5V)
#define SCOUNT 100             // Số lượng mẫu đọc mỗi lần
int analogBuffer[SCOUNT];      // Mảng lưu giá trị ADC đọc được
int analogBufferTemp[SCOUNT];  // Mảng phụ để lọc trung vị
int analogBufferIndex = 0;     // Chỉ số lưu mẫu hiện tại
int copyIndex = 0;             // Chỉ số dùng để sao chép mảng
float averageVoltage = 0;      // Giá trị điện áp trung bình sau lọc
float tdsValue = 0;            // Giá trị TDS sau khi tính toán
#define M0 4                   // PD4 tương ứng với chân 4 trên Mega 2560
#define M1 5                   // PD5 tương ứng với chân 5
#define AUX 19
#define DHTPIN 7
#define DHTTYPE DHT21
#define SensorPin A7  // Đầu vào cảm biến pH
#define van1 22
#define van2 26
#define van3 24
#define maybom1 30
#define maybom2 31
#define maybom3 29
#define maybom4 28
#define RREF 430.0
typedef DFRobot_BME280_IIC BME;  // ******** use abbreviations instead of full names ********
#define ArrayLength 40
float Offset = 0.0;  // Bạn sẽ chỉnh giá trị này sau khi hiệu chuẩn
int pHArray[ArrayLength];
// 100.0 for PT100, 1000.0 for PT1000
#define RNOMINAL 100.0
BME bme(&Wire, 0x77);
#define SEA_LEVEL_PRESSURE 1015.0f
// Khởi tạo LCD với địa chỉ 0x27, LCD 16x2
LiquidCrystal_I2C lcd(0x27, 16, 2);
Adafruit_MAX31865 thermo = Adafruit_MAX31865(10, 6, 8, 12);
DHT dht(DHTPIN, DHTTYPE);
LoRa_E32 e32ttl1(&Serial2, AUX, M1, M0);
void setup() {
  Serial.begin(9600);
  Serial2.begin(9600);
  pinMode(van1, OUTPUT);
  pinMode(van2, OUTPUT);
  pinMode(van3, OUTPUT);
  pinMode(maybom1, OUTPUT);
  pinMode(maybom2, OUTPUT);
  pinMode(maybom3, OUTPUT);
  pinMode(maybom4, OUTPUT);
  pinMode(TdsSensorPin, INPUT);
  Wire.begin();  // Khởi tạo I2C (trên Mega: SDA 20, SCL 21)
  dht.begin();
  // Khởi tạo LCD
  pinMode(M0, OUTPUT);
  pinMode(M1, OUTPUT);
  pinMode(AUX, INPUT);
  e32ttl1.begin();
  diachi();
  delay(50);
  digitalWrite(M0, LOW);   // Set 2 chân M0 và M1 xuống LOW
  digitalWrite(M1, HIGH);  // để hoạt động ở chế độ Normal
  attachInterrupt(digitalPinToInterrupt(AUX), wakeUp, FALLING);
  analogReference(DEFAULT);
  lcd.init();
  lcd.backlight();
  thermo.begin(MAX31865_3WIRE);
  bme.reset();
  while (bme.begin() != BME::eStatusOK) {
    Serial.println("bme begin faild");
    printLastOperateStatus(bme.lastOperateStatus);
    delay(2000);
  }
  lcd.setCursor(0, 0);
          lcd.print("OK");
}
struct LoRaData {
  int deviceId;
  char manual[10];
};
void loop() {
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);  // Chọn chế độ Power-down
  sleep_enable();                       // Cho phép ngủ
  sleep_cpu();                          // CPU vào trạng thái ngủ
  sleep_disable();                      // Tắt chế độ ngủ
  String input = Serial2.readStringUntil('\n');
  Serial.println(input);
  docdbme280();
  hethongph(input);
}
void hethongph(String input) {
  e32ttl1.begin();
  StaticJsonDocument<128> docc;
  DeserializationError error = deserializeJson(docc, input);
  if (error) {
    Serial.print("Lỗi phân tích JSON: ");
    Serial.println(error.c_str());
    delay(50);
  } else {
    LoRaData data;
    data.deviceId = docc["i"];
    String datareceive = docc["d"];
    datareceive.toCharArray(data.manual, sizeof(data.manual));
    Serial.println("ok");
    if (datareceive.length() > 0) {
      digitalWrite(maybom4, HIGH);
      delay(11000);
      digitalWrite(maybom4, LOW);
      delay(50);
      char command = datareceive.charAt(0);
      switch (command) {
        case 'Manual1':
          lcd.clear();
          // Hiển thị lên LCD
          lcd.setCursor(0, 0);
          lcd.print("Dang do pH mau 1");
          docph(van1);
          digitalWrite(van1, LOW);
          Serial.println("Mau1");
          lcd.clear();
          delay(50);
          break;
        case 'Manual2':
          lcd.clear();
          // Hiển thị lên LCD
          lcd.setCursor(0, 0);
          lcd.print("Dang do pH mau 2");
          docph(van2);
          digitalWrite(van2, LOW);
          Serial.println("Mau2");
          lcd.clear();
          delay(50);
          break;
        case 'Manual3':
          lcd.clear();
          // Hiển thị lên LCD
          lcd.setCursor(0, 0);
          lcd.print("Dang do pH mau 3");
          docph(van3);
          digitalWrite(van3, LOW);
          Serial.println("Mau3");
          lcd.clear();
          delay(50);
          break;
        case 'Auto':
          lcd.clear();
          // Hiển thị lên LCD
          lcd.setCursor(0, 0);
          lcd.print("Dang do pH mau 1");
          docph(van1);
          digitalWrite(van1, LOW);
          lcd.clear();
          // Hiển thị lên LCD
          lcd.setCursor(0, 0);
          lcd.print("Dang do pH mau 2");
          docph(van2);
          digitalWrite(van2, LOW);
          lcd.clear();
          // Hiển thị lên LCD
          lcd.setCursor(0, 0);
          lcd.print("Dang do pH mau 3");
          docph(van3);
          digitalWrite(van3, LOW);
          Serial.println("Ca 3 mau");
          lcd.clear();
          digitalWrite(maybom3, HIGH);
          delay(10000);
          digitalWrite(maybom3, LOW);
          delay(50);
          delay(50);
          break;
        case 'Maunal4':
          lcd.clear();
          // Hiển thị lên LCD
          lcd.setCursor(0, 0);
          lcd.print("Dang ve sinh");
          digitalWrite(maybom3, HIGH);
          delay(9000);
          digitalWrite(maybom3, LOW);
          lcd.clear();
          delay(50);
          break;
      }
    }
  }
}
char xdong[] = "\n";
// Software SPI: (CS, DI, DO, CLK)
void nhietdonuoc() {
  float temp = thermo.temperature(RNOMINAL, RREF);
  StaticJsonDocument<128> doc;
  doc["i"] = 5;
  doc["w"] = temp;
  char bupphe[128];
  serializeJson(doc, bupphe);
  Serial.println(bupphe);
  strcat(bupphe, xdong);
  waitAUX();
  ResponseStatus rsz = e32ttl1.sendFixedMessage(0, 3, 23, bupphe, strlen(bupphe));
  waitAUX();
  Serial.println(rsz.getResponseDescription());
}
float tdsValue3 = 0;  // Biến lưu giá trị TDS lần thứ 10
void docph(int pin) {
  digitalWrite(pin, HIGH);
  digitalWrite(maybom1, HIGH);
  delay(14000);
  digitalWrite(pin, LOW);
  digitalWrite(maybom1, LOW);
  //docph
  phsensor(pin);
  digitalWrite(maybom4, HIGH);
  delay(11000);
  digitalWrite(maybom4, LOW);
  delay(50);
  digitalWrite(maybom2, HIGH);
  delay(13000);
  digitalWrite(maybom2, LOW);
  delay(50);
  digitalWrite(maybom4, HIGH);
  delay(11000);
  digitalWrite(maybom4, LOW);
  delay(50);
}
char temperature1[8];
char humidity[8];
void wakeUp() {}
void docdbme280() {
  float temp = bme.getTemperature();
  uint32_t press = bme.getPressure();                       //Pa (apsuatkhiquyen)
  float alti = bme.calAltitude(SEA_LEVEL_PRESSURE, press);  //m (docao tuong doi)
  float humi = bme.getHumidity();
  StaticJsonDocument<128> doc;
  doc["i"] = 5;
  doc["t"] = temp;
  doc["h"] = humi;
  doc["e"] = press;  //do ph da dinh nghia ph
  doc["a"] = alti;
  char bupphe[128];
  serializeJson(doc, bupphe);
  Serial.println(bupphe);
  strcat(bupphe, xdong);
  waitAUX();
  ResponseStatus rsz = e32ttl1.sendFixedMessage(0, 3, 23, bupphe, strlen(bupphe));
  waitAUX();
  Serial.println(rsz.getResponseDescription());
  delay(50);
}
void phsensor(int pin) {
  int mau;
  if (pin == 22) {
    mau = 1;
  } else if (pin == 26) {
    mau = 2;
  } else if (pin == 24) {
    mau = 3;
  }
  for (int i = 0; i < ArrayLength; i++) {
    pHArray[i] = analogRead(SensorPin);
    delay(20);  // Đợi giữa mỗi mẫu để ổn định
  }
  float voltage = averageArray(pHArray, ArrayLength) * 5.0 / 1024.0;
  float pHValue = 3.5 * voltage + Offset;
  char buf[6];
  char cat[4];
  dtostrf(pHValue, 4, 2, buf);  // Ghi kết quả ra chuỗi
  for (int readCount = 1; readCount <= 3; readCount++) {
    // Đọc (SCOUNT) mẫu analog
    for (int i = 0; i < SCOUNT; i++) {
      analogBuffer[i] = analogRead(TdsSensorPin);
      delay(40);  // delay để mô phỏng lấy mẫu mỗi 40ms
    }
    // Copy sang mảng tạm
    for (int i = 0; i < SCOUNT; i++) {
      analogBufferTemp[i] = analogBuffer[i];
    }
    float tempwater = 0; // Khai báo biến ngoài vòng lặp để lưu giá trị
    for(int i=0;i<10;i++){
       float rawTemp = thermo.temperature(RNOMINAL, RREF);
      tempwater = round(rawTemp * 100) / 100.0;
      delay(40);
    }
    // Tính trung vị và chuyển đổi sang TDS
    float averageVoltage = getMedianNum(analogBufferTemp, SCOUNT) * VREF / 1024.0;
    float compensationCoefficient = 1.0 + 0.02 * (tempwater - 25.0);
    float compensationVoltage = averageVoltage / compensationCoefficient;
    float tdsValue = (133.42 * compensationVoltage * compensationVoltage * compensationVoltage
                      - 255.86 * compensationVoltage * compensationVoltage
                      + 857.39 * compensationVoltage)
                     * 0.5;
    
    // Lưu giá trị lần thứ 3
    if (readCount == 3) {
      Serial.print("TDS Value: ");
      Serial.print(tdsValue, 0);
      Serial.println(" ppm");
      tdsValue3 = tdsValue;
      dtostrf(tdsValue3, 3, 0, cat);
      StaticJsonDocument<128> doc;
      doc["i"] = 5;
      doc["m"] = mau;
      doc["p"] = buf;
      doc["tds"] = cat;
      doc["w"]=tempwater;
      char bupphe[128];
      serializeJson(doc, bupphe);
      Serial.println(bupphe);
      strcat(bupphe, xdong);
      waitAUX();
      ResponseStatus rsz = e32ttl1.sendFixedMessage(0, 3, 23, bupphe, strlen(bupphe));
      waitAUX();
      Serial.println(rsz.getResponseDescription());
      delay(50);
    }
  }
}
void printLastOperateStatus(BME::eStatus_t eStatus) {
  switch (eStatus) {
    case BME::eStatusOK: Serial.println("everything ok"); break;
    case BME::eStatusErr: Serial.println("unknow error"); break;
    case BME::eStatusErrDeviceNotDetected: Serial.println("device not detected"); break;
    case BME::eStatusErrParameter: Serial.println("parameter error"); break;
    default: Serial.println("unknow status"); break;
  }
}
void waitAUX() {
  unsigned long startTime = millis();
  while (digitalRead(AUX) == LOW && (millis() - startTime <= 5000)) {
    delay(20);  // Chờ đến khi AUX HIGH hoặc hết 5 giây
  }
  delay(2);
}
// Hàm tính giá trị trung bình của mảng (loại bỏ max/min)
double averageArray(int* arr, int number) {
  if (number <= 0) return 0;
  long sum = 0;
  int minVal = arr[0], maxVal = arr[0];
  for (int i = 0; i < number; i++) {
    sum += arr[i];
    if (arr[i] < minVal) minVal = arr[i];
    if (arr[i] > maxVal) maxVal = arr[i];
  }
  sum -= (minVal + maxVal);           // Loại bỏ giá trị lớn nhất và nhỏ nhất
  return (double)sum / (number - 2);  // Trả về giá trị trung bình
}
int getMedianNum(int bArray[], int iFilterLen) {
  int bTab[iFilterLen];
  for (byte i = 0; i < iFilterLen; i++)
    bTab[i] = bArray[i];
  int i, j, bTemp;
  for (j = 0; j < iFilterLen - 1; j++) {
    for (i = 0; i < iFilterLen - j - 1; i++) {
      if (bTab[i] > bTab[i + 1]) {
        bTemp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = bTemp;
      }
    }
  }
  if ((iFilterLen & 1) > 0)
    bTemp = bTab[(iFilterLen - 1) / 2];
  else
    bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  return bTemp;
}
void diachi() {
  e32ttl1.begin();
  ResponseStructContainer c;
  c = e32ttl1.getConfiguration();
  Configuration configuration = *(Configuration*)c.data;
  configuration.ADDL = 2;
  configuration.ADDH = 0;
  configuration.CHAN = 23;
  configuration.SPED.uartBaudRate = UART_BPS_9600;        // 9600 bps
  configuration.SPED.airDataRate = AIR_DATA_RATE_010_24;  // 2.4 kbps
  configuration.SPED.uartParity = MODE_00_8N1;            // 8N1
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
