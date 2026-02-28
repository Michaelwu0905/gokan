#!/bin/bash

# Gokan Backend Startup Script

echo "🎌 Starting Gokan Backend..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   Please edit .env and add your API keys."
    echo ""
fi

# Show current API status
echo "📋 API Configuration Status:"
echo ""

# Check Moonshot API
if grep -q "^MOONSHOT_API_KEY=sk-" .env 2>/dev/null; then
    echo "   ✅ Moonshot Kimi: Configured"
else
    echo "   ⚪ Moonshot Kimi: Not configured (using virtual mode)"
fi

# Check OpenAI API
if grep -q "^OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "   ✅ OpenAI Whisper: Configured"
else
    echo "   ⚪ OpenAI Whisper: Not configured (using virtual mode)"
fi

# Check Azure TTS
if grep -q "^AZURE_TTS_KEY=[a-zA-Z0-9]" .env 2>/dev/null; then
    echo "   ✅ Azure TTS: Configured"
else
    echo "   ⚪ Azure TTS: Not configured (using virtual mode)"
fi

echo ""
echo "🚀 Starting server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

# Start uvicorn
PYTHONPATH=./src uv run uvicorn gokan_backend.main:app --host 0.0.0.0 --port 8000 --reload
