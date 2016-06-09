# NUS3BANK Editor
_by jam1garner (1.0-1.7 then support) and BlueDan aka BDS aka DanSyor (1.7-now)_

This is a GUI for Windows users to convert and import audio tracks into nus3bank files. Nus3bank files are basically a set of idsp audio tracks (for bgm, they most likely have only one track) that can feature a loop or not.

You need Python 2.7 installed to run it. Or since 2.20, Python 3.5!

Run `NUS3BANK Editor.pyw` either on your file explorer or on console.
Or since 2.10 you can use `NUS3BANK_Editor.bat`, that you can bind to be the default program to open files with nus3bank extension.


### Credits:
- Soneek who made tools essential for this
- everyone involved with vgmstream
- everyone involved with ffmpeg
- everyone who tested this tool and gave feedback

### Known issues:
* Crack noise at the end of loops
* You might have encoding problems (some error window popping up yelling at you something about UnicodeEncodeError) related to characters within the paths of files you're using. I try my best for you to avoid those but unfortunately the behaviour doesn't seem consistent from one computer to another, making it hard for me to clearly identify what goes wrong. If you're using Python 2.7 and encounter these issues, either be careful about any potentially exotic character in the paths of your files, or consider switching to Python 3.5.
    
### Troubleshooting
Be sure to grab the latest version, for now download links are posted on the [GBATemp Thread](http://gbatemp.net/threads/easy-nus3bank-editor-with-gui.426370/) by BlueDan as BDS.

You may want to check the latest pages in case any specific hotfix was posted.

If you encounter any error, please provide (on the above thread or PM BlueDan on Discord) a clear and detailed explanation of what you're attempting to achive and how you do so. A screenshot of the error is highly appreciated.

You may want to use NUS3BANK_Editor_troubleshooting.bat to have a better chance to screenshot any error.
 * "When trying to use NUS3BANK_Editor.bat, an error pops up: ``Windows cannot find 'pythonw'. Make sure you typed the name correctly, and then try again.``
  * Looks like Python is not in your environment variable PATH. Follow the following instructions (these are for Python 2.7):
        - Right click on the windows logo (or hit windows + pause and go to step 3)
        - Select system
        - Select advanced settings
        - Environment variables
        - Find path, click edit
        - Select new and enter C:\Python27\
        - Select new (again) and enter C:\Python27\Scripts
        - If you have any cmd opened, you should close them before checking your %path% again
        - Try first with system variables then user variables
 * "I'd like to run the Python 3.5 version, how do I do that?"
  * 

[Version history](HISTORY.md)