For more information about RAPPS, please take a look at the [wiki](https://reactos.org/wiki/RAPPS) 

ADDING PROGRAMS TO THE RAPPS DATABASE
--------------------------------------------------

Each program entry consists of a text file formatted with an INI-like syntax.

They must be:
Encoded in `UTF-16 LE (Little Endian)` or characters out of the ANSI range will display broken. 
**Note:** some editors like Notepad++ call this format `UCS-2 Little Endian.`


Each `[Section]` is language-independent and individual, you can override the URL to a source program or any other field by adding a language-specific `[Section.]`, followed by the language code.

**Note:** You can find a complete listing of LCIDs and language names on [MSDN](https://msdn.microsoft.com/en-us/library/windows/desktop/dd318693%28v=vs.85%29.aspx), includes neutral codes:
     
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

File format overview:

      ; This is a INI-style comment, useful for adding additional information.
      ; Lines starting with a ; character are skipped by the parser.
    
      [Section]
      Name = My fun stuff-o-matic
      RegName = Name in Registry
      Version = 1.1.1
      License = GPL
      Description = Shortish description giving some additional background information about what it does.
      Size = 10 MB
      Category = 5
      URLSite = https://example.org/
      URLDownload = https://ftp.example.org/pub/installer.exe
      Screenshot1 = Screenshot URL
      Icon = Icon filename in icons folder (with .ico extension)
      
      [Section.0419] ; 0419 - for Russian language
      Description = Description in Russian language




The mandatory fields are: *Name*, *Category* and *URLDownload*
All other fields are completely optional and can be skipped.

List of valid categories:

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

The official list of downloadable programs is kept on a public ReactOS server
and synced every time RAPPS is launched for the first time.
