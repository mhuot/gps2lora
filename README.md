# lora2gps

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

