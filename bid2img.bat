@echo off
set args=%1
:More
shift
if '%1'=='' goto Done
set args=%args%, %1
goto More
:Done
(for %%a in (%args%) do ( 
   .\bid2img.py --path_bid %%a --no_display_image
))
pause