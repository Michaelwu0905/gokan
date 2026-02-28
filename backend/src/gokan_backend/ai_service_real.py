import openai
from .config import (
    MOONSHOT_API_KEY,
    OPENAI_API_KEY,
    AZURE_TTS_KEY,
    AZURE_TTS_REGION,
    AZURE_TTS_VOICE,
    USE_REAL_AI,
    USE_REAL_WHISPER,
    USE_REAL_TTS,
)
from .ai_service import VirtualAIService, SCENARIOS


class RealAIService(VirtualAIService):
    """支持真实API的AI服务"""

    def __init__(self):
        super().__init__()

        # 初始化 Moonshot 客户端
        if USE_REAL_AI and MOONSHOT_API_KEY:
            self.moonshot_client = openai.OpenAI(
                api_key=MOONSHOT_API_KEY, base_url="https://api.moonshot.cn/v1"
            )
        else:
            self.moonshot_client = None

        # 初始化 OpenAI 客户端 (Whisper)
        if USE_REAL_WHISPER and OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        else:
            self.openai_client = None

        # Azure TTS 配置
        self.use_real_tts = USE_REAL_TTS and AZURE_TTS_KEY
        self.azure_key = AZURE_TTS_KEY
        self.azure_region = AZURE_TTS_REGION
        self.azure_voice = AZURE_TTS_VOICE

    def generate_response(
        self, scenario_id: int, user_message: str, conversation_history: list
    ):
        """生成AI回复，优先使用真实API"""

        # 如果没有配置真实AI，使用虚拟模式
        if not self.moonshot_client:
            return super().generate_response(
                scenario_id, user_message, conversation_history
            )

        # 使用 Moonshot Kimi 生成回复
        try:
            scenario = self.get_scenario(scenario_id)

            # 构建系统提示词
            system_prompt = self._build_system_prompt(scenario)

            # 构建对话历史
            messages = [{"role": "system", "content": system_prompt}]

            # 添加历史对话（限制最近10条）
            for msg in conversation_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})

            # 调用 Moonshot API
            response = self.moonshot_client.chat.completions.create(
                model="moonshot-v1-8k",  # 或其他适合的模型
                messages=messages,
                temperature=0.7,
                max_tokens=200,
            )

            ai_response = response.choices[0].message.content

            # 分析错误（使用虚拟的错误检测，或使用简单的规则）
            errors = self._analyze_errors(user_message)

            return ai_response, errors

        except Exception as e:
            print(f"Error calling Moonshot API: {e}")
            # 出错时回退到虚拟模式
            return super().generate_response(
                scenario_id, user_message, conversation_history
            )

    def _build_system_prompt(self, scenario: dict) -> str:
        """构建系统提示词"""
        prompt = f"""你正在扮演一个日语对话练习中的角色。

角色设定：
- 姓名：{scenario["character_name"]}
- 简介：{scenario["character_profile"]}
- 场景：{scenario["name_jp"]}（{scenario["name"]}）

对话要求：
1. 使用N4级别以下的简单日语
2. 保持角色的语气和特点
3. 回复要简短自然（2-3句话）
4. 适当使用敬语
5. 如果对方日语有错误，在回复中自然地使用正确的说法
6. 保持对话流畅，适当提问来延续对话

请用日语回复。"""
        return prompt

    def transcribe_audio(self, audio_file_path: str) -> str:
        """语音转文字，使用 Whisper"""
        if not self.openai_client:
            # 虚拟模式：返回提示
            return "[语音输入 - 请先配置 OPENAI_API_KEY]"

        try:
            with open(audio_file_path, "rb") as audio_file:
                response = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file, language="ja"
                )
            return response.text
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return "[语音识别失败，请重试]"

    def generate_speech(self, text: str) -> str:
        """文字转语音，使用 Azure TTS"""
        if not self.use_real_tts:
            # 虚拟模式：返回模拟URL
            import uuid

            return f"/audio/mock/{uuid.uuid4()}.mp3"

        try:
            import requests

            # Azure TTS API endpoint
            url = f"https://{self.azure_region}.tts.speech.microsoft.com/cognitiveservices/v1"

            headers = {
                "Ocp-Apim-Subscription-Key": self.azure_key,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
            }

            # 构建 SSML
            ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='ja-JP'>
                <voice name='{self.azure_voice}'>
                    {text}
                </voice>
            </speak>"""

            response = requests.post(url, headers=headers, data=ssml.encode("utf-8"))

            if response.status_code == 200:
                # 保存音频文件并返回URL
                import uuid

                audio_filename = f"{uuid.uuid4()}.mp3"
                audio_path = f"/tmp/gokan_audio/{audio_filename}"

                import os

                os.makedirs("/tmp/gokan_audio", exist_ok=True)

                with open(audio_path, "wb") as f:
                    f.write(response.content)

                return f"/audio/{audio_filename}"
            else:
                print(f"Azure TTS error: {response.status_code}")
                return f"/audio/mock/{uuid.uuid4()}.mp3"

        except Exception as e:
            print(f"Error generating speech: {e}")
            import uuid

            return f"/audio/mock/{uuid.uuid4()}.mp3"


# 创建全局服务实例
ai_service = RealAIService()
