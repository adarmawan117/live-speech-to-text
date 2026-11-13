Set WshShell = CreateObject("WScript.Shell")
ScriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
PythonwPath = ScriptDir & "\venv\Scripts\pythonw.exe"
MainPath = ScriptDir & "\main.py"

WshShell.CurrentDirectory = ScriptDir
WshShell.Run Chr(34) & PythonwPath & Chr(34) & " " & Chr(34) & MainPath & Chr(34), 0, False
Set WshShell = Nothing

