@echo off
title Sistema de Busca de Documentos

echo ==================================================
echo  Sistema de Busca de Documentos (SRI)
echo ==================================================
echo.

REM --- Verifica se o Python esta instalado e no PATH ---
echo Verificando a instalacao do Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERRO: O comando 'python' nao foi encontrado.
    echo Por favor, instale o Python e adicione-o ao PATH do sistema.
    echo.
    pause
    exit /b 1
)
echo Python encontrado.
echo.

REM --- Instala as dependencias via pip ---
echo Instalando dependencias necessarias (PyPDF2)...
python -m pip install --quiet PyPDF2
echo Dependencias instaladas com sucesso.
echo.

REM --- Executa a interface grafica ---
echo Iniciando a interface grafica...
cd /d "%~dp0\src"
python InterfaceGrafica.py

