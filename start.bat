@echo off
echo ====================================
echo   API Aplicacion de Estudio
echo ====================================
echo.

echo Verificando dependencias...
pip install -r requirements.txt

echo.
echo Inicializando base de datos...
python database.py

echo.
echo Iniciando servidor API...
echo.
echo La aplicacion estara disponible en:
echo - API Principal: http://127.0.0.1:8000/
echo - Documentacion: http://127.0.0.1:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python -m uvicorn crud:app --reload

pause
