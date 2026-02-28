# Environment variables configuration
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AZURE_TTS_KEY = os.getenv("AZURE_TTS_KEY", "")

# Azure TTS Settings
AZURE_TTS_REGION = os.getenv("AZURE_TTS_REGION", "japaneast")
AZURE_TTS_VOICE = os.getenv("AZURE_TTS_VOICE", "ja-JP-NanamiNeural")

# Application Settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# Feature flags - use real APIs if keys are provided
USE_REAL_AI = bool(MOONSHOT_API_KEY)
USE_REAL_WHISPER = bool(OPENAI_API_KEY)
USE_REAL_TTS = bool(AZURE_TTS_KEY)
