// Feather9x_TX
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client (transmitter)
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example Feather9x_RX

#include <SPI.h>
#include <RH_RF95.h>
#include <Adafruit_GPS.h>

HardwareSerial* mySerial = &Serial1;
Adafruit_GPS GPS(mySerial);


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
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

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

  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
  GPS.sendCommand(PGCMD_ANTENNA);
  delay(1000);
  mySerial->println(PMTK_Q_RELEASE);
}

int16_t packetnum = 0;  // packet counter, we increment per xmission

void loop()
{

  GPS.read();
  if (GPS.newNMEAreceived()) {
    if (!GPS.parse(GPS.lastNMEA()))
      return;
  }

  if (GPS.fix) {
    String latdegrees = String(GPS.latitudeDegrees, 4);
    String longdegrees = String(GPS.longitudeDegrees, 4);
    String gpshour = String(GPS.hour);
    String gpsminute = String(GPS.minute);
    String gpsseconds = String(GPS.seconds);
    String gpsquality = String(GPS.fixquality);
    String message = String("Location " + latdegrees + " " + longdegrees + " at " + gpshour + ":" + gpsminute + ":" + gpsseconds + " quality " + gpsquality);
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
  }
}
