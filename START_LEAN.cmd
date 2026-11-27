@echo off
setlocal
pushd "%~dp0" || exit /b 1
where wsl.exe >nul 2>&1
if errorlevel 1 (
  echo WSL is not available. Open your Ubuntu terminal or install WSL first.
  pause
  popd
  exit /b 1
)
wsl.exe --exec bash ./lean_verification/run_local.sh
set "RESULT=%ERRORLEVEL%"
if "%RESULT%"=="0" (echo Verification finished successfully.) else (echo Verification did not finish. See the messages above.)
 echo Results folder: lean_verification\results
pause
popd
exit /b %RESULT%
