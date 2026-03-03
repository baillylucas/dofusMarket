@echo off
echo ============================================================
echo   LANCEMENT DU SCRAPPER DOFUS - XP FAMILIER
echo ============================================================
echo.
echo Chargement des donnees...
echo.

cd /d "%~dp0"
uv run python scrapper\8_familier_xp_scrapper.py %*

echo.
echo ============================================================
if errorlevel 1 (
    echo ERREUR: Le script a rencontre une erreur
) else (
    echo TERMINE: Le scrapping XP familier est termine
)
echo ============================================================
echo.
pause
