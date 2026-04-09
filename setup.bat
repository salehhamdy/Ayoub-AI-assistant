@echo off
echo === Ayoub AI Assistant - Windows Setup ===

:: Check for uv
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing uv...
    pip install uv
)

:: Install all Python deps
uv sync

:: Create required directories
if not exist "data\memory"      mkdir "data\memory"
if not exist "data\tmp"         mkdir "data\tmp"
if not exist "logs"             mkdir "logs"
if not exist "output\imgs"      mkdir "output\imgs"
if not exist "output\sketches"  mkdir "output\sketches"
if not exist "templates"        mkdir "templates"

:: Copy env template
if not exist ".env" (
    copy ".env.example" ".env"
    echo .env created - fill in your API keys before running.
)

echo.
echo Setup complete! Run:
echo   ayoub -a "Your question"    (ask mode)
echo   ayoub -c "Hello"            (chat with memory)
echo   ayoub -m "Search AI news"   (full ReAct agent)
echo   ayoub-server                (start MCP server on :8000)
echo   ayoub-voice                 (voice agent - requires LiveKit keys)
echo.
echo To use Ollama (local model, no API key):
echo   ollama pull llama3
echo   In .env: LLM_PROVIDER=ollama   LLM_MODEL=llama3
