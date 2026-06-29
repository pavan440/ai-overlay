@echo off
echo ════════════════════════════════════
echo   Building AI Overlay  (.exe)
echo ════════════════════════════════════
cd /d "%~dp0"

pyinstaller overlay.spec --noconfirm

if exist "dist\AIOverlay\AIOverlay.exe" (
    echo.
    echo ✓ Build complete: dist\AIOverlay\AIOverlay.exe
    echo   Copy the entire dist\AIOverlay\ folder anywhere you like.
    echo   Run AIOverlay.exe  — no Python needed.
) else (
    echo.
    echo ✗ Build failed. Check output above.
)
pause
