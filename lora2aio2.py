#!/usr/bin/env python3
import json
import os
import re
#import serial
# Import Python System Libraries
import time
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import RFM9x
import adafruit_rfm9x

# Import Adafruit IO REST client.
from Adafruit_IO import Client, Feed, RequestError

homedir = os.path.expanduser('~')

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
if 'AIOKEY' in os.environ and 'AIOUSER' in os.environ:
    ADAFRUIT_IO_USERNAME = os.environ['AIOUSER']
    ADAFRUIT_IO_KEY = os.environ['AIOKEY']
else:
    try:
        aiojson = open('%s/.aio.json' % homedir)
        aioinfo = json.load(aiojson)
        print(aioinfo)
        ADAFRUIT_IO_USERNAME = aioinfo['AIOUSER']
        ADAFRUIT_IO_KEY = aioinfo['AIOKEY']
    except:
        print("AIOKEY is not set")
        ADAFRUIT_IO_KEY = input("Please provide an Adafruit IO Key: ")
        print("AIOUSER is not set")
        ADAFRUIT_IO_USERNAME = input("Please provide an Adafruit user name: ")

print('AIOKEY %s, AIOUSER %s' % ( ADAFRUIT_IO_KEY,  ADAFRUIT_IO_USERNAME ))

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Create an instance of the REST client.
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Assign a location feed, if one exists already
try:
    location = aio.feeds('location')
except RequestError: # Doesn't exist, create a new feed
    location = aio.create_feed(Feed(name="location"))

# Assign a rssi feed, if one exists already
try:
    rssifeed = aio.feeds('rssi')
except RequestError: # Doesn't exist, create a new feed
    rssifeed = aio.create_feed(Feed(name='rssi'))

# Assign a satellites feed, if one exists already
try:
    satfeed = aio.feeds('satellites')
except RequestError: # Doesn't exist, create a new feed
    satfeed = aio.create_feed(Feed(name='satellites'))

# Assign a lpminutes feed, if one exists already
try:
    lpminutesfeed = aio.feeds('lpminutes')
except RequestError: # Doesn't exist, create a new feed
    lpminutesfeed = aio.create_feed(Feed(name='lpminutes'))
    aio.send(lpminutesfeed.key, 0)

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
rfm9x.tx_power = 23
prev_packet = None
lastpacket = 0
lpminutes = 1

display.fill(0)
display.text('RasPi LoRa', 35, 0, 1)
display.show()

while True:
    packet = None
    # draw a box to clear the image

    # check for packet rx
    packet = rfm9x.receive()
    if packet is None:
        #display.show()
        #display.text('- Waiting for PKT -', 15, 20, 1)
        print("%s - Waiting for packet %s" % (time.asctime( time.localtime(time.time()) ),lastpacket))
        if lastpacket > 60:
            if lastpacket > (60 * lpminutes):
                display.fill(0)
                display.text("No RX in %s min" % lpminutes, 0, 0, 1)
                print("No packets received in %s minutes" % lpminutes)
                lpminutes = lpminutes + 1
                aio.send(lpminutesfeed.key, lpminutes)
                display.show()
        lastpacket = lastpacket + 1
    else:
        rssi = rfm9x.rssi
        lastpacket = 0
        if (lpminutes > 1):
            lpminutes = 1
            aio.send(lpminutesfeed.key, 0)
        # Display the packet text and rssi
        display.fill(0)
        prev_packet = packet
        try:
            packet_text = str(prev_packet, "utf-8")
        except:
            print("Failed to read packet string - RSSI: %s" % rssi)
            display.fill(0)
            display.text("Failed to read packet string - RSSI: %s" % rssi, 0, 0, 1)
            display.show()
            continue
        #print(packet_text)
        time.sleep(3)
        # NODE1 1700 RSSI 0 Location 44.8857 -93.1373 309.30 at 2:19:52 satellites 7 quality 1
        # NODE1 1687 RSSI 0 GPS no fix
        match = re.search(r'(NODE\d) -?(\d+) RSSI (-?\d+) Location (-?\d+\.\d+) (-?\d+\.\d+) (\d+\.\d+) at (\d{1,2}:\d{1,2}:\d{1,2}) satellites (\d+) .*', packet_text)
        if match:
            lat = float(match.group(4))
            lon = float(match.group(5))
            ele = float(match.group(6))
            sats = int(match.group(8))
            rawtime = match.group(7).split(":")
            utctime = "%s:%s:%s" % (rawtime[0].rjust(2,"0"),rawtime[1].rjust(2,"0"),rawtime[2].rjust(2,"0"))
            name = "%s-%s-%s" % (rssi, match.group(2), utctime)
            locdata = {
                "lat" : lat,
                "lon" : lon,
                "ele" : ele,
                "created_at" : None
            }

            locjson = json.dumps(locdata)

            print("RSSI: %s - %s" % (rssi,locjson))

            display.text('RX: ', 0, 0, 1)
            display.text("RSSI: %s" % rssi, 25, 0, 1)
            # Send location data to Adafruit IO
            aio.send(location.key, name, locdata)
            aio.send(rssifeed.key, rssi)
            aio.send(satfeed.key, sats)

            # Read the location data back from IO
            #print('\nData Received by Adafruit IO Feed:\n')
            #data = aio.receive(location.key)
            #print('\tValue: {0}\n\tLat: {1}\n\tLon: {2}\n\tEle: {3}'
            #  .format(data.value, data.lat, data.lon, data.ele))
        else:
            print(packet_text)
            display.fill(0)
            display.text("Failed to read packet string - RSSI: %s" % rssi, 0, 0, 1)
            display.show()
            match = re.search(r'(NODE\d) (\d+) RSSI (-?\d+) GPS no fix', packet_text)
            if match:
                    aio.send(rssifeed.key, rssi)
                    data = aio.receive(rssifeed.key)
                    print("Sent RSSI: %s" % rssi)
                    aio.send(satfeed.key, 0)
    display.show()
    time.sleep(0.1)
