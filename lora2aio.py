#!/usr/bin/env python
import os
import re
import serial

# Import Adafruit IO REST client.
from Adafruit_IO import Client, Feed, RequestError

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = os.environ['AIOKEY']

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = os.environ['AIOUSER']

# Create an instance of the REST client.
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)


gps = serial.Serial("/dev/tty.usbserial-A700fiJM", baudrate=115200)

# Assign a location feed, if one exists already
try:
    location = aio.feeds('location')
except RequestError: # Doesn't exist, create a new feed
    feed = Feed(name="location")
    location = aio.create_feed(feed)

while True:
    line = gps.readline()
    match = re.search(r'Got: Packet - (\d+) RSSI (-\d+) Location (-?\d+\.\d+) (-?\d+\.\d+) (\d+\.\d+) at (\d{1,2}:\d{1,2}:\d{1,2}) .*', line)
    if match:
        lat = float(match.group(3))
        lon = float(match.group(4))
        alt = float(match.group(5))
        name = "%s-%s-%s" % (match.group(2), match.group(1), match.group(6))

        print "%f, %f, %f, %s" % (lat, lon, alt, name)

        # Send location data to Adafruit IO
        aio.send_location_data(location.key, name, lat, lon, alt)

        # Read the location data back from IO
        print('\nData Received by Adafruit IO Feed:\n')
        data = aio.receive(location.key)
        print('\tValue: {0}\n\tLat: {1}\n\tLon: {2}\n\tEle: {3}'
          .format(data.value, data.lat, data.lon, data.ele))
