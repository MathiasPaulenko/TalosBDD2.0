'=================================================================================================================================
' Name:		talos-pcom.vbs
' Version:	V01R01-2021/02
' Descrip:	Talos Automation Framework - IBM Personal Communications Automation Library
' Author:	Santander Global Tech - Solutions Engineering / Quality Assurance
' Functions:
'---------------------------------------------------------------------------------------------------------------------------------
'  1.talos_pcom_check_param			 2.talos_pcom_exit_error		 3.talos_pcom_exit_ok			 4.talos_pcom_file_exist
'  5.talos_pcom_task_close			 6.talos_pcom_check_range		 7.talos_pcom_get_session		 8.talos_pcom_open
'  9.talos_pcom_close				10.talos_pcom_put				11.talos_pcom_set_cursor		12.talos_pcom_key
' 13.talos_pcom_wait				14.talos_pcom_get				15.talos_pcom_ftp_exec			16.talos_pcom_minimize_all
'=================================================================================================================================


'=======================================================================================================================
' Global vars for IBM Personal Communications
'=======================================================================================================================
Dim autECLConnMgr, autECLSession, autECLOIA, autECLPS

Public Const HOSTSESSION = "A"      ' Host session name
Public Const intHOSTespera = 10     ' Timeout in seconds


'=======================================================================================================================
' Main script execution
'=======================================================================================================================
	Call talos_pcom_check_param()
	WScript.Quit
	

'=======================================================================================================================
' Check for input parameters
'=======================================================================================================================
Function talos_pcom_check_param()
	
	totalParam = WScript.Arguments.Count
	
	If totalParam = 0 then
		Call talos_pcom_exit_error("Missing parameter 1")
	End If
	
	strParam1 = LCase(WScript.Arguments(0))
	
	Select Case (strParam1)
		
		Case "open"
			If totalParam = 1 then
				Call talos_pcom_exit_error("Missing parameter 2: path")
			End If
			strPath = WScript.Arguments(1)
			Call talos_pcom_open(strPath)
			Call talos_pcom_exit_ok(strParam1 & " " & strPath)
		
		Case "close"
			Call talos_pcom_close()
			Call talos_pcom_exit_ok(strParam1)
		
		Case "put"
			If totalParam = 1 then
				Call talos_pcom_exit_error("Missing parameter 2: row number")
			End If
			If totalParam = 2 then
				Call talos_pcom_exit_error("Missing parameter 3: col number")
			End If
			If totalParam = 3 then
				Call talos_pcom_exit_error("Missing parameter 4: value")
			End If
			intRow   = WScript.Arguments(1)
			intCol   = WScript.Arguments(2)
			strValue = WScript.Arguments(3)
			Call talos_pcom_put(intRow, intCol, strValue)
			Call talos_pcom_exit_ok(strParam1 & " " & intRow & " " & intCol & " " & strValue)
			
		Case "key"
			If WScript.Arguments.Count = 1 then
				Call talos_pcom_exit_error("Missing parameter 2: key")
			End If
			strKey = WScript.Arguments(1)
			Call talos_pcom_key(strKey)
			Call talos_pcom_exit_ok(strParam1 & " " & strKey )
		
		Case "wait"
			If totalParam = 1 then
				Call talos_pcom_exit_error("Missing parameter 2: row number")
			End If
			If totalParam = 2 then
				Call talos_pcom_exit_error("Missing parameter 3: col number")
			End If
			If totalParam = 3 then
				Call talos_pcom_exit_error("Missing parameter 4: long number")
			End If
			If totalParam = 4 then
				Call talos_pcom_exit_error("Missing parameter 5: value")
			End If
			intRow   = WScript.Arguments(1)
			intCol   = WScript.Arguments(2)
			intLon   = WScript.Arguments(3)
			strValue = WScript.Arguments(4)
			Call talos_pcom_wait(intRow, intCol, intLon, strValue)
			Call talos_pcom_exit_ok(strParam1 & " " & intRow & " " & intCol & " " & intLon & " " & strValue)
			
		Case "get"
			If totalParam = 1 then
				Call talos_pcom_exit_error("Missing parameter 2: row number")
			End If
			If totalParam = 2 then
				Call talos_pcom_exit_error("Missing parameter 3: col number")
			End If
			If totalParam = 3 then
				Call talos_pcom_exit_error("Missing parameter 4: long number")
			End If
			intRow   = WScript.Arguments(1)
			intCol   = WScript.Arguments(2)
			intLon   = WScript.Arguments(3)
			strValue = talos_pcom_get(intRow, intCol, intLon)
			Call talos_pcom_exit_ok(strValue)
		
		Case "ftp"
			If totalParam = 1 then
				Call talos_pcom_exit_error("Missing parameter 2: operation type put/get")
			End If
			If totalParam = 2 then
				Call talos_pcom_exit_error("Missing parameter 3: PC file name")
			End If
			If totalParam = 3 then
				Call talos_pcom_exit_error("Missing parameter 4: HOST file name")
			End If
			operType     = WScript.Arguments(1)
			PCfileName   = WScript.Arguments(2)
			HOSTfileName = WScript.Arguments(3)
			Call talos_pcom_ftp_exec(operType, PCfileName, HOSTfileName)
			Call talos_pcom_exit_ok(operType & " " & PCfileName & " " & HOSTfileName)
		
		Case Else
			Call talos_pcom_exit_error("Parameter not considered: " & strParam1)
		
	End Select
	
End Function


'=======================================================================================================================
' Exit script with error
'=======================================================================================================================
Function talos_pcom_exit_error(strMessage)
	
	WScript.Echo "<:result:>Error: " & strMessage
	WScript.Quit(2)

End Function


'=======================================================================================================================
' Exit script with ok
'=======================================================================================================================
Function talos_pcom_exit_ok(strMessage)
	
	WScript.Echo "<:result:>Ok: " & strMessage
	WScript.Quit

End Function


'=======================================================================================================================
' Check if a file path is correct
'=======================================================================================================================
Function talos_pcom_file_exist(strFilePath)
	
	If strFilePath <> "" Then
		Dim objFS
		Set objFS = CreateObject("Scripting.FileSystemObject")
		If objFS.FileExists(strFilePath) Then
			talos_pcom_file_exist = "ok"
		Else
			talos_pcom_file_exist = "File does not exist"
		End If
	Else
		talos_pcom_file_exist = "Empty file name"
	End If

End Function


'=======================================================================================================================
' Terminate running processes 
'=======================================================================================================================
Function talos_pcom_task_close(strProc)
	
	strLit = "talos_pcom_task_close(""" & strProc & """): "
	
	On Error Resume Next
		
		Dim objWMIService : Set objWMIService = GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2")
		Dim objProcesses : Set objProcesses = objWMIService.ExecQuery("SELECT * FROM Win32_Process WHERE Name='" &  strProc & "'")
		
		If objProcesses.count > 0 Then
			strDesc = strLit & "Total processes: " & objProcesses.count
			For Each objProcess in objProcesses
				intTermProc = objProcess.Terminate
				strDesc = strLit & "OK - finished process " & objProcess.ProcessId & " " & objProcess.Name
			Next
		End If
	
	On Error GoTo 0

End Function


'=======================================================================================================================
' Check a number between a minimum value and a maximum value
'
'=======================================================================================================================
Function talos_pcom_check_range(intNum, intMin, intMax)
	
	If intNum <> "" Then
		If IsNumeric(intNum) Then
			intNum = CInt(intNum)
			If intNum > (intMin - 1) And intNum < (intMax + 1) Then
				talos_pcom_check_range = "ok"
			Else
				talos_pcom_check_range = "Number out of range [" & intMin & "-" & intMax & "]: " & intNum
			End If
		Else
			talos_pcom_check_range = "It is not a number: '" & intNum & "' "
		End If
	Else
		talos_pcom_check_range = "Empty value: '" & intNum & "' "
	End If

End Function


'=======================================================================================================================
' IBM Personal Communications automation: get session
'
'=======================================================================================================================
Function talos_pcom_get_session()
	
	On Error Resume Next
		Set autECLSession = CreateObject("PCOMM.autECLSession")
		Set autECLOIA     = CreateObject("PCOMM.autECLOIA")
		Set autECLPS      = CreateObject("PCOMM.autECLPS")
		autECLSession.SetConnectionByName (HOSTSESSION)
		autECLSession.autECLOIA.WaitForAppAvailable
		If Err.Number <> 0 Then
			strDesc = "Failed to create object autECLSession: " & Err.Number & " - " & Err.Description
			Call talos_pcom_exit_error(strDesc)
		End If
	On Error GoTo 0
	
End Function


'=======================================================================================================================
' IBM Personal Communications automation: open session
'
'=======================================================================================================================
Function talos_pcom_open(strPath)
	
	strLit = "talos_pcom_open('" & strPath & "'): "
	strRes = talos_pcom_file_exist(strPath)
	If strRes <> "ok" Then
		strDesc = strLit & "Error - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	Call talos_pcom_close()
	
	strConexionHost = "profile=" & strPath & " connname=" & HOSTSESSION
	
	On Error Resume Next
		Set autECLConnMgr = CreateObject("PCOMM.autECLConnMgr")
		Set autECLSession = CreateObject("PCOMM.autECLSession")
		Set autECLOIA = CreateObject("PCOMM.autECLOIA")
		Set autECLPS = CreateObject("PCOMM.autECLPS")
		autECLConnMgr.StartConnection (strConexionHost)
		autECLSession.SetConnectionByName (HOSTSESSION)
		autECLSession.autECLOIA.WaitForAppAvailable
		If Err.Number <> 0 Then
			strDesc = strLit & "Error - Failed to open Host emulator. " & Err.Number & " - " & Err.Description
			Call talos_pcom_exit_error(strDesc)
		End If
	On Error GoTo 0
	
	strDesc = strLit & "OK"
	
	' Maximize window
	On Error Resume Next
		Set objShell = WScript.CreateObject("WScript.Shell")
		objShell.SendKeys "% x"
		If Err.Number <> 0 Then
		End If
	On Error GoTo 0	

End Function


'=======================================================================================================================
' IBM Personal Communications automation: close session
'
'=======================================================================================================================
Function talos_pcom_close()
	
	Call talos_pcom_task_close("pcsws.exe")
	Call talos_pcom_task_close("pcscm.exe")

End Function


'=======================================================================================================================
' IBM Personal Communications automation: put value on a position in emulator window
'
'=======================================================================================================================
Function talos_pcom_put(intRow, intCol, strValue)
	
	Call talos_pcom_get_session()
	
	strLit = "talos_pcom_put(" & intRow & ", " & intCol & ", """ & strValue & """): "
	
	strRes = talos_pcom_check_range(intRow, 1, 24)
	If strRes <> "ok" Then
		strDesc = strLit & "Error in param 1 - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	strRes = talos_pcom_check_range(intCol, 1, 80)
	If strRes <> "ok" Then
		strDesc = strLit & "Error in param 2 - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	If Len(strValue) = 0 Then
		strDesc = strLit & "Error in param 3 - Empty value"
		Call talos_pcom_exit_error(strDesc)		
	End If
	
	strResFun = talos_pcom_set_cursor(intRow, intCol)
	
	If strResFun = "ok" Then
		autECLSession.autECLOIA.WaitForInputReady
		autECLSession.autECLPS.SendKeys strValue
		strDesc = strLit & "OK"
	Else
		strDesc = strLit & "Error: " & strResFun
		Call talos_pcom_exit_error(strDesc)
	End If

End Function


'=======================================================================================================================
' IBM Personal Communications automation: put cursor on a position in emulator window
'
'=======================================================================================================================
Function talos_pcom_set_cursor(intRow, intCol)
	
	strLit = "talos_pcom_set_cursor(" & intRow & ", " & intCol & "): "
	
	strRes = talos_pcom_check_range(intRow, 1, 24)
	If strRes <> "ok" Then
		strDesc = strLit & "Error in param 1 - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	strRes = talos_pcom_check_range(intCol, 1, 80)
	If strRes <> "ok" Then
		strDesc = strLit & "Error in param 2 - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	autECLSession.autECLOIA.WaitForAppAvailable
	autECLSession.autECLPS.SetCursorPos intRow, intCol
	talos_pcom_set_cursor = "ok"
	strDesc = strLit & "OK"

End Function


'=======================================================================================================================
' IBM Personal Communications automation: press a key
'
'=======================================================================================================================
Function talos_pcom_key(strKey)
	
	Call talos_pcom_get_session()
	
	strLit = "talos_pcom_key('" & strKey & "'): "
	strKey = UCase(strKey)
	
	If strKey <> "" Then
		If  strKey = "ENTER" Or _
			strKey = "PF1" Or _
			strKey = "PF2" Or _
			strKey = "PF3" Or _
			strKey = "PF4" Or _
			strKey = "PF5" Or _
			strKey = "PF6" Or _
			strKey = "PF7" Or _
			strKey = "PF8" Or _
			strKey = "PF9" Or _
			strKey = "PF10" Or _
			strKey = "PF11" Or _
			strKey = "PF12" Then
			strKeyAux = "[" & strKey & "]"
			autECLSession.autECLPS.SendKeys strKeyAux
			strDesc = strLit & "OK"

		ElseIf Left(strKey, 2) = "->" Then
			strFilaCol = Split(Mid(strKey, 3, Len(strKey) - 2), ";")
			strFormat = "error"
			strKeyAux = "[ERASE EOF]"
			If UBound(strFilaCol) = 1 Then
				If IsNumeric(strFilaCol(0)) Then
					If IsNumeric(strFilaCol(1)) Then
						intRow = CInt(strFilaCol(0))
						intCol = CInt(strFilaCol(1))
						strFormat = "ok"
					End If
				End If
			End If
			If strFormat = "ok" Then
				strResFun = talos_pcom_set_cursor(intRow, intCol)
				If strResFun = "ok" Then
					autECLSession.autECLPS.SendKeys strKeyAux
					strDesc = strLit & strKeyAux & " - OK, pressed key in row/col " & intRow & "/" & intCol

				Else
					strDesc = strLit & strKeyAux & ", Error in operation result"
					Call talos_pcom_exit_error(strDesc)
				End If
			Else
				strDesc = strLit & strKeyAux & ", Error in row/col: '" & strFilaCol & "' "
				Call talos_pcom_exit_error(strDesc)
			End If
		Else
			strDesc = strLit & ", Error - undefined key: '" & strKey & "' "
			Call talos_pcom_exit_error(strDesc)
		End If
	Else
		strDesc = strLit & ", Error: There is no introduced key"
		Call talos_pcom_exit_error(strDesc)
	End If

End Function


'=======================================================================================================================
' IBM Personal Communications automation: wait for a text on a position in emulator window
'
'=======================================================================================================================
Function talos_pcom_wait(intRow, intCol, intLon, strValue)
	
	Call talos_pcom_get_session()
	
	strLit = "talos_pcom_wait(" & intRow & ", " & intCol & ", " & intLon & ", """ & strValue & """): "
	
	strRes = talos_pcom_check_range(intRow, 1, 24)
	If strRes <> "ok" Then
		strDesc = strLit & "Error in param 1 - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	strRes = talos_pcom_check_range(intCol, 1, 80)
	If strRes <> "ok" Then
		strDesc = strLit & "Error in param 2 - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	strRes = talos_pcom_check_range(intLon, 1, 80)
	If strRes <> "ok" Then
		strDesc = strLit & "Error in param 3 - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	If strValue = "" Then
		strDesc = strLit & "Error in param 4 - Empty value"
		Call talos_pcom_exit_error(strDesc)
	End If
	
	milisegundos = CLng(intHOSTespera * 1000)
	strLimiteTimeout = Now + (milisegundos * 0.00000001)
	
	Do
		strTextoAparecido = RTrim(autECLSession.autECLPS.GetText(intRow, intCol, intLon))
		On Error Resume Next
			WScript.sleep 50
			If Err.Number <> 0 Then
				Wait 0, 50
			End If
		On Error GoTo 0		
	Loop While strTextoAparecido <> strValue And strLimiteTimeout > Now
	
	If strTextoAparecido = strValue Then
		talos_pcom_wait = "ok"
	Else
		strDesc = strLit & "Error - literal not expected: '" & strTextoAparecido & "' "
		Call talos_pcom_exit_error(strDesc)
	End If

End Function


'=======================================================================================================================
' IBM Personal Communications automation: get text from a position in emulator window
'
'=======================================================================================================================
Function talos_pcom_get(intRow, intCol, intLon)
	
	Call talos_pcom_get_session()
	
	strLit = "talos_pcom_get(" & intRow & ", " & intCol & ", " & intLon & "): "
	
	strRes = talos_pcom_check_range(intRow, 1, 24)
	If strRes <> "ok" Then
		strDesc = strLit & "Error in param 1 - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	strRes = talos_pcom_check_range(intCol, 1, 80)
	If strRes <> "ok" Then
		strDesc = strLit & "Error in param 2 - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	strRes = talos_pcom_check_range(intLon, 1, 80)
	If strRes <> "ok" Then
		strDesc = strLit & "Error in param 2 - " & strRes
		Call talos_pcom_exit_error(strDesc)
	End If
	
	autECLSession.autECLOIA.WaitForAppAvailable
	autECLSession.autECLOIA.WaitForInputReady
	strValorAux = autECLSession.autECLPS.GetText(intRow, intCol, intLon)
	
	strDesc = strLit & "OK - value obtained: '" & strValorAux & "' "
	
	
	talos_pcom_get = strValorAux

End Function


'=======================================================================================================================
' Execute FTP instruction from PC
'
'=======================================================================================================================
Function talos_pcom_ftp_exec(operType, PCfileName, HOSTfileName)
	
	strLit = "talos_pcom_ftp_exec(" & operType & ", " & PCfileName & ", " & HOSTfileName & "): "
	
	If LCase(operType) = "put" Then
		internalOper = "send"
	ElseIf LCase(operType) = "get" Then
		internalOper = "receive"
	Else
		strDesc = strLit & "Operation type must be put or get, found: " & operType
		Call talos_pcom_exit_error(strDesc)
	End If
	
	strInstruction = _
		"%comspec% /c " &_
		internalOper &_
		" """ & PCfileName   & """ " &_
		HOSTSESSION & ": "   &_
		"'"   & HOSTfileName & "' "  &_
		"ASCII CRLF "
	
	Set objFileSystem = CreateObject("Scripting.FileSystemObject")
	Set objWScriptShell = CreateObject("WScript.Shell")
	
	strResultRutaTemp = objWScriptShell.ExpandEnvironmentStrings("%TEMP%")
	strResultArchivo = strResultRutaTemp & "\" & objFileSystem.GetTempName
	strInstruction = strInstruction & " > " & strResultArchivo
	
	objWScriptShell.Run strInstruction, 0, True
	
	'Leer el archivo de resultado de la instrucción (solo lectura) y borrarlo
	Set objArchResult = objFileSystem.OpenTextFile(strResultArchivo, 1, False)
	strResultText = objArchResult.ReadAll
	objArchResult.Close
	objFileSystem.DeleteFile (strResultArchivo)
	
	If InStr(strResultText, "Transferencia de archivos completa") > 0 Then
		'strDesc = strLit & "OK - result obtained: '" & strResultText & "' "
		'talos_pcom_ftp_exec = "OK"
	ElseIf InStr(strResultText, "File transfer complete") > 0 Then
		'strDesc = strLit & "OK - result obtained: '" & strResultText & "' "
		'talos_pcom_ftp_exec = "OK"			
	ElseIf InStr(strResultText, "PCSXFER040") > 0 Then
		strLitErr = "Mainframe window must be in command mode (ISPF option 6)"
		strDesc = strLit & "Error obtained: " & strLitErr
		Call talos_pcom_exit_error(strDesc)
		'talos_pcom_ftp_exec = strLitErr
	Else
		strDesc = strLit & "Error obtained: " & strResultText
		Call talos_pcom_exit_error(strDesc)
		'talos_pcom_ftp_exec = strResultText
	End If
	
	Set objFileSystem = Nothing
	Set objWScriptShell = Nothing

End Function


'=======================================================================================================================
' Minimize all windows
'
'=======================================================================================================================
Function talos_pcom_minimize_all()
	
	Set objShell = CreateObject("shell.application")
	objShell.MinimizeAll

End Function
