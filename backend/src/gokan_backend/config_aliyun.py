# Aliyun NLS (语音服务) Configuration
import os
from dotenv import load_dotenv

load_dotenv()

# Aliyun Credentials
ALIYUN_ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
ALIYUN_ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")
ALIYUN_APP_KEY = os.getenv("ALIYUN_APP_KEY", "")
ALIYUN_TTS_VOICE = os.getenv("ALIYUN_TTS_VOICE", "xiaoyun")

# Provider selection
AUDIO_PROVIDER = os.getenv("AUDIO_PROVIDER", "virtual")

# Feature flags
USE_ALIYUN_AUDIO = bool(
    ALIYUN_ACCESS_KEY_ID and ALIYUN_ACCESS_KEY_SECRET and ALIYUN_APP_KEY
)
