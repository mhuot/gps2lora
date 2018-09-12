#!/usr/bin/env python
import serial
import re

gps = serial.Serial("/dev/tty.usbserial-A700fiJM", baudrate=115200)

while True:
	line = gps.readline()
	match = re.search(r'Got: Packet - (\d+) RSSI (-\d+) Location (\d+\.\d+) (-\d+\.\d+) at (\d{1,2}:\d{1,2}:\d{1,2}) .*', line)
	if match:
		lat = float(match.group(3))
		lon = float(match.group(4))
		name = "%s-%s-%s" % (match.group(2), match.group(1), match.group(5))

		print "%f, %f, %s" % (lat, lon, name)

		with open ("position.kml", "w") as pos:
			pos.write('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
 xmlns:gx="http://www.google.com/kml/ext/2.2">
 <Placemark>
  <name>Python Live GPS</name>
  <description>Hello World</description>
  <Point>
    <coordinates>%f,%f</coordinates>
  </Point>
</Placemark>
</kml>
'''  % (lon, lat))