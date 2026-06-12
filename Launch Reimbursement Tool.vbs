' ============================================================
' Reimbursement Report Sender — Launcher
' Double-click to open as desktop app (powered by Electron)
' Close the app window to shut everything down
' ============================================================

Dim oShell, oFSO, sRoot, sFrontend

Set oShell = CreateObject("WScript.Shell")
Set oFSO   = CreateObject("Scripting.FileSystemObject")

sRoot     = oFSO.GetParentFolderName(WScript.ScriptFullName)
sFrontend = sRoot & "\apps\reimbursement-tool\frontend"

If Not oFSO.FolderExists(sFrontend) Then
    MsgBox "Frontend folder not found:" & vbCrLf & sFrontend, 16, "Launch Error"
    WScript.Quit 1
End If

' Kill any leftover processes on ports 3000 / 3001
oShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -aon ^| findstr :3001') do taskkill /F /PID %a", 0, True
oShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -aon ^| findstr :3000') do taskkill /F /PID %a", 0, True

' Launch Electron app (starts backend + frontend servers internally, opens app window)
oShell.Run "cmd /k ""title Reimbursement Tool && cd /d """ & sFrontend & """ && npm run electron-app""", 1, False

Set oShell = Nothing
Set oFSO   = Nothing
