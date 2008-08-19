@echo off
REM
REM This will setup a scheduled task that runs a batch file which inturn checks for myTV programme files.
REM Runs every MINUTE
REM
REM Put the full folder path in /TR ie. C:\XBMC\myTV_schedular.bat
REM
schtasks /create /TN "myTV Recording Schedular" /SC MINUTE /TR "\"G:\My Documents\My TV\myTV_schedular.bat\"" /RU SYSTEM
