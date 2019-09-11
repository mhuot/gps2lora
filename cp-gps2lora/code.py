import time
import board
import busio
import digitalio
from adafruit_tinylora.adafruit_tinylora import TTN, TinyLoRa
import adafruit_gps

RX = board.RX
TX = board.TX
uart = busio.UART(TX, RX, baudrate=9600, timeout=30)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b'PMTK220,1000')
last_print = time.monotonic()
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs = digitalio.DigitalInOut(board.RFM9X_CS)
irq = digitalio.DigitalInOut(board.RFM9X_D0)
rst = digitalio.DigitalInOut(board.RFM9X_RST)

devaddr = bytearray([0x26, 0x02, 0x1B, 0xDF])

nwkey = bytearray([0x16, 0x58, 0xD7, 0x2F, 0xFE, 0x8D, 0xC1, 0xC2,
                   0xB7, 0xBB, 0x30, 0x72, 0xB6, 0x44, 0xB6, 0xF1])

app = bytearray([0x42, 0xDA, 0x9D, 0xC2, 0x41, 0x50, 0x41, 0x00,
                 0x7B, 0xF7, 0x32, 0x71, 0xB6, 0xC7, 0xEF, 0x73])

ttn_config = TTN(devaddr, nwkey, app, country='US')

lora = TinyLoRa(spi, cs, irq, rst, ttn_config)

data = bytearray(4)

while True:
    gps.update()
    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        if not gps.has_fix:
            print('Waiting for fix...')
            continue
        print('=' * 40)  # Print a separator line.
        print('Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}'.format(
            gps.timestamp_utc.tm_mon,   # Grab parts of the time from the
            gps.timestamp_utc.tm_mday,  # struct_time object that holds
            gps.timestamp_utc.tm_year,  # the fix time.  Note you might
            gps.timestamp_utc.tm_hour,  # not get all data like year, day,
            gps.timestamp_utc.tm_min,   # month!
            gps.timestamp_utc.tm_sec))
        print('Latitude: {0:.6f} degrees'.format(gps.latitude))
        print('Longitude: {0:.6f} degrees'.format(gps.longitude))
        print('Fix quality: {}'.format(gps.fix_quality))
        if gps.satellites is not None:
            print('# satellites: {}'.format(gps.satellites))
        if gps.altitude_m is not None:
            print('Altitude: {} meters'.format(gps.altitude_m))
        if gps.speed_knots is not None:
            print('Speed: {} knots'.format(gps.speed_knots))
        if gps.track_angle_deg is not None:
            print('Track angle: {} degrees'.format(gps.track_angle_deg))
        if gps.horizontal_dilution is not None:
            print('Horizontal dilution: {}'.format(gps.horizontal_dilution))
        if gps.height_geoid is not None:
            print('Height geo ID: {} meters'.format(gps.height_geoid))
        
        temp_val = gps.latitude
        humid_val = gps.longitude
        print('Temperature: %0.2f C' % temp_val)
        print('relative humidity: %0.1f %%' % humid_val)

        data[0] = (temp_val >> 8) & 0xff
        data[1] = temp_val & 0xff
        data[2] = (humid_val >> 8) & 0xff
        data[3] = humid_val & 0xff
        
        print('Sending packet...')
        lora.send_data(data, len(data), lora.frame_counter)
        print('Packet Sent!')
        led.value = True
        lora.frame_counter += 1
        time.sleep(5)
        led.value = False
