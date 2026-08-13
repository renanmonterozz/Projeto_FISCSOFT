
; NSIS script to create an installer for the dist\FISCSOFT folder
; Requires makensis in PATH

!define APPNAME "FISCSOFT"
!define APPDIR "FISCSOFT"
!define OUTFILE "FISCSOFT_Installer.exe"

!include "MUI2.nsh"

SetCompressor /SOLID lzma
OutFile "${OUTFILE}"
InstallDir "$PROGRAMFILES64\\${APPDIR}"
ShowInstDetails show

; If icon exists in dist, use it for installer and shortcuts
!define ICONPATH "dist\\FISCSOFT\\logo_fiscsoft.ico"
; set installer icon if available
IfFileExists "${ICONPATH}" +2
  Icon "${ICONPATH}"

Section "Install"
  SetOutPath "$INSTDIR"
  ; Recursively copy files from dist\FISCSOFT
  File /r "dist\\FISCSOFT\\*"

  ; Create Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\FISCSOFT.exe" "" "$INSTDIR\\logo_fiscsoft.ico"

  ; Desktop shortcut
  CreateShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\FISCSOFT.exe" "" "$INSTDIR\\logo_fiscsoft.ico"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\\FISCSOFT.exe"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
  RMDir "$SMPROGRAMS\\${APPNAME}"
  Delete "$DESKTOP\\${APPNAME}.lnk"
SectionEnd
