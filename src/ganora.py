# coding: utf-8
#!/usr/bin/env python
'''
    File name: ganora.py
    Author: Jingun Jung
    Date created: 10/06/2016
    Date last modified: 10/06/2016
    Python Version: 2.7
'''
import time
import sys
import spidev
import serial

def remap( x, oMin, oMax, nMin, nMax ):
	#range check
	if oMin == oMax:
		print "Warning: Zero input range"
		return None

	if nMin == nMax:
		print "Warning: Zero output range"
		return None

	#check reversed input range
	reverseInput = False
	oldMin = min( oMin, oMax )
	oldMax = max( oMin, oMax )
	if not oldMin == oMin:
		reverseInput = True

	#check reversed output range
	reverseOutput = False   
	newMin = min( nMin, nMax )
	newMax = max( nMin, nMax )
	if not newMin == nMin :
		reverseOutput = True

	portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
	if reverseInput:
		portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

	result = portion + newMin
	if reverseOutput:
		result = newMax - portion
	return result

spi = spidev.SpiDev()
spi.open(0, 0)
port = serial.Serial(
        port='/dev/ttyAMA0',
        baudrate=19200,
        timeout=3)

olddata1 = -255
olddata2 = -255
while True:
	try:
	        resp1 = spi.xfer2([0x68, 0x00])
	        resp2 = spi.xfer2([0x78, 0x00])
	        data1 = (resp1[0] * 256 + resp1[1]) & 0x3ff
	        data2 = (resp2[0] * 256 + resp2[1]) & 0x3ff
		redata1 = remap(data1, 0, 1023, 0, 255)
		redata2 = remap(data2, 0, 1023, 0, 255)
		updatedata1 = olddata1 - redata1
		updatedata2 = olddata2 - redata2

		if (updatedata1 > 5 or updatedata1 < -5) and (updatedata2 > 5 or updatedata2 < -5):
			port.write("A" + str(10000 + redata1) + str(10000 + redata2))
			olddata1 = redata1
			olddata2 = redata2
			print "Send left and right motor : " + str(redata1) + ", " + str(redata2)
			if port.read(3) == "Ack":
				print "OK"
		else:
			if updatedata1 > 5 or updatedata1 < -5:
				port.write("L" + str(10000 + redata1))
				olddata1 = redata1
				print "Send left motor : " + str(redata1)
				if port.read(3) == "Ack":
					print "OK"

			if updatedata2 > 5 or updatedata2 < -5:
				port.write("R" + str(10000 + redata2))
				olddata2 = redata2
				print "Send right mortor :" + str(redata2)
				if port.read(3) == "Ack":
					print "OK"

		time.sleep(0.2)
	except KeyboardInterrupt:
		spi.close()
		port.close()
		sys.exit(0)

