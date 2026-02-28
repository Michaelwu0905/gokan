import json
import time
import uuid
import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from .config_aliyun import (
    ALIYUN_ACCESS_KEY_ID,
    ALIYUN_ACCESS_KEY_SECRET,
    ALIYUN_APP_KEY,
    ALIYUN_TTS_VOICE,
    USE_ALIYUN_AUDIO,
)


class AliyunAudioService:
    """阿里云语音服务 (语音识别 + 语音合成)"""

    def __init__(self):
        self.access_key_id = ALIYUN_ACCESS_KEY_ID
        self.access_key_secret = ALIYUN_ACCESS_KEY_SECRET
        self.app_key = ALIYUN_APP_KEY
        self.voice = ALIYUN_TTS_VOICE
        self.enabled = USE_ALIYUN_AUDIO

        if self.enabled:
            self.client = AcsClient(
                self.access_key_id,
                self.access_key_secret,
                "cn-shanghai",  # NLS 服务在华东2(上海)
            )

    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        语音识别 (ASR)
        将日语语音转换为文字
        """
        if not self.enabled:
            return "[语音输入 - 请先配置阿里云语音服务]"

        try:
            # 读取音频文件
            with open(audio_file_path, "rb") as f:
                audio_data = f.read()

            # 构建请求
            request = CommonRequest()
            request.set_accept_format("json")
            request.set_domain("nls-meta.cn-shanghai.aliyuncs.com")
            request.set_method("POST")
            request.set_protocol_type("https")
            request.set_version("2019-02-28")
            request.set_action_name("CreateToken")

            # 获取 Token
            response = self.client.do_action_with_exception(request)
            token_info = json.loads(response)
            token = token_info.get("Token", {}).get("Id")

            if not token:
                return "[获取语音识别Token失败]"

            # 调用语音识别接口
            # 使用 RESTful API 方式
            url = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr"

            headers = {
                "X-NLS-Token": token,
                "Content-type": "application/octet-stream",
                "Content-Length": str(len(audio_data)),
            }

            params = {
                "appkey": self.app_key,
                "format": "wav",  # 或其他格式
                "sample_rate": "16000",
                "enable_punctuation_prediction": "true",
                "enable_intermediate_result": "false",
            }

            response = requests.post(
                url, params=params, headers=headers, data=audio_data, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == 20000000:
                    return result.get("result", "")
                else:
                    return f"[语音识别错误: {result.get('message', '未知错误')}]"
            else:
                return f"[语音识别请求失败: {response.status_code}]"

        except Exception as e:
            print(f"Error in Aliyun ASR: {e}")
            return "[语音识别失败，请重试]"

    def generate_speech(self, text: str) -> str:
        """
        语音合成 (TTS)
        将日语文字转换为语音
        """
        if not self.enabled:
            return f"/audio/mock/{uuid.uuid4()}.mp3"

        try:
            # 获取 Token
            request = CommonRequest()
            request.set_accept_format("json")
            request.set_domain("nls-meta.cn-shanghai.aliyuncs.com")
            request.set_method("POST")
            request.set_protocol_type("https")
            request.set_version("2019-02-28")
            request.set_action_name("CreateToken")

            response = self.client.do_action_with_exception(request)
            token_info = json.loads(response)
            token = token_info.get("Token", {}).get("Id")

            if not token:
                return f"/audio/mock/{uuid.uuid4()}.mp3"

            # 使用长文本语音合成接口
            url = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/tts"

            headers = {"X-NLS-Token": token, "Content-Type": "application/json"}

            payload = {
                "appkey": self.app_key,
                "text": text,
                "token": token,
                "format": "mp3",
                "sample_rate": 16000,
                "voice": self.voice,
                "volume": 50,
                "speech_rate": 0,
                "pitch_rate": 0,
            }

            response = requests.post(
                url, headers=headers, data=json.dumps(payload), timeout=30
            )

            if response.status_code == 200:
                # 保存音频文件
                audio_filename = f"{uuid.uuid4()}.mp3"
                audio_dir = "/tmp/gokan_audio"
                import os

                os.makedirs(audio_dir, exist_ok=True)
                audio_path = f"{audio_dir}/{audio_filename}"

                with open(audio_path, "wb") as f:
                    f.write(response.content)

                return f"/audio/{audio_filename}"
            else:
                print(f"Aliyun TTS error: {response.status_code}")
                return f"/audio/mock/{uuid.uuid4()}.mp3"

        except Exception as e:
            print(f"Error in Aliyun TTS: {e}")
            return f"/audio/mock/{uuid.uuid4()}.mp3"


# 全局实例
aliyun_audio = AliyunAudioService()
