@echo off
setlocal enabledelayedexpansion

cd /d "C:\dev\dyeness_av"

echo ========================================
echo Running Dyness Aquavolt Modbus Tests
echo ========================================

echo.
echo [1/4] Installing test dependencies...
pip install -r requirements_test.txt -q 2>nul
if %ERRORLEVEL% neq 0 (
    echo WARNING: pip install may have failed, continuing anyway...
)

echo.
echo [2/4] Running test_decoding.py (28 tests)...
python -m pytest tests/test_decoding.py -v
if %ERRORLEVEL% neq 0 (
    echo WARNING: test_decoding.py had failures
)

echo.
echo [3/4] Running test_setup.py, test_modbus_client.py, test_config_flow.py, test_init.py...
python -m pytest tests/test_setup.py tests/test_modbus_client.py tests/test_config_flow.py tests/test_init.py -v
if %ERRORLEVEL% neq 0 (
    echo WARNING: Some tests had failures
)

echo.
echo [4/4] Running all tests...
python -m pytest tests/ -v
if %ERRORLEVEL% neq 0 (
    echo.
    echo ========================================
    echo TESTS FAILED
    echo ========================================
    exit /b 1
)

echo.
echo ========================================
echo ALL TESTS PASSED
echo ========================================
endlocal