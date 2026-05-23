@echo off
title Lancement Caisse Enregistreuse 🐾
echo ====================================================
echo   Lancement de la Caisse Enregistreuse de Miaou 🐱   
echo ====================================================
echo.
echo Demarrage de l'application...

start pythonw caisse.py

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] Impossible de lancer avec pythonw.
    echo Essai de lancement avec console standard...
    python caisse.py
    pause
)
