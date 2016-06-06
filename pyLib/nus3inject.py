# coding: utf-8
from __future__ import absolute_import, division, print_function
import pyLib.six as six
import sys
from pyLib.util import *
import os
import struct
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
    data = None
    def __init__(self, offset, metaSize):
        self.offset = offset
        self.metaSize = metaSize

def inject(nusPath,replacePath,hexID):
    nus3 = open(nusPath, 'rb+')
    if nus3.read(4) != b"NUS3":
        nus3.seek(0)
        data = nus3.read()
        nus3_decom = zlib.decompress(data)
        nus3.close()
        nus3 = open(string.replace(nusPath, u'.nus3bank', u'_decompressed.nus3bank'), u'wb+')
        nus3.write(nus3_decom)
        nus3.seek(0)
        data = None
        nus3_decom = None
    else:
        nus3.seek(0)

    assert nus3.read(4) == b"NUS3"

    all = False    
    if hexID == u'all':
        toneID = 0xffff
        all = True
    else:
        toneID = int(hexID, 0)
    print((hex(toneID)))

    replacementSoundSize = os.path.getsize(replacePath)
    mainPackOffset = 0


    size = readu32le(nus3)
    #nus3.seek(-4,1)
    #nus3.write(struct.pack("<I", size + replacementSoundSize))
    #nus3.write(struct.pack("<I", 0))



    bank = nus3bank(size)
    assert nus3.read(8) == b"BANKTOC ", u'Not a bank archive!'
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
            packSizeOffset = nus3.tell() - 4
            #nus3.seek(-4, 1)
            #nus3.write(struct.pack("<I", packSize + replacementSoundSize))
        else:
            print(u'Unknown content type ' + six.text_type(content))
        offset += 8 + contentSize

    nus3.seek(binfOffset)
    assert nus3.read(4) == b"BINF"
    assert readu32le(nus3) == binfSize
    assert readu32le(nus3) == 0
    assert readu32le(nus3) == 3
    binfStringSize = readByte(nus3)
    binfString = nus3.read(binfStringSize-1)

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
        if all == True:
            toneID = i
        if tones[i].metaSize <= 0xc:
            continue
        nus3.seek(tones[i].offset+6)
        tempByte = readByte(nus3)
        if tempByte > 9 or tempByte == 0:
            nus3.seek(5, 1)
        else:
            nus3.seek(1,1)
        stringSize = readByte(nus3)
    #    print hex(nus3.tell())
        tones[i].name = nus3.read(stringSize - 1)
        nus3.seek(1,1)
        #print b"\t" + hex(i) + b":" + tones[i].name
        padding = (stringSize + 1) % 4
        if padding == 0:
            nus3.seek(4, 1)
        else:
            nus3.seek(abs(padding-4) + 4, 1)
    #    assert readu32le(nus3) == 8
        nus3.seek(4,1)
        tones[i].packOffset = readu32le(nus3)
        tones[i].size = readu32le(nus3)
        if i == toneID:
            mainPackOffset = tones[i].packOffset
            origSoundSize = tones[i].size
            nus3.seek(-4, 1)
            tones[i].size = replacementSoundSize
            #nus3.write(struct.pack("<I", replacementSoundSize))
            #nus3.seek(packOffset + 8 + tones[i].packOffset + tones[i].size)
            #print(hex(nus3.tell()))
            #remainingPackData = nus3.read(packSize - tones[i].packOffset - tones[i].size)
            #nus3.seek(packOffset + 8 + tones[i].packOffset)
            #print(hex(nus3.tell()))
            replacementSound = open(replacePath, 'rb')
            tones[i].data = replacementSound.read()
            #nus3.write(replacementSound.read())
            #nus3.write(remainingPackData)
            #finalOffset = nus3.tell()
        else: 
            nus3.seek(packOffset + 8 + tones[i].packOffset)
            tones[i].data = nus3.read(tones[i].size)
        
    currentPackOffset = 0
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
    #    print hex(nus3.tell())
        tones[i].name = nus3.read(stringSize - 1)
        nus3.seek(1,1)
        #print b"\t" + hex(i) + b":" + tones[i].name
        padding = (stringSize + 1) % 4
        if padding == 0:
            nus3.seek(4, 1)
        else:
            nus3.seek(abs(padding-4) + 4, 1)
    #    assert readu32le(nus3) == 8
        nus3.seek(4,1)
        tones[i].packOffset = currentPackOffset
        nus3.write(struct.pack(b"<I", currentPackOffset))
        nus3.write(struct.pack(b"<I", tones[i].size))
        nus3.seek(packOffset + 8 + tones[i].packOffset)
        nus3.write(tones[i].data)
        tones[i].data = None
        currentPackOffset += tones[i].size
        #tones[i].packOffset = readu32le(nus3)
        #tones[i].size = readu32le(nus3)
        b"""
        if 0xffffffff > tones[i].packOffset > mainPackOffset:
            nus3.seek(-8, 1)
            print ("Tone %s at offset %s" % (hex(i), hex(nus3.tell())))
            nus3.write(struct.pack("<I", tones[i].packOffset + replacementSoundSize - origSoundSize))
        b"""
    finalOffset = nus3.tell()
    nus3.seek(packOffset + 4)
    #nus3.write(struct.pack("<I", packSize + replacementSoundSize - origSoundSize))    
    nus3.write(struct.pack(b"<I", currentPackOffset))    
    nus3.seek(packSizeOffset)    
    #nus3.write(struct.pack("<I", packSize + replacementSoundSize - origSoundSize))    
    nus3.write(struct.pack(b"<I", currentPackOffset))    
    nus3.seek(4)
    #nus3.write(struct.pack("<I", bank.size + replacementSoundSize - origSoundSize))    
    nus3.write(struct.pack(b"<I", bank.size + currentPackOffset - packSize))    

    replacementSound.close()    
    nus3.seek(0)
    finalNus3 = nus3.read(finalOffset)
    nus3.close()
    #newNus3 = open(string.replace(nusPath, b".nus3bank", b".edit_nus3bank"), b"wb")
    newNus3 = open(nusPath, u'wb')
    newNus3.write(finalNus3)
    newNus3.close()