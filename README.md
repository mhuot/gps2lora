# gps2lora
I am trying to see if I can build a GPS-based tracking system that leverages LoRa. The initial setup that is working uses a Adafruit Feather M0 with RFM95 LoRa Radio and an Adafruit Ultimate GPS FeatherWing as the transmitter. talking to an Adafruit RFM95W LoRa Radio Transceiver Breakout connected va SPI to an Arduino Duemilanove which is in turn connected via USB to a Raspberry Pi Zero as the receiver. I am seeing with just a wire antenna(7.8 cm soldered to the ANT pad) on the receiver for LoRa seeing a range of 90+ meters semi-obstructed.

# Parts List
Adafruit Ultimate GPS FeatherWing
Adafruit Feather M0 with RFM95 LoRa Radio - 900MHz
Adafruit RFM95W LoRa Radio Transceiver Breakout - 868 or 915 MHz - RadioFruit
Antennas GPS Antenna 3-5V 28dB 5 meter SMA
Arduino Duemilanove
Rasberry Pi Zero

# Not working RPi wiring
| Board Label |  Board pin  |  Jumper Color | RPi Pin | Rpi Label | Note     |
|-------|-------|--------|-----|-------|-------|
| 3v | 1 | red | 17	| |		
| gnd | 2 | black | 25 | gnd | |		
| en | 3	| | | |				
| g0 | 4 | grey | 7 |  | #define RF_IRQ_PIN RPI_V2_GPIO_P1_07    // IRQ on GPIO4 so P1 connector pin #7 |
| sck | 5 | green | 23 | sclk | 	
| miso | 6 | yellow | 19 | miso | |	
| mosi | 7 | orange | 21 | mosi | |		
| cs | 8 | blue | 22 | | #define RF_CS_PIN  RPI_V2_GPIO_P1_22    // Slave Select on GPIO25 so P1 connector pin #22 |
| rst | 9 | white | 11 | | #define RF_RST_PIN RPI_V2_GPIO_P1_11    // Reset on GPIO17 so P1 connector pin #11 |

# Working wiring with Arduino Duemilanove 
| Board Label |  Board pin  |  Jumper Color | Arduino Pin | Arduino Label |
|-------------|-------------|---------------|-------------|---------------|
|          3v |           1 |           red |             |           3v3 |
|         gnd |           2 |         black |             |           Gnd |
|          en |           3	|               |             |               |				
|          g0 |           4 |          grey |           3 |     Digital 3 |
|         sck |           5 |         green |          13 |    Digital 13 |	
|        miso |           6 |        yellow |          12 |    Digital 12 |	
|        mosi |           7 |        orange |          11 |    Digital 11 |		
|          cs |           8 |          blue |           4 |     Digital 4 | 
|         rst |           9 |         white |           2 |     Digital 2 | 

# Resources
https://www.hackster.io/idreams/getting-started-with-lora-fd69d1
http://www.airspayce.com/mikem/arduino/RadioHead/

