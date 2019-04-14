#include <SPI.h>
#include <RH_RF95.h>
#include <Adafruit_GPS.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_FeatherOLED.h>

Adafruit_FeatherOLED oled = Adafruit_FeatherOLED();

#define BUTTON_A 9 //OLED
#define BUTTON_B 6 //OLED
#define BUTTON_C 5 //OLED
#define LED      13 //OLED

#if (SSD1306_LCDHEIGHT != 32)
#error("Height incorrect, please fix Adafruit_SSD1306.h!");
#endif

#define GPSSerial Serial1
Adafruit_GPS GPS(&GPSSerial);

#define PMTK_SET_NMEA_UPDATE_10SEC "$PMTK220,10000*2F"
// This timer is for the GPS readings.  Don't mess with it.
uint32_t timer = millis();

/* for feather m0  */
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3

// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 915.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

void setup()
{
  Serial.begin(9600);

  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  // by default, we'll generate the high voltage from the 3.3v line internally! (neat!)
  //  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);  // initialize with the I2C addr 0x3C (for the 128x32)
  //  display.display();

  delay(100);

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    while (1);
  }

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    while (1);
  }

  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);

  // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
  GPS.begin(9600);

  // Turn on RMC (recommended minimum) and GGA (fix data) including altitude
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);

  // Set the update rate
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate

  delay(1000);

  pinMode(BUTTON_A, INPUT_PULLUP);
  pinMode(BUTTON_B, INPUT_PULLUP);
  pinMode(BUTTON_C, INPUT_PULLUP);

  oled.init();
  oled.setBatteryVisible(true);
  oled.println("gps2lora is ready");
  oled.display(); // actually display all of the above

}

int16_t packetnum = 0;  // packet counter, we increment per xmission
int16_t fixattempt = 0;
bool screen1 = true;

void loop()
{

  // read data from the GPS in the 'main loop'
  char c = GPS.read();
  // if a sentence is received, we can check the checksum, parse it...
  if (GPS.newNMEAreceived()) {
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences!
    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
    if (!GPS.parse(GPS.lastNMEA())) // this also sets the newNMEAreceived() flag to false
      return; // we can fail to parse a sentence in which case we should just wait for another
  }
  // if millis() or timer wraps around, we'll just reset it
  if (timer > millis()) timer = millis();

  // approximately every 2 seconds or so, print out the current stats
  if (millis() - timer > 6000) {
    timer = millis(); // reset the timer

    packetnum++;
    fixattempt++;
    String nodename = String("NODE1");
    String packet = String(packetnum);
    String latdegrees = String(GPS.latitudeDegrees, 4);
    String longdegrees = String(GPS.longitudeDegrees, 4);
    String gpshour = String(GPS.hour);
    String gpsminute = String(GPS.minute);
    String gpsseconds = String(GPS.seconds);
    String gpsday = GPS.day;
    String GPS.month;
    String GPS.year;
    String gpssatellites = String(GPS.satellites);
    String gpsquality = String(GPS.fixquality);
    String rssi = String(rf95.lastRssi(), DEC);
    String gpsalt = String(GPS.altitude);
    String message = String(nodename + " GPS Fail " + String(fixattempt)+ " RSSI " + rssi);
    String displaytext = message;

    if (gpshour.length() =1) {
      gpshour = "0" + gpshour
    }
    if (gpsminute.length() =1) {
      gpsminute = "0" + gpsminute
    }
    if (gpsseconds.length() =1) {
      gpsseconds = "0" + gpsseconds
    }
    if (GPS.fix) {
      message = String(nodename + " " + packet + " RSSI " + rssi + " Location " + latdegrees + " " + longdegrees + " " + gpsalt + " at " + gpshour + ":" + gpsminute + ":" + gpsseconds + " satellites " + gpssatellites + " quality " + gpsquality);
      fixattempt = 0;
      if (screen1) {
        displaytext = String(nodename + " packet " + packet + "\nLoc " + latdegrees + " " + longdegrees + "\nAlt " + gpsalt + "m");
        screen1 = false;
      } else {
        displaytext = String(nodename + " packet " + packet + "\nSatellites " + gpssatellites + "\nRSSI " + rssi + " dBm");
        screen1 = true;
      }
    }

    Serial.println(message);

    int message_len = message.length() + 1;

    char radiopacket[message_len];
    message.toCharArray(radiopacket, message_len);
    delay(10);
    rf95.send((uint8_t *)radiopacket, message_len);

    delay(10);
    rf95.waitPacketSent();
    // Now wait for a reply
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);

    if (rf95.waitAvailableTimeout(1000)) {
      delay(1000); // Wait 1 second between transmits, could also 'sleep' here!
    }
    oled.clearDisplay();

    // get the current voltage of the battery from
    // one of the platform specific functions below
    float battery = getBatteryVoltage();

    // update the battery icon
    oled.setBattery(battery);
    oled.renderBattery();

    oled.println(displaytext);
    oled.display();
  }
}

#if defined(ARDUINO_ARCH_SAMD) || defined(__AVR_ATmega32U4__)

// m0 & 32u4 feathers
#define VBATPIN A7

float getBatteryVoltage() {

  float measuredvbat = analogRead(VBATPIN);

  measuredvbat *= 2;    // we divided by 2, so multiply back
  measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
  measuredvbat /= 1024; // convert to voltage

  return measuredvbat;

}

#elif defined(ESP8266)

// esp8266 feather
#define VBATPIN A0

float getBatteryVoltage() {

  float measuredvbat = analogRead(VBATPIN);

  measuredvbat *= 2;    // we divided by 2, so multiply back
  measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
  measuredvbat /= 1024; // convert to voltage

  return measuredvbat;

}

#elif defined(ARDUINO_STM32_FEATHER)

// wiced feather
#define VBATPIN PA1

float getBatteryVoltage() {

  pinMode(VBATPIN, INPUT_ANALOG);

  float measuredvbat = analogRead(VBATPIN);

  measuredvbat *= 2;         // we divided by 2, so multiply back
  measuredvbat *= 0.80566F;  // multiply by mV per LSB
  measuredvbat /= 1000;      // convert to voltage

  return measuredvbat;

}

#else

// unknown platform
float getBatteryVoltage() {
  Serial.println("warning: unknown feather. getting battery voltage failed.");
  return 0.0F;
}

#endif
