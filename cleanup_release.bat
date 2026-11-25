@echo off
cd /d "C:\dev\dyeness_av"

echo Cleaning up extra files from previous tags...

echo.
echo Removing fix*.py files:
for %%f in (fix_*.py) do (
    if exist "%%f" (
        echo   Deleting: %%f
        del "%%f"
    )
)

echo.
echo Removing check*.py files:
for %%f in (check_*.py) do (
    if exist "%%f" (
        echo   Deleting: %%f
        del "%%f"
    )
)

echo.
echo Cleanup complete.
echo.