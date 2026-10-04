@echo off
rem Remove the Warma Encyclopedia scheduled task
schtasks /Delete /TN "WarmaEncyclopediaAutoUpdate" /F
echo Scheduled task removed.
pause