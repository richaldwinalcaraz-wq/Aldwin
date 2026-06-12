' LeadForge AI Scraper Launcher
' Starts Node server silently + opens Edge in app mode (no browser chrome)

Dim WshShell, fso
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

Dim appDir : appDir = "C:\Users\user\OneDrive\Documents\DashBoard Project\apps\leadforge"
Dim port   : port   = "3000"
Dim url    : url    = "http://localhost:" & port

' Start Node server hidden (window style 0 = hidden)
WshShell.CurrentDirectory = appDir
WshShell.Run "node src\server.js", 0, False

' Wait for server to boot
WScript.Sleep 2800

' Try Microsoft Edge in app mode (no URL bar, no tabs — looks native)
Dim edgePath, chromePath
edgePath   = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"

Dim appArgs : appArgs = " --app=" & url & " --window-size=1280,820"

If fso.FileExists(edgePath) Then
    WshShell.Run """" & edgePath & """" & appArgs, 1, False
ElseIf fso.FileExists(chromePath) Then
    WshShell.Run """" & chromePath & """" & appArgs, 1, False
Else
    WshShell.Run "explorer " & url, 1, False
End If
