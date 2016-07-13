### Changelog:

_2.20_ - 2016/07/?
 * Fixed other encoding problems for input file
 * Fixed encoding problems regarding nus3bank extraction
 * Fully ported to Python 3.5: if you still have encoding problems, consider switching
 * Disabled log file creation and re-enable DOS output when it exists (= launched from python.exe, no pythonw.exe)
 * Doesn't ask anymore for a confirmation to close the file when no change has been done since last save
 * workspace/tmpspace folder now gets deleted when empty

_2.13b_ - 2016/06/04
 * Updated NUS3BANK_Editor.bat so no DOS console pops up
 * Fixed IOError 9 when trying to print to a non-existent DOS console
    
_2.13a_ - 2016/06/04
 * Fixed other encoding issues (paths related)
 * Made traceback visible for errors happening with nus3bank extraction

_2.13_ - 2016/06/03
 * Fixed playlist creation (on previous versions, an m3u could be left opened after nus3bank extraction failed, eventually causing an error when clearing workspace)
 * Changed colors for the path of the file (gray = no changes, no need to save; blue = changes (probably), should save)
 * Better algorithm for partial display of path
 * Alternates background color for tracks for better visibility
 * Various changes in how the app closes files/itself
 * Fixed encoding for errors (…)

_2.12_ - 2016/06/03
 * Hotfix so that it works either like in 2.10 or in 2.11 when deleting these temporary files (previous hotfix broke it for others)

_2.11_ - 2016/06/03
 * Hotfix for an issue when deleting temporary files without being in the main folder

_2.10_ - 2016/06/03
 * Fixed some menu entries with wrong action
 * Fixed default name when exporting
 * Opening a NUS3BANK now sets focus inside the list, so you can scroll directly
 * You can now preview a selection of tracks: either click the button, use the File menu, double click or hit enter/return
 * Right-clicking now allows you to select one track or can be used on a set of tracks already selected and grants the user with a context menu with replace/revert/preview/export options
 * Fixed something I forgot to edit within nus3bank.py and nus3inject.py
 * Better error handling (yes, again!)
 * Added a batch file that can be used to open and edit nus3bank files anywhere you can go with your file explorer (code edited so that everything works fine)
 * Window is now truly resizable
 * Added on-screen indicator of whether or not changes have apparently be applied or not (so that you save) (green = no changes since last save; red = maybe changes from last save)
 * It also gives you the path to the file you're currently editing (the .nus3bank extension is hidden)
 * A major design flow that could prevent two instances to work correctly simultaneously has been fixed
 * Fixed some encoding problems (no more UnicodeEncodingError?)

_2.02_ - 2016/06/01
 * Now supports directly DSP and HSP files (audio replacement)
 * Added the option to consider "unknown" extensions as VGM files (audio replacement)

_2.01_ - 2016/05/31
 * Fixed "Saving as..."
 * Opening nus3bank files and saving should now work for people who had an error trying to

_2.00_ - 2016/05/31
 * Now uses ffmpeg to support a LOT more file types (literally anything ffmpeg can convert to wav, from MP3 to video files)
 * Added an x-axis scrollbar
 * Entries go blue when replaced
 * Error handling enhanced (yes, again!)
 * Grouped some extensions together (like .wav with .ogg and .mp3; .bXstm together) + added wildcard extension for any extra extension that works (video files...) for easier use
 * Added the ability to revert replacements
 * Now uses a set workspace folder instead of a file-dependant folder
 * Saving when the user wants (injections into nus3bank are done only when actually saving instead of whenever replacing an idsp; replacing an idsp only converts the file to idsp and puts it in the preview playlist)
 * Ability to save as another nus3bank file added
 * Fixing playlist path, take 2
 * Reworked conversion to idsp for replacement sounds. Can loop audio on demand.
 * Menu entries with keyboard shortcuts have been added
 * The "Export to WAV" button has been removed and replaced with a menu entry that can also export an idsp with no conversion

_1.96_ - 2016/05/27
 * Now copies replacement audio files to tmp files to ensure filename to be supported

_1.95_ - 2016/05/27
 * Fixed a bug where replacement idsp was not properly located and probably no change happened
 * Added better error handling for the conversion of replacement audio files to IDSP
 * Now makes a backup of the nus3bank file when replacing its idsp's
 * Replacing idsp's in the file also replaces them within the playlist, backups are made for replaced idsp's
 * Fixing playlist path, take 1
 * Fixed a bug that could happen and prevent from opening idsp's or replacing them

_1.9_ - 2016/05/26
 * Fixed opening NUS3BANK files
 * Additional warnings
 * Fixed multiple file replacement
 * Added a confirmation window for file replacement

_1.8_ - 2016/05/25
 * Better error handling

_1.7_ - 2016/05/22
 * Added playlist support (and open in playlist option).
 * Also fixed a bug with certain nus3banks not properly opening.

_1.6_ - 2016/05/21
 * Added an "Export to WAV" option. Just select the IDSPs to export and hit the button and it will export to `/nus3bankeditor/<Name of *.nus3bank>/<name of *.idsp>.wav` this does support doing multiple at once.

_1.5_ - 2016/05/18
 * Added the ability to open idsps from within the tool through the default IDSP opener. To set this up install a something that can listen to idsps (example: foobar2000+vgmstream) and open an idsp in any way, when prompted select open with foobar (or whatever program you want)

_1.3_ - 2016/05/15
 * Added support for BRSTMs, BCSTMs, BFSTMs and OGGs.
 * Added more debugging related features.
 * Fixed bugs nobody cares about.

_1.1_ - 2016/05/14
 * Fixed some issues with renamed nus3bank's not properly opening
 * Added the ability to import idsp's
 * A few smaller bug fixes.

_1.0_ - 2016/05/13
 * Initial release
