# RAPPS DATABASE 
For more information about RAPPS, please take a look at the [wiki](https://reactos.org/wiki/RAPPS) 

## ADDING PROGRAMS TO THE RAPPS DATABASE

Each program entry consists of a text file formatted with an INI-like syntax.

They must be:
Encoded in `UTF-16 LE (Little Endian)` or characters out of the ANSI range will display broken. 
**Note:** some editors like Notepad++ call this format `UCS-2 Little Endian.`

### Sections

Each `[Section]` is language-independent and individual, you can override the URL to a source program or any other field by adding a language-specific `[Section.]`, followed by the language code.

**Note:** You can find a complete listing of LCIDs and language names on [MSDN](https://msdn.microsoft.com/en-us/library/windows/desktop/dd318693%28v=vs.85%29.aspx), includes neutral codes:

**__Link is "broken", it works but redirects [here](https://docs.microsoft.com/en-us/windows/win32/intl/language-identifier-constants-and-strings), that does not show the codes anymore, as it has been deprecated as system, this information is now [here at page 31 and next](https://winprotocoldoc.blob.core.windows.net/productionwindowsarchives/MS-LCID/%5bMS-LCID%5d.pdf)__**
     
RAPPS also accepts neutral language codes, meaning that you can do things like this:
 
     ; Default English fallback, used if everything else fails.
      [Section]
      Name = Name in English
    
      ; Neutral Spanish, used if the specific variant of Spanish does not match.
      [Section.0a]
      Name = Name in Generic Spanish
    
      ; Spanish from Spain, used if the system is configured for it.
      [Section.0c0a]
      Name = Name in Castilian Spanish

You can also define an entry without English fallback to make it visible to certain users only.
For instance; software from 1C, which is mostly for Russian speakers and unusable for anyone else.

**__ There are some user that can speak multiple languages, for example an English-native user (with the OS set to English)  could also speak German (and use German-only software, but in case couldn't see it listed). Maybe there could be a way for the user to set which languages he would like to be listes? __**

The official list of downloadable programs is kept on a public ReactOS server and synced every time RAPPS is launched for the first time.

### Minimal example

For a complete file format overview see the [File Schema on the ReactOS wiki](https://reactos.org/wiki/RAPPS#File_Schema)

The mandatory fields are: *Name*, *Category* and *URLDownload*. All other fields are completely optional and can be skipped.

     [Section]
     Name = Example Program
     Category = 1; See below for available categories
     URLDownload = example.com/myfile.exe

## FILE SCHEMA FIELD LIST
* Name (mandatory)
* Version
* License
* Description
* SizeBytes
* Category (mandatory)
* URLSite
* URLDownload (mandatory)
* ScreenshotN
* Icon

### Name
This is the program name that is displayed.

### Version
This is the version of the program.  **__ As it is used to check for updates, which decimal separator it uses? Comma or dot? Does it use the OS language one? Or is it fixed? __**

### License
The license that the program is based on. Typical options are : Trial, Demo, Freeware, Open-Source. Or more specifically, GPL, MIT and so on. **__ What happens if it used together with LicenseInfo? Does it also support links? __**

### Description
The description of the program giving some additional background information about what it does.

### SizeBytes
The actual size of the download in bytes. Used to display size value in the application info as well as while downloading. 

### Category
The category of the program. Category name corresponds to the number. There are 15+1 valid categories for now: 

 1. Audio
 2. Video
 3. Graphics
 4. Games
 5. Internet
 6. Office
 7. Development
 8. Edutainment
 9. Engineering
 10. Finance
 11. Science
 12. Tools
 13. Drivers
 14. Libraries
 15. Themes
 16. Other

### URLSite
Main web site where the program can be found. **__ Is HTTPS mandatory or only advised? If the link is in HTTP, can it try to switch automatically to HTTPS if avaliable? __**

### URLDownload
Direct link to the installer/program. **__ Is HTTPS mandatory or only advised? If the link is in HTTP, can it try to switch automatically to HTTPS if avaliable? __**

### ScreenshotN
Screenshot URL link. (N = 1, 2, 3 ...)

Currently, only first Screenshot is used. Ensure the URL is a direct link to the image, not a page containing the image (e.g. Imgur links). It is also preferred to include the screenshot taken on ReactOS, not on Windows.  **__ Does it still support only one screenshot? Have you thought about creating a repository for screenshots? __**

### Icon
Icon filename in icons folder (with .ico extension) **__ Any specification on size etc? __**

### DEPRECATED
Previously used parameters, now deprecated, should be removed if found in a existing file

* Size

### EXPERIMENTAL

* Languages
* LicenseInfo

### Languages
This field is used to inform the user whether the app is available in their language.

You should place all the language codes app supports separated by | there. 
Example
     Languages=0C09|0813|0422
**__ How are these code formatted? Are the same used in Sections? __**     

### LicenseInfo
This is a field in the DB which, when present, changes the way License field in the info is shown.

Application license types correspond to a number:

    1 - "Open Source"
    2 - "Freeware"
    3 - "Demo/Trial".
   
**__ How does this change the way the License is shown? __**   
