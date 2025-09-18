@echo off
REM GPT Researcher MCP Server - Deploy Only
REM ========================================
REM This script deploys an existing executable to the network share

echo.
echo ==========================================
echo   GPT Researcher MCP Server - Deploy Only
echo ==========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if executable exists
if not exist "dist\gpt-researcher-mcp-streaming.exe" (
    echo ERROR: Executable not found!
    echo Expected: %~dp0dist\gpt-researcher-mcp-streaming.exe
    echo.
    echo Please run build_and_deploy.bat first to create the executable.
    pause
    exit /b 1
)

REM Check if Python virtual environment is available
if not exist "C:\Users\ianimash\source\repos\venvs\gpt-researcher\Scripts\python.exe" (
    echo ERROR: Python virtual environment not found!
    echo Expected: C:\Users\ianimash\source\repos\venvs\gpt-researcher\Scripts\python.exe
    echo.
    echo Please ensure the virtual environment is set up correctly.
    pause
    exit /b 1
)

echo Deploying existing executable to network share...
echo ------------------------------------------------
C:\Users\ianimash\source\repos\venvs\gpt-researcher\Scripts\python.exe deploy_mcp_server.py

if errorlevel 1 (
    echo.
    echo ERROR: Deployment failed!
    echo Please check the deployment output above for errors.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Deployment completed successfully!
echo ============================================
echo.
pause