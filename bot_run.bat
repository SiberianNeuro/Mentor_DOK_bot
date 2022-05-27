@echo off

call %~dp0Mentor_DOK_bot\venv\Scripts\activate

cd %~dp0Mentor_DOK_bot

set TOKEN=''

python bot_telegram.py

pause
