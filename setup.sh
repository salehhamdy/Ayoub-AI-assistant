#!/bin/bash
set -e

echo "=== Ayoub AI Assistant — Linux Setup ==="

# Install uv if not present
if ! command -v uv &>/dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install all Python deps
uv sync

# Create required directories
mkdir -p data/memory data/tmp logs output/imgs output/sketches templates

# Copy env template
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env created — fill in your API keys before running."
fi

echo ""
echo "Setup complete! Activate venv then run:"
echo "  ayoub -a 'Your question'    (ask mode)"
echo "  ayoub -c 'Hello'            (chat with memory)"
echo "  ayoub -m 'Search AI news'   (full ReAct agent)"
echo "  ayoub-server                (start MCP server on :8000)"
echo "  ayoub-voice                 (voice agent — requires LiveKit keys)"
echo ""
echo "To use Ollama (local model, no API key):"
echo "  ollama pull llama3"
echo "  # In .env: LLM_PROVIDER=ollama  LLM_MODEL=llama3"
