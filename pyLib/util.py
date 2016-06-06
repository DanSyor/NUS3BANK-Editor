# coding: utf-8
from __future__ import absolute_import, division, print_function
import struct

def readByte(file):
	return struct.unpack(b"B", file.read(1))[0]

def readu16be(file):
	return struct.unpack(b">H", file.read(2))[0]

def readu16le(file):
	return struct.unpack(b"<H", file.read(2))[0]
	
def readu32be(file):
	return struct.unpack(b">I", file.read(4))[0]

def readu32le(file):
	return struct.unpack(b"<I", file.read(4))[0]

def readfloatbe(file):
	return struct.unpack(b">f", file.read(4))[0]

def readfloatle(file):
	return struct.unpack(b"<f", file.read(4))[0]


	
'''def getString(file):
	result = ""
	tmpChar = file.read(1)
	while ord(tmpChar) != 0:
		result += tmpChar
		tmpChar =file.read(1)
	return result'''