' LDM_launcher.vbs — lanza el .bat oculto y crea acceso directo al propio .vbs
Option Explicit

Dim fso, shell, scriptPath, scriptDir, desktop, lnkPath, batPath, icoPath
Dim pyExe
Set fso   = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptPath = WScript.ScriptFullName
scriptDir  = fso.GetParentFolderName(scriptPath)
desktop    = shell.SpecialFolders("Desktop")
lnkPath    = desktop & "\Lo de Manoli.lnk"
batPath    = scriptDir & "\Gestion de Stock Lo de Manoli.bat"
icoPath    = scriptDir & "\ldm.ico"
pyExe      = scriptDir & "\..\venv\Scripts\python.exe"  ' venv en manoli\venv

' 1) Acceso directo al MISMO .vbs (sin consola)
If Not fso.FileExists(lnkPath) Then
  Dim lnk: Set lnk = shell.CreateShortcut(lnkPath)
  lnk.TargetPath = scriptPath
  lnk.WorkingDirectory = scriptDir
  If fso.FileExists(icoPath) Then lnk.IconLocation = icoPath
  lnk.Save
End If

' 2) Checks visibles
If Not fso.FileExists(pyExe) Then
  MsgBox "No se encontró el entorno virtual (venv):" & vbCrLf & pyExe & vbCrLf & vbCrLf & _
         "Crealo con:" & vbCrLf & _
         "  py -3.13 -m venv ..\venv --copies" & vbCrLf & _
         "  ..\venv\Scripts\python -m pip install --upgrade pip wheel setuptools" & vbCrLf & _
         "  ..\venv\Scripts\pip install -r .\requirements.txt", _
         vbCritical + vbOKOnly, "Lo de Manoli"
  WScript.Quit 1
End If

If Not fso.FileExists(batPath) Then
  MsgBox "No se encontró el lanzador:" & vbCrLf & batPath, vbCritical + vbOKOnly, "Lo de Manoli"
  WScript.Quit 1
End If

' 3) Ejecutar el .bat totalmente oculto
shell.Run """" & batPath & """", 0, False
