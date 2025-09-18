@echo off
REM GPT Researcher MCP Server Deployment Script
REM ============================================
REM This script builds and deploys the MCP server to the network share

echo.
echo ==================================================
echo   GPT Researcher MCP Server - Build and Deploy
echo ==================================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python virtual environment is available
if not exist "C:\Users\ianimash\source\repos\venvs\gpt-researcher\Scripts\python.exe" (
    echo ERROR: Python virtual environment not found!
    echo Expected: C:\Users\ianimash\source\repos\venvs\gpt-researcher\Scripts\python.exe
    echo.
    echo Please ensure the virtual environment is set up correctly.
    pause
    exit /b 1
)

echo Step 1: Building MCP Server executable...
echo ------------------------------------------
C:\Users\ianimash\source\repos\venvs\gpt-researcher\Scripts\python.exe build_mcp_streaming.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Please check the build output above for errors.
    pause
    exit /b 1
)

echo.
echo Step 2: Deploying to network share...
echo ------------------------------------
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
echo   Build and Deployment completed successfully!
echo ============================================
echo.
echo The MCP server has been built and deployed.
echo Local copy remains in: %~dp0dist\
echo Network copy deployed to: \\IREGPT1\mcp-servers\
echo.
pause