@echo off

call %~dp0telegram_bot\venv\Scripts\activate

cd %~dp0telegram_bot

set TOKEN=5272216108:AAEAdG72QfeB95dwcGLliF_Cv_X_Ou0ZU44

python bot_telegram.py

pause