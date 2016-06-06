# coding: utf-8
from __future__ import absolute_import, division, print_function
import pyLib.six as six
import sys
from pyLib.util import *
import os
import string
import zlib

class strg(object):
	name = b""
	size = 0
	offset = 0
	def __init__(self, id):
		self.id = id

class nus3bank(object):
	contents = []
	propOffset = 0
	binfOffset = 0
	grpOffset = 0
	dtonOffset = 0
	toneOffset = 0
	junkOffset = 0
	packOffset = 0
	def __init__(self, size):
		self.size = size

class tone(object):
	name = b""
	ext = b""
	packOffset = 0
	size = 0
	def __init__(self, offset, metaSize):
		self.offset = offset
		self.metaSize = metaSize

def extract(nus3Path,outfolder):
    nus3 = open(nus3Path, u'rb+')
    if nus3.read(4) != b"NUS3":
        nus3.seek(0)
        data = nus3.read()
        nus3_decom = zlib.decompress(data)
        nus3.close()
        nus3 = open(string.replace(nus3Path, u".nus3bank", u"_decompressed.nus3bank"), u"wb+")
        nus3.write(nus3_decom)
        nus3.seek(0)
        data = None
        nus3_decom = None
    else:
        nus3.seek(0)
    
    assert nus3.read(4) == b"NUS3"
    size = readu32le(nus3)

    bank = nus3bank(size)
    assert nus3.read(8) == b"BANKTOC ", u"Not a bank archive!"
    tocSize = readu32le(nus3)
    contentCount = readu32le(nus3)
    offset = 0x14 + tocSize
    for i in range(contentCount):
        content = nus3.read(4)
        contentSize = readu32le(nus3)
        if content == b"PROP":
            propOffset = offset
            propSize = contentSize
        elif content == b"BINF":
            binfOffset = offset
            binfSize = contentSize
        elif content == b"GRP b":
            grpOffset = offset
            grpSize = contentSize
        elif content == b"DTON":
            dtonOffset = offset
            dtonSize = contentSize
        elif content == b"TONE":
            toneOffset = offset
            toneSize = contentSize
        elif content == b"JUNK":
            junkOffset = offset
            junkSize = contentSize
        elif content == b"MARK":
            markOffset = offset
            markSize = contentSize
        elif content == b"PACK":
            packOffset = offset
            packSize = contentSize
        else:
            print(u"Unknown content type " + six.text_type(content))
        offset += 8 + contentSize

    nus3.seek(binfOffset)
    assert nus3.read(4) == b"BINF"
    assert readu32le(nus3) == binfSize
    assert readu32le(nus3) == 0
    assert readu32le(nus3) == 3
    binfStringSize = readByte(nus3)
    binfString = nus3.read(binfStringSize-1)
    # if len(sys.argv) < 3:
        # outfolder = binfString
    # else:
        # outfolder = sys.argv[2]
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)
    # playlistPath = os.path.join(outfolder,'playlist.m3u')
    tracks = []
    nus3.seek(1,1)
    #print binfString
    padding = (binfStringSize + 1) % 4
    #print padding
    if padding == 0:
        pass
    else:
        nus3.seek(abs(padding-4), 1)
    nus3ID = readu32le(nus3)
    #print hex(nus3ID)

    nus3.seek(toneOffset)
    assert nus3.read(4) == b"TONE"
    assert readu32le(nus3) == toneSize
    toneCount = readu32le(nus3)
    print(u"%s:%s:\"%s\"" % (nus3ID, hex(nus3ID), binfString))
    tones = []
    for i in range(toneCount):
        offset = readu32le(nus3) + toneOffset + 8
        metaSize = readu32le(nus3)
        tones.append(tone(offset, metaSize))
	
    for i in range(toneCount):
        if tones[i].metaSize <= 0xc:
            continue
        nus3.seek(tones[i].offset+6)
        tempByte = readByte(nus3)
        if tempByte > 9 or tempByte == 0:
            nus3.seek(5, 1)
        else:
            nus3.seek(1,1)
        stringSize = readByte(nus3)
    #	print hex(nus3.tell())
        tones[i].name = nus3.read(stringSize - 1).decode('utf-8')
        nus3.seek(1,1)
        print(u"\t" + hex(i) + u":" + tones[i].name)
        padding = (stringSize + 1) % 4
        if padding == 0:
            nus3.seek(4, 1)
        else:
            nus3.seek(abs(padding-4) + 4, 1)
    #	assert readu32le(nus3) == 8
        nus3.seek(4,1)
        tones[i].packOffset = readu32le(nus3)
        tones[i].size = readu32le(nus3)
        print((tones[i].packOffset))
    #	print hex(tones[i].packOffset) + b" - b" + hex(tones[i].size)
        if tones[i].packOffset < 0xffffffff:
            nus3.seek(packOffset + 8 + tones[i].packOffset)
            tones[i].ext = u".idsp"

            track = os.path.join(outfolder, hex(i) + u"-" + tones[i].name + tones[i].ext)
            
            # outSound = open(outfolder + b"/" + hex(i) + b"-" + tones[i].name + tones[i].ext, b"wb")
            outSound = open(track,u"wb")
            outSound.write(nus3.read(tones[i].size))
            outSound.close()
            tracks.append(track)
            
            # playlist=open(playlistPath,"a")
            # playlist.write(hex(i) + b"-" + tones[i].name + tones[i].ext+"\n")
            # playlist.close()
        
    nus3.close()
    return tracks