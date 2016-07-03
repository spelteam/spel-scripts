@echo off
set OLDDIR=%CD%
set UNITTESTS=D:\posebuild\tests\Debug\
set LOGFILE=D:\speltests.exe.log
set TEMPLOGFILE=D:\speltests.exe.log.temp
set TEMPRESULTS=D:\tests.results.temp
set RESULTS=D:\tests.results
set UPLOAD=D:\upload.script
set LOCK=D:\.windows.lock
set ARCH=D:\windowslogs.7z
cd %UNITTESTS%
if exist %LOGFILE% del %LOGFILE%
if exist %TEMPLOGFILE% del %TEMPLOGFILE%
if exist %TEMPRESULTS% del %TEMPRESULTS%
if exist %RESULTS% del %RESULTS%
if exist %UPLOAD% del %UPLOAD%
if exist %LOCK% del %LOCK%
speltests.exe > %LOGFILE% 2>&1
type %LOGFILE% | findstr /C:"[ RUN      ]" > %TEMPLOGFILE%
for /f "tokens=*" %%a in (%TEMPLOGFILE%) do call :PROCESSLINE %%a
goto :PROCESS
:PROCESSLINE
set line=%*
set line=%line:~13%
speltests.exe --gtest_filter=%line% >> %TEMPRESULTS% 2>&1
goto :EOF
:PROCESS
type %TEMPRESULTS% | findstr /C:"[       OK ]" > %RESULTS%
type %TEMPRESULTS% | findstr /C:"[  FAILED  ]" >> %RESULTS%
start /wait "" "C:\Program Files\7-Zip\7z.exe" a %ARCH% %LOGFILE% %TEMPLOGFILE% %TEMPRESULTS% %RESULTS%
echo LOCK > %LOCK%
echo put %ARCH% > %UPLOAD%
echo put %RESULTS% > %UPLOAD%
echo put %LOCK% >> %UPLOAD%
echo exit >> %UPLOAD%
start /wait "" "C:\Program Files (x86)\PuTTY\psftp.exe" -b %UPLOAD%
if exist %LOGFILE% del %LOGFILE%
if exist %TEMPLOGFILE% del %TEMPLOGFILE%
if exist %TEMPRESULTS% del %TEMPRESULTS%
if exist %RESULTS% del %RESULTS%
if exist %UPLOAD% del %UPLOAD%
if exist %LOCK% del %LOCK%
cd /
cd %OLDDIR%
goto :EOF
:EOF
