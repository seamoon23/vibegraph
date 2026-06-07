@echo off
setlocal EnableExtensions
set "VIBE_DIR=%~dp0"
if "%VIBE_DIR:~-1%"=="\" set "VIBE_DIR=%VIBE_DIR:~0,-1%"

echo.
echo ============================================================
echo    VibeGraph - 바이브코딩 순도 분석기  설치 마법사
echo ============================================================
echo    설치 위치: %VIBE_DIR%
echo.

REM ---- 1. Python 확인 ----
set "PYCMD="
where py >nul 2>nul && set "PYCMD=py"
if not defined PYCMD ( where python >nul 2>nul && set "PYCMD=python" )

if not defined PYCMD (
  echo [X] Python 이 설치되어 있지 않습니다.
  echo     https://www.python.org/downloads/  에서 설치하세요.
  echo     설치 첫 화면에서 "Add Python to PATH" 체크가 필수입니다.
  echo     설치 후 이 install.bat 을 다시 실행하세요.
  echo.
  echo ------------------------------------------------------------
  echo  창을 닫으려면 아무 키나 누르세요...
  pause >nul
  exit /b 1
)
echo [1/2] Python 확인 완료  (%PYCMD%)

REM ---- 2. PATH 등록 (PowerShell로 안전하게) ----
echo [2/2] vibe 명령어 PATH 등록 중...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$d='%VIBE_DIR%'; $p=[Environment]::GetEnvironmentVariable('PATH','User'); if([string]::IsNullOrEmpty($p)){$p=''}; if($p -notlike ('*'+$d+'*')){ $n=($p.TrimEnd(';')+';'+$d).TrimStart(';'); [Environment]::SetEnvironmentVariable('PATH',$n,'User'); Write-Host '      등록 완료 (새 터미널부터 적용)' } else { Write-Host '      이미 등록되어 있습니다' }"

REM ---- 성공 마커 파일 생성 ----
set "OKFILE=%VIBE_DIR%\_설치완료_OK.txt"
> "%OKFILE%" echo VibeGraph 설치가 정상 완료되었습니다.
>> "%OKFILE%" echo 설치 위치: %VIBE_DIR%
>> "%OKFILE%" echo 사용법: 새 터미널에서  vibe start 프로젝트명 작업명
>> "%OKFILE%" echo (이 파일은 설치 성공 표시용입니다. 지워도 됩니다.)

echo.
echo ############################################################
echo #                                                          #
echo #                  설치 성공!  (SUCCESS)                   #
echo #                                                          #
echo ############################################################
echo.
echo  - 별도 API 키나 추가 결제가 필요 없습니다.
echo  - 채점은 작업하던 Claude Code 창에서 이뤄집니다.
echo  - 확인용 파일 생성됨:  _설치완료_OK.txt
echo.
echo  [반드시] 지금 창은 닫고 *새 터미널*을 열어 사용하세요:
echo      vibe start  프로젝트명  작업명
echo      vibe prompt
echo      vibe end
echo      vibe stats
echo.
echo  잠시 후 사용 가이드(가이드.html)가 열립니다.
echo ============================================================
if exist "%VIBE_DIR%\가이드.html" start "" "%VIBE_DIR%\가이드.html"
echo.
echo  이 창은 아무 키나 누르면 닫힙니다...
pause >nul