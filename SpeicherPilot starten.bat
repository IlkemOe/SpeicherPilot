@echo off
rem Startet SpeicherPilot ohne Konsolenfenster
where pythonw >nul 2>nul && (start "" pythonw "%~dp0speicherpilot.py" & exit /b)
where pyw >nul 2>nul && (start "" pyw "%~dp0speicherpilot.py" & exit /b)
echo Python wurde nicht gefunden. Bitte Python 3.10+ von python.org installieren.
pause
