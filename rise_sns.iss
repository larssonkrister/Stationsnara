; -- Components.iss --
; Demonstrates a components-based installation.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=Stationsn�ra Demo
OutputBaseFilename=Stationsnara Demo
SetupIconFile=snsd.ico
AppVersion=1.0
AppPublisher=Research Institutes of Sweden (RI.SE)
AppPublisherURL=http://www.ri.se/
DefaultDirName={pf}\Stationsn�ra
DefaultGroupName=Stationsn�ra
UninstallDisplayIcon={app}\main\main.exe
UninstallIconFile=snsd.ico
VersionInfoVersion=1.0.0


[Files]
Source: "snsd.ico"; DestDir: "{app}";
Source: "config.json"; DestDir: "{app}";
Source: "start.bat"; DestDir: "{app}";
Source: "dist\main\*"; DestDir: "{app}\main";
Source: "dist\main\cryptography\hazmat\bindings\*"; DestDir: "{app}\main\cryptography\hazmat\bindings";
Source: "dist\main\cryptography-2.6.1-py3.7.egg-info\*"; DestDir: "{app}\main\cryptography-2.6.1-py3.7.egg-info";
Source: "dist\main\Include\*"; DestDir: "{app}\main\Include";
Source: "dist\main\lib2to3\*"; DestDir: "{app}\main\lib2to3";
Source: "dist\main\markupsafe\*"; DestDir: "{app}\main\markupsafe";
Source: "dist\main\win32com\shell\*"; DestDir: "{app}\main\win32com\shell";

Source: "static\*"; DestDir: "{app}\static";
Source: "static\media\audio\*"; DestDir: "{app}\static\media\audio";
Source: "static\media\video\*"; DestDir: "{app}\static\media\video";
Source: "static\media\img\*"; DestDir: "{app}\static\media\img";
Source: "templates\*"; DestDir: "{app}\templates";


[Icons]
Name: "{userprograms}\Stationsn�ra Demo"; Filename: "{app}\start.bat"; IconFilename: "{app}\snsd.ico";
Name: "{userdesktop}\Stationsn�ra Demo"; Filename: "{app}\start.bat"; IconFilename: "{app}\snsd.ico";
