# coding: utf-8
from __future__ import absolute_import, division, print_function
import pyLib.six as six
import pyLib.xis as xis
if six.PY3:
    from tkinter import *
    from tkinter.filedialog import *
    import tkinter.font as tkFont
    import tkinter.messagebox as tkMessageBox
    from configparser import SafeConfigParser
    print (u"Python3 imports")
else:
    from Tkinter import *
    from tkFileDialog import *
    import tkFont
    import tkMessageBox
    from ConfigParser import SafeConfigParser
    print (u"Python2 imports")
import os
import sys
import subprocess
import shutil
import glob
import traceback
from shutil import copyfile
import time
import pyLib.nus3bank
import pyLib.nus3inject

# class NullWriter(object):
    # def write(self, value): pass

# if not (os.isatty(1) and os.isatty(2)):
# sys.stdout = sys.stderr = open('log-'+unicode(time.strftime('%Y-%m-%d-%H-%M-%S'))+'-'+unicode(os.getpid())+'.txt', 'w')
if sys.executable.endswith(u"pythonw.exe") or sys.executable.endswith(u"pythonw3.exe") or sys.executable.endswith(u"pythonw2.exe"):
    # sys.stdout = sys.stderr = NullWriter()
    sys.stdout = sys.stdout = None

appVer = u'2.20-pre'
appName = u"NUS3BANK Editor " + appVer    

# you should add a github updater
# they are pretty easy in python
# basically just use urllib2 and check the newest file version
# if it is greater then copy the file over
# you can write over a python file during it's runtime btw

# directory where application files are stored
n3beDir = xis.decode(os.path.dirname(os.path.realpath(__file__)))

# exe dependencies
vgmstream = u'"' + os.path.join(os.path.join(n3beDir,u'exeLib'), u'vgmstream.exe') + u'"'
ffmpeg    = u'"' + os.path.join(os.path.join(n3beDir,u'exeLib'), u'ffmpeg.exe')    + u'"'
dspadpcm  = u'"' + os.path.join(os.path.join(n3beDir,u'exeLib'), u'dspadpcm.exe')  + u'"'
revb      = u'"' + os.path.join(os.path.join(n3beDir,u'exeLib'), u'revb.exe')      + u'"'

# extensions of replacement sounds
known_ext      = [u'.wav',
                  u'.ogg',
                  u'.brstm',
                  u'.bctsm',
                  u'.bfstm',
                  u'.idsp',
                  u'.dsp',
                  u'.hps']
known_stand    = [u'.wav',
                  u'.ogg',
                  u'.mp3',
                  u'.flac',
                  u'.mp4',
                  u'.m4a',
                  u'.flv']
known_vgm      = [u'.brstm',
                  u'.bctsm',
                  u'.bfstm',
                  u'.idsp',
                  u'.dsp',
                  u'.hps']
known_ext_plus = [u'.wav',
                  u'.ogg',
                  u'.brstm',
                  u'.bctsm',
                  u'.bfstm',
                  u'.idsp',
                  u'.dsp',
                  u'.hps',
                  u'.mp3',
                  u'.flac',
                  u'.mp4',
                  u'.m4a',
                  u'.flv']
known_work_ext = [u'.m3u',
                  u'.wav',
                  u'.ogg',
                  u'.brstm',
                  u'.bctsm',
                  u'.bfstm',
                  u'.idsp',
                  u'.dsp',
                  u'.hps',
                  u'.mp3',
                  u'.flac',
                  u'.mp4',
                  u'.m4a',
                  u'.flv']

# colors for file path at the bottom of the window
color_f_default = u'black'
color_b_default = u'#bebebe'
color_f_null    = u'white'
color_b_null    = u'black'
color_f_change  = u'black'
color_b_change  = u'#aaccff'

# colors for listbox elements
color_l_default = u'black'
color_l_change  = u'blue'
color_l_bg = [u'white',u'#eeeeff']

change = False

# def readConfig():
    # parser = SafeConfigParser()
    # parser.read('nus3bankeditor.ini')
# readConfig()

def getExtension(path):
    if os.path.isdir(path):
        return u''
    lastDot = path.rfind(u'.')
    if lastDot < 0 or lastDot >= len(path):
        return u''
    else:
        ext = path[lastDot:].lower()
        if len(ext) > 1:
            return ext
        else:
            return u''

def getBatSetVal(batString,var):
    return int(batString.decode('utf-8').split(u'set '+var+u'=')[1].split(u'\n')[0])
    
def fixLoop(lstart,lend):# fix (from soneek's tempoWrite)
    sampleAdd = (lstart % 14336 > 0) * 14336 - lstart % 14336
    return (lstart + sampleAdd, lend + sampleAdd)
    
def editor(hasLoop):# for now it will be only that, will get improved over time hopefully (need for a proper pythonic class + good gui)
    if hasLoop:
        return not tkMessageBox.askyesno(appName,u'A loop was detected, would you want to disable it?')
    else:
        return tkMessageBox.askyesno(appName,u'No loop was detected, would you like your audio sound to loop from the beginning to the end?')

def convert2idsp(replacementSound):
    # making sure there is no remaining tmp files
    for e in known_ext:
        file = os.path.join(folderName,u'tmp'+e)
        if os.path.isfile(file):
            os.remove(file)
            
    ext = getExtension(replacementSound)
    
    is_vgm = ext in known_ext
    if not is_vgm:
        if not ext in known_stand:
            is_vgm = tkMessageBox.askyesno(appName,u'Unknown extension '+ext+u'\nDo you wish to consider it as an audio file from video games? Otherwise it will attempt to convert your file to WAV before any proceeding.')
    
    if is_vgm:
        copyfile(replacementSound,os.path.join(folderName,u'tmp'+ext)) # copy to ensure supported filename
        print (replacementSound + u' copied to local file tmp' + ext)
    # convert to wav
    else:
        cmd = ffmpeg + u' -i "' + replacementSound + u'" "' + os.path.join(folderName,u'tmp.wav') + u'"'
        if subprocess.call(xis.encode(cmd)):
            tkMessageBox.showerror(appName,u'Conversion from MP3 to WAV failed with ' + replacementSound + u'\nThe following command failed:\n' + cmd)
            return
        print (replacementSound + u' converted to local tmp.wav')
        ext = u'.wav'
        
    # getting metadata
    cmd_output=u''
    cmd=vgmstream + u' -b -l1 -d0 -f0 -o "' + os.path.join(folderName,u'tmp.bak.wav') + u'" "' + os.path.join(folderName,u'tmp'+ext) + u'"'
    try:
        cmd_output = subprocess.check_output(xis.encode(cmd))
    except subprocess.CalledProcessError:
        tkMessageBox.showerror(appName,u'Couldn\'t get metadata for ' + replacementSound + u'\nThe following command failed:\n' + cmd)
        return
    chan   = getBatSetVal(cmd_output,u'chan')
    rate     = getBatSetVal(cmd_output,u'rate')
    tsamp = getBatSetVal(cmd_output,u'tsamp')
    lstart = 0
    lend  = tsamp-1
    hasLoop= bool(getBatSetVal(cmd_output,u'loop'))
    if hasLoop:
        lstart = getBatSetVal(cmd_output,u'lstart')
        lend  = getBatSetVal(cmd_output,u'lend')
    # if rate > 44100:
        # cmd = ffmpeg+' -i "'+os.path.join(folderName,'tmp.bak.wav')+'" -r:a 44100 "'+os.path.join(folderName,'tmp44100.wav')+'"'
        # if subprocess.call(cmd):
            # tkMessageBox.showinfo(appName,'Conversion to 44100Hz wav failed, some features might now work properly')
        # else:
            # copyfile(os.path.join(folderName,'tmp44100.wav'),os.path.join(folderName,'tmp.wav'))
            # os.remove(os.path.join(folderName,'tmp44100.wav'))
            # ext = '.wav'
            # tsamp = tsamp*44100/rate
            # lstart   = lstart  *44100/rate
            # lend    = lend    *44100/rate
            # rate = 44100
    lstart,lend=fixLoop(lstart,lend)
    
    # maybe do stuff, like adjust vars, add loop, etc. here
    hasLoop= editor(hasLoop)
    
    # making dsp files
    wdrevBuild = u''
    for c in range(chan):
        cmd1 = vgmstream + u' -l1 -d1 -f0 -1 ' + six.text_type(c) + u' -o "' + os.path.join(folderName,u'tmp.' + six.text_type(c) + u'.wav') + u'" "' + os.path.join(folderName,u'tmp'+ext) + u'"'
        cmd2 = dspadpcm + u' -e "' + os.path.join(folderName,u'tmp.' + six.text_type(c) + u'.wav') + u'" "' + os.path.join(folderName,u'tmp.' + six.text_type(c) + u'.dsp') + u'"'
        if hasLoop:
            cmd2 += u' -l' + six.text_type(lstart) + u'-' + six.text_type(lend)
        wdrevBuild += u' "' + os.path.join(folderName,u'tmp.' + six.text_type(c) + u'.dsp') + u'"'
        print (cmd1)
        if subprocess.call(xis.encode(cmd1)):
            tkMessageBox.showerror(appName,u'Conversion script to IDSP failed with ' + replacementSound + u'\nThe following command failed:\n' + cmd1)
            return
        print (cmd2)
        if subprocess.call(xis.encode(cmd2)):
            tkMessageBox.showerror(appName,u'Conversion script to IDSP failed with ' + replacementSound + u'\nThe following command failed:\n' + cmd2)
            return
    # making idsp
    idsp = os.path.join(folderName,u'new.idsp')
    if os.path.isfile(idsp):
        os.remove(idsp)
    cmd = revb + u' --build-idsp "' + idsp + u'"' + wdrevBuild
    print (cmd)
    if subprocess.call(xis.encode(cmd)):
        if os.path.isfile(idsp):
            tkMessageBox.showwarning(appName,u'Conversion of ' + replacementSound + u' to IDSP ended with an error but an IDSP was created, thus this file (which may be invalid) will be used.\nThe following command failed:\n' + cmd)
        else:
            tkMessageBox.showerror(appName,u'Conversion script to IDSP failed with ' + replacementSound + u'\nThe following command failed:\n' + cmd)
            return
    
    # removing tmp files
    os.remove(os.path.join(folderName,u'tmp.bak.wav'))
    os.remove(os.path.join(folderName,u'tmp'+ext))
    for c in range(chan):
        tmptxt_basename = u'tmp.' + six.text_type(c) + u'.txt'
        tmptxt = tmptxt_basename
        if not os.path.isfile(tmptxt): # location of this file is weird, doesn't seem to work the same for everyone
            tmptxt = os.path.join(n3beDir,tmptxt_basename)
        if not os.path.isfile(tmptxt):
            tmptxt = os.path.join(os.path.join(n3beDir,u'exeLib'),tmptxt_basename)
        os.remove(tmptxt)
        os.remove(os.path.join(folderName,u'tmp.' + six.text_type(c) + u'.wav'))
        os.remove(os.path.join(folderName,u'tmp.' + six.text_type(c) + u'.dsp'))
    
    print (u'\nIDSP: '+idsp)
    if not os.path.isfile(idsp):
        tkMessageBox.showerror(appName,u'File ' + replacementSound + u' could not be converted to IDSP, no replacement done')
        return
    return idsp

def replace(l):
    global change
    if not l.curselection():
        # tkMessageBox.showwarning(appName, 'No IDSP selected!')
        print (u"Selection empty: nothing to replace")
        return
    #asking for replacement file
    replacementSound = xis.decode(askopenfilename(filetypes=[(u'Standard media files',tuple(known_stand)),(u'VGM files',tuple(known_vgm)),(u'All files',u'.*')]))
                                                                        # tuple() for atrocious python 2 support (no need to be atrocious for python 3)
    if not os.path.isfile(replacementSound):
        return
    idsp = convert2idsp(replacementSound)
    if not idsp:
        print (u'Replace: cancelled')
        return
    print (u'Proceeding to replace')
    
    #replace all selected entries with replacement idsp
    songReplacedNumber = 0
    songReplacedName = u""
    songNotReplacedNumber = 0
    songNotReplacedName = u""
    for i in range(len(l.curselection())):
        currentSong = songs[int(l.curselection()[int(i)])]
        
        if not tkMessageBox.askyesno(appName,u"Are you sure you want to replace " + os.path.basename(currentSong) + u" with "+os.path.basename(replacementSound) + u"?"):
            songNotReplacedNumber += 1
            songNotReplacedName   += u'\n'+os.path.basename(currentSong)
            continue
        
        #replacement for idsp in playlist (better previewing) + backup
        backupSong = currentSong[:-5] + u".bak.idsp"
        backupId = 0
        while os.path.isfile(backupSong):
            backupSong = currentSong[:-5] + u".bak" + six.text_type(backupId) + u".idsp"
            backupId += 1
        copyfile(currentSong,backupSong)
        print (u"IDSP backup saved to: " + backupSong)
        try:
            copyfile(idsp,currentSong)
        except IOError:
            songNotReplacedNumber+=1
            songNotReplacedName+=u'\n'+os.path.basename(currentSong)
            continue
        print (u"IDSP replaced in playlist")
        
        songReplacedName   += u"\n" + os.path.basename(currentSong)
        songReplacedNumber += 1
        l.itemconfig(int(l.curselection()[int(i)]),foreground=color_l_change)
    info = u""
    if songReplacedNumber > 0:
        info += u'Successfully replaced with ' + os.path.basename(replacementSound) + u':' + songReplacedName
        pathLabel.config(bg=color_b_change,fg=color_f_change)
        change = True
    if songReplacedNumber*songNotReplacedNumber > 0:
        info += u'\n\n'
    if songNotReplacedNumber > 0:
        info += u'Not replaced with ' + os.path.basename(replacementSound) + u':' + songNotReplacedName
    tkMessageBox.showinfo(appName,info)
    os.remove(idsp)

def revert(l):
    global change
    if not l.curselection():
        # tkMessageBox.showwarning(appName, 'No IDSP selected!')
        print (u"Selection empty: nothing to revert")
        return
    revertedN       = 0
    revertedNotN    = 0
    revertedName    = u''
    revertedNotName = u''
    for i in range(len(l.curselection())):
        song = songs[int(l.curselection()[int(i)])]
        if not tkMessageBox.askyesno(appName,u"Are you sure you want to revert last replacement for " + os.path.basename(song) + u"?"):
            revertedNotN    += 1
            revertedNotName += u'\n' + os.path.basename(song)
            continue
        #find last backup
        backup0    = song[:-5] + u'.bak.idsp'
        backupTest = backup0
        backupL    = ''
        backupId   = 0
        while os.path.isfile(backupTest):
            backupL    = backupTest
            backupTest = song[:-5] + u'.bak' + six.text_type(backupId) + u'.idsp'
            backupId   += 1
        if backupL == u'':
            revertedNotN    += 1
            revertedNotName += u'\n' + os.path.basename(song)
        else:
            try:
                copyfile(backupL,song)
            except IOError:
                revertedNotN    += 1
                revertedNotName += u'\n' + os.path.basename(song)
                continue
            revertedN    += 1
            revertedName += u'\n'+os.path.basename(song)
            os.remove(backupL)
            if backupL == backup0:
                l.itemconfig(int(l.curselection()[int(i)]),foreground=color_l_default)
    info = u''
    if revertedN > 0:
        info += u'Successfully reverted:' + revertedName
        pathLabel.config(bg=color_b_change,fg=color_f_change)
        change = True
    if revertedN*revertedNotN > 0:
        info += u'\n\n'
    if revertedNotN > 0:
        info += u'Not reverted:'+revertedNotName
    tkMessageBox.showinfo(appName,info)

def adaptLength(fullPath,width):
    shortPath=fullPath
    # if getExtension(fullPath) == ext:
        # shortPath = fullPath[:-len(ext)]
    # 278 (232) => 47
    # 23 pixels marging (both sides)
    # 516 (470) => 90
    # (90-47)/(470-232)
    # W'*43/238+b=L
    # b=90-470*43/238
    #b=+5
    
    # maxL = max(47,(width-46) * 43/238+5)
    # midL = (maxL-5)/2
    # if len(shortPath)>maxL:
        # shortPath = shortPath[:midL]+' ... '+shortPath[-midL:]
    
    maxPathWidth = width-10
    minPathWidth = 230
    if tkFont.Font().measure(shortPath) < maxPathWidth:
        return shortPath
    pathLen     = len(shortPath)
    minChars    = min(45,pathLen)
    leftPath    = u''
    rightPath   = u''
    mid         = u'…'
    i = 0
    # while i < pathLen/2 and (2*i+1 < minChars or tkinter.font.Font().measure(leftPath+shortPath[i]+mid+shortPath[pathLen-1-i]+rightPath) < maxPathWidth):
    while i < pathLen/2 and (tkFont.Font().measure(leftPath+mid+rightPath) < minPathWidth or tkFont.Font().measure(leftPath+shortPath[i]+mid+shortPath[pathLen-1-i]+rightPath) < maxPathWidth):
        leftPath += shortPath[i]
        rightPath = shortPath[pathLen-1-i] + rightPath
        i+=1
    shortPath = leftPath + mid + rightPath
    return shortPath

def saveNus(newfile):
    global change
    global nusPath
    try:
        nusPath
    except NameError:
        print (u'No N3B opened')
        return
    if newfile:
        newNusPath = asksaveasfilename(defaultextension=u'.nus3bank',initialfile=os.path.basename(nusPath),filetypes=[(u'NUS3BANK', u'.nus3bank')])#
        if newNusPath == u'':
            return
        if os.path.realpath(nusPath) != os.path.realpath(newNusPath):
            copyfile(nusPath,newNusPath)
            nusPath=newNusPath
    for song in songs:
        if not os.path.isfile(song[:-5] + u'.bak.idsp'):# check if song has been replaced in the current session
            continue
        songID = os.path.basename(song)[:os.path.basename(song).find(u'-')]
        try:
            pyLib.nus3inject.inject(nusPath,song,songID)
        except AssertionError:
            tkMessageBox.showerror(appName, u'An error has occured, ' + os.path.basename(nusPath) + u' couldn\'t get saved with changes.')
            return
    pathLabel.config(text=adaptLength(nusPath,top.winfo_width()),bg=color_b_default,fg=color_f_default)
    tkMessageBox.showinfo(appName,u'Save to ' + os.path.basename(nusPath) + u' successful')
    change = False
    
def openNus(newNusPath = u''):
    global songs
    global playlistPath
    global nusPath
    global listbox
    if newNusPath == u'':
        newNusPath = xis.decode(askopenfilename(filetypes=[(u'NUS3BANK', u'.nus3bank')]))#
    if not os.path.isfile(newNusPath):
        return
    if not clearWorkspace(False):
        return
    nusPath=newNusPath
    try:
        songs = pyLib.nus3bank.extract(nusPath,folderName)
    except AssertionError:
        tkMessageBox.showerror(appName,u'An error has occured, ' + os.path.basename(nusPath) + u' couldn\'t get extracted.')
        clearWorkspace(True)
        return
    except:
        sysexcinfo = ''
        for e in sys.exc_info():
            sysexcinfo += u'\n' + six.text_type(e)
        tkMessageBox.showerror(appName,u'An error has occured, ' + os.path.basename(nusPath) + u' couldn\'t get extracted.\nUnexpected error:' + sysexcinfo + u'\n\n' + xis.decode(traceback.format_exc()))
        clearWorkspace(True)
        return
    print (u"nus3bank extraction: success")
    if not os.path.isdir(folderName):
        tkMessageBox.showerror(appName,folderName + u' where ' + os.path.basename(nusPath) + u' was extracted can\'t be found.')
        clearWorkspace()
        return
    # playlistPath = os.path.join(folderName,'playlist.m3u')
    # if not os.path.isfile(playlistPath):
        # tkMessageBox.showerror(appName,'Playlist storing IDSP files extracted from '+os.path.basename(nusPath)+' can\'t be found.')
        # clearWorkspace()
        # return
    # playlist=open(playlistPath,"r")
    # for line in playlist.readlines():
    i = 0
    for song in songs:
        # song=os.path.join(folderName,line[:-1])
        # songs.append(song)
        listbox.insert(END,os.path.basename(song))
        listbox.itemconfig(i,background=color_l_bg[i%2])
        i+=1
    # playlist.close()
    listbox.focus_set()
    pathLabel.config(text=adaptLength(nusPath,top.winfo_width()),bg=color_b_default,fg=color_f_default)

def clearWorkspace(silent=True):
    global listbox
    global nusPath
    global songs
    global folderName
    global change
    fileopened = True
    try:
        fileopened = bool(nusPath)
    except NameError:
        fileopened = False
    if not silent and fileopened and change and not tkMessageBox.askyesno(appName,u'Are you sure you want to close ' + os.path.basename(nusPath) + u' without saving?'):
        return False
    nusPath=''
    songs=[]
    listbox.delete(0,END)
    folderName = os.path.join(n3beDir,u'tmpspace')
    if os.path.exists(folderName):
        if not os.path.isdir(folderName):
            os.remove(folderName)
            os.mkdir(folderName)
        else:
            for file in os.listdir(folderName):
                filePath = os.path.join(folderName,file)
                if os.path.isfile(filePath) and getExtension(file) in known_work_ext:
                    os.remove(filePath)
    else:
        os.mkdir(folderName)
    print (u'Workspace: '+folderName)
        
    #real foldername, specific to this specific python process
    folderName = os.path.join(folderName,six.text_type(os.getpid()))
    print (u'Workspace: '+folderName)
    
    if os.path.exists(folderName):
        if not os.path.isdir(folderName):
            os.remove(folderName)
        else:
            for file in os.listdir(folderName):
                filePath = os.path.join(folderName,file)
                if os.path.isfile(filePath) and getExtension(file) in known_work_ext:
                    os.remove(filePath)
    
    for c in range(4):
        filePath = os.path.join(n3beDir,'tmp.'+six.text_type(c)+'.txt')
        if os.path.isfile(filePath):
            os.remove(filePath)
            print (u'Removed '+filePath)
    
    top.wm_title(appName)
    pathLabel.config(text=u'No file opened',bg=color_b_null,fg=color_f_null)
    change = False
    print (u'Workspace cleared')
    return True
    
def openidsp(l):
    if len(l.curselection()) ==0:
        print (u"Selection empty: nothing to open")
        return
    elif len(l.curselection())>1:
        plPath = os.path.join(folderName,u'tmp.m3u')
        playlist = open(plPath,u'w')
        for i in l.curselection():
            playlist.write(songs[int(i)] + u'\n')
        playlist.close()
        openplaylist(plPath)
    else:
        currentSong = songs[int(l.curselection()[0])]
        if os.path.isfile(currentSong):
            os.startfile(currentSong)
        else:
            tkMessageBox.showerror(appName, u'File ' + currentSong + u' is missing!')

def openall():
    if not songs:
        print (u'Playlist empty')
        return
    plPath = os.path.join(folderName,u'tmp.m3u')
    playlist = open(plPath,u'w')
    for song in songs:
        playlist.write(song + u'\n')
    playlist.close()
    openplaylist(plPath)

def exportidsp(l):
    if len(l.curselection()) == 0:
        print (u'Selection empty: nothing to export')
        return
    for i in l.curselection():
        currentSong = songs[int(i)]
        if os.path.isfile(currentSong):
            output = xis.decode(asksaveasfilename(defaultextension=u'.wav',initialfile=os.path.basename(currentSong)[:-5],filetypes=[(u'Wave Audio File', u'.wav'),(u'IDSP Track', u'.idsp')]))
            if output ==u"":
                print (u"Export canceled")
                return
            print (u"Set output to "+output)
            ext = getExtension(output)
            if ext == u'.wav':
                cmd = (vgmstream + u' "' + currentSong + u'" -o "' + output + u'"')
                if subprocess.call(xis.encode(cmd)):
                    tkMessageBox.showerror(appName,u'Export to WAV failed.\nThe following command failed:\n' + cmd)
                    return
                    # tkMessageBox.showerror(appName,'Unicode error with:\n'+cmd)
            elif ext == '.idsp':
                if os.path.realpath(currentSong) != os.path.realpath(output):
                    try:
                        copyfile(currentSong, output)
                    except IOError:
                        tkMessageBox.showerror(appName,u'Can\'t write to ' + output)
                        return
            else:
                tkMessageBox.showerror(appName, u'Export to ' + ext + u' not supported')
                return
            tkMessageBox.showinfo(appName,u'Export to ' + output + u' done')
        else:
            tkMessageBox.showerror(appName, u'File ' + currentSong + u' is missing!')

def openplaylist(playlist):
    if os.path.isfile(playlist):
        print (u"Playing playlist")
        os.startfile(playlist)
    else:
        # tkMessageBox.showerror(appName, 'File '+playlist+' is missing!')
        # tkMessageBox.showwarning(appName, 'There is no playlist to open!')
        print (u"No playlist")

def invertSelection(l):
    for i in range(l.size()):
        if l.select_includes(i):
            l.select_clear(i)
        else:
            l.select_set(i)

def show_error(self, *args):
    err    = traceback.format_exception(*args);
    errMsg = u""
    for e in err:
       errMsg += xis.decode(e)
    tkMessageBox.showerror(appName,errMsg)
    
def about():
    aboutText =    u'A GUI that injects many things into nus3bank files'
    aboutText += u'\n'
    aboutText += u'\nStarted with love by jam1garner'
    aboutText += u'\nContinued with passion by BlueDan'
    aboutText += u'\n'
    aboutText += u'\nCredits go to :'
    aboutText += u'\n- Soneek who made tools essential for this'
    aboutText += u'\n- everyone involved with vgmstream'
    aboutText += u'\n- everyone involved with ffmpeg'
    aboutText += u'\n- everyone who tested this tool and gave feedback!'
    tkMessageBox.showinfo(u'About '+appName,aboutText)
    

def on_exit():
    if not clearWorkspace(False):
        return
    if os.path.isdir(folderName):
        os.rmdir(folderName)
    try:
        os.rmdir(os.path.dirname(folderName))
    except OSError:
        pass
    exit()

    
timeRefPathLabel = time.clock()
def reactOnResize(event):
    global timeRefPathLabel
    try:
        nusPath
    except NameError:
        return
    if not os.path.isfile(nusPath):
        return
    if time.clock()-timeRefPathLabel<0.1:
        return
    timeRefPathLabel = time.clock()
    pathLabel.config(text=adaptLength(nusPath,event.width))

# global songs
# global folderName
# playlistPath=''
Tk.report_callback_exception = show_error
songs = []
folderName = u""
top = Tk()
menubar = Menu(top)
top.minsize(300,265)

frame = Frame(top, bd = 0)
yscrollbar = Scrollbar(frame, orient=VERTICAL)
xscrollbar = Scrollbar(frame, orient=HORIZONTAL)
listbox = Listbox(frame,width=46,bd=0,yscrollcommand=yscrollbar.set,xscrollcommand=xscrollbar.set,selectmode=EXTENDED)
yscrollbar.config(command=listbox.yview)
yscrollbar.pack(side=RIGHT, fill=Y)
xscrollbar.config(command=listbox.xview)
xscrollbar.pack(side=BOTTOM, fill=X)
listbox.pack(fill=BOTH, padx = 10, expand=1)
frame.pack(fill=BOTH,expand=1)

# menu entries
filemenu = Menu(menubar,tearoff=0)
filemenu.add_command(label       = u"Open NUS3BANK",
                     command     = openNus,
                     accelerator = u"Ctrl+O")
filemenu.add_command(label       = u'Close',
                     command     = lambda: clearWorkspace(False),
                     accelerator = u"Ctrl+W")
filemenu.add_command(label       = u'Save',
                     command     = lambda: saveNus(False),
                     accelerator = u"Ctrl+S")
filemenu.add_command(label       = u'Save as…',
                     command     = lambda: saveNus(True),
                     accelerator = u"Ctrl+Shift+S")
filemenu.add_separator()
filemenu.add_command(label       = u'Preview selection',
                     command     = lambda: openidsp(listbox),
                     accelerator = u'Ctrl+P')
filemenu.add_command(label       = u'Preview full playlist',
                     command     = openall,
                     accelerator = u'Ctrl+Shift+P')
filemenu.add_separator()
filemenu.add_command(label       = u'Export to…',
                     command     = lambda: exportidsp(listbox),
                     accelerator = u'Ctrl+E')
filemenu.add_separator()
filemenu.add_command(label       = u"Exit",
                     command     = on_exit,
                     accelerator = u"Ctrl+Q")
editmenu = Menu(menubar,tearoff=0)
editmenu.add_command(label       = u'Select all',
                     command     = lambda: listbox.select_set(0,END),
                     accelerator = u'Ctrl+A')
editmenu.add_command(label       = u'Invert selection',
                     command     = lambda: invertSelection(listbox),
                     accelerator = u'Ctrl+I')
editmenu.add_separator()
editmenu.add_command(label       = u'Replace',
                     command     = lambda: replace(listbox),
                     accelerator = u'Ctrl+R')
editmenu.add_command(label       = u'Revert',
                     command     = lambda: revert(listbox),
                     accelerator = u'Ctrl+Shift+R')
qm_menu = Menu(menubar,tearoff=0)
qm_menu.add_command(label   = u'About',
                    command = about)
menubar.add_cascade(label=u"File", menu = filemenu)
menubar.add_cascade(label=u"Edit", menu = editmenu)
menubar.add_cascade(label=u"?"   , menu = qm_menu)
top.wm_title(appName)
top.config(menu=menubar)

# keyboard shortcuts
top.bind_all(u"<Control-o>", lambda e: openNus())
top.bind_all(u"<Control-w>", lambda e: clearWorkspace(False))
top.bind_all(u'<Control-s>', lambda e: saveNus(False))
top.bind_all(u'<Control-S>', lambda e: saveNus(True))
top.bind_all(u'<Control-q>', lambda e: on_exit())
top.bind_all(u'<Control-a>', lambda e: listbox.select_set(0,END))
top.bind_all(u'<Control-i>', lambda e: invertSelection(listbox))
top.bind_all(u'<Control-r>', lambda e: replace(listbox))
top.bind_all(u'<Control-R>', lambda e: revert(listbox))
top.bind_all(u'<Control-p>', lambda e: openidsp(listbox))
listbox.bind(u'<Double-1>',  lambda e: openidsp(listbox))
listbox.bind(u'<Return>',    lambda e: openidsp(listbox))
top.bind_all(u'<Control-P>', lambda e: openall())
top.bind_all(u'<Control-e>', lambda e: exportidsp(listbox))

# buttons
frameB = Frame(top,bd=0)

replaceButton = Button(frameB,text=u"Replace",width=19,command=lambda l=listbox: replace(l))
replaceButton.grid(row=0,column=0,padx=2,pady=2)

revertButton = Button(frameB,text=u"Revert",width=19,command=lambda l=listbox: revert(l))
revertButton.grid(row=0,column=1,padx=2,pady=2)

openButton = Button(frameB,text=u"Preview selection",width=19,command=lambda l=listbox: openidsp(l))
openButton.grid(row=1,column=0,padx=2,pady=2)

playlistButton = Button(frameB, text=u"Preview full playlist",width=19,command= openall)
playlistButton.grid(row=1,column=1,padx=2,pady=2)

frameB.pack(padx=5,pady=5)

# bottom with file path
pathLabel = Label(top,text=u'No file opened',bg=u'black',fg=u'white')
pathLabel.pack(fill=X)

top.bind_all(u'<Configure>',reactOnResize)

# context menu
idspMenu = Menu(top, tearoff=0)
idspMenu.add_command(label=u'Replace',command=lambda: replace(listbox))
idspMenu.add_command(label=u'Revert' ,command=lambda: revert(listbox))
idspMenu.add_command(label=u'Preview',command=lambda: openidsp(listbox))
idspMenu.add_command(label=u'Export' ,command=lambda: exportidsp(listbox))

def popup(event):
    i = listbox.nearest(event.y)
    if not listbox.select_includes(i):
        listbox.select_clear(0,END)
        listbox.select_set(listbox.nearest(event.y))
    if len(listbox.curselection())>0:
        idspMenu.post(event.x_root,event.y_root)
listbox.bind(u'<Button-3>',popup)

# opening file submitted on argument
if len(sys.argv)>1:
    openNus(xis.decode(sys.argv[1]))
    
top.protocol(u"WM_DELETE_WINDOW",on_exit)

top.mainloop()
