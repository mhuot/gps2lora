#!/usr/bin/env python
import os
import re
import serial

# Import Adafruit IO REST client.
from Adafruit_IO import Client, Feed, RequestError

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
if 'AIOKEY' in os.environ:
	ADAFRUIT_IO_KEY = os.environ['AIOKEY']
else:
	print("AIOKEY is not set")
	ADAFRUIT_IO_KEY = raw_input("Please provide an Adafruit IO Key: ")


# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
if 'AIOUSER' in os.environ:
	ADAFRUIT_IO_USERNAME = os.environ['AIOUSER']
else:
	print("AIOUSER is not set")
	ADAFRUIT_IO_USERNAME = raw_input("Please provide an Adafruit user name: ")

if 'GPSSERIAL' in os.environ:
	GPSSERIAL = os.environ['GPSSERIAL']
else:
	print("GPSSERIAL is not set")
	GPSSERIAL = raw_input("Please provide a serial device: ")

gps = serial.Serial(GPSSERIAL, baudrate=115200)

# Create an instance of the REST client.
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Assign a location feed, if one exists already
try:
    location = aio.feeds('location')
except RequestError: # Doesn't exist, create a new feed
    feed = Feed(name="location")
    location = aio.create_feed(feed)

# Assign a rssi feed, if one exists already
try:
    rssifeed = aio.feeds('rssi')
except RequestError: # Doesn't exist, create a new feed
    rssifeed = aio.create_feed(Feed(name='rssi'))

while True:
    line = gps.readline()
    match = re.search(r'Got: (NODE\d) (\d+) RSSI (-\d+) Location (-?\d+\.\d+) (-?\d+\.\d+) (\d+\.\d+) at (\d{1,2}:\d{1,2}:\d{1,2}) .*', line)
    if match:
        lat = float(match.group(4))
        lon = float(match.group(5))
        alt = float(match.group(6))
        rssi = match.group(3)
        name = "%s-%s-%s" % (rssi, match.group(2), match.group(7))

        print "%f, %f, %f, %s" % (lat, lon, alt, name)

        # Send location data to Adafruit IO
        aio.send_location_data(location.key, name, lat, lon, alt)
        aio.send(rssifeed.key, rssi)

        # Read the location data back from IO
        print('\nData Received by Adafruit IO Feed:\n')
        data = aio.receive(location.key)
        print('\tValue: {0}\n\tLat: {1}\n\tLon: {2}\n\tEle: {3}'
          .format(data.value, data.lat, data.lon, data.ele))
