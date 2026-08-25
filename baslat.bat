@echo off
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  echo Python bulunamadi. python.org uzerinden kurup tekrar dene.
  pause
  exit /b
)
python -c "import flask, requests" >nul 2>&1
if errorlevel 1 (
  echo Gerekli paketler kuruluyor...
  python -m pip install -r requirements.txt
)
python app.py
pause
