import os
import base64
import json
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

from .models import AnalyzeData, GrammarPoint, ExampleSentence

load_dotenv()

SYSTEM_PROMPT = """你是一个专业的日语教师。请分析图片中的日语文本，并按以下要求处理：

1. 提取图片中的所有日语文本
2. 提供精确的中文翻译
3. 为原文中的汉字标注平假名读音
4. 拆解核心语法点，解释词性和用法
5. 提供一个包含核心语法或单词的例句及其中文翻译

重要：请严格按照以下JSON格式输出，不要包含markdown代码块标记，不要添加任何额外说明：

{
    "original_text": "提取出的日文原文",
    "translation": "对应的中文翻译",
    "furigana": "原文的平假名注音（仅针对汉字标注）",
    "grammar_analysis": [
        {"word": "单词或语法点1", "explanation": "词性与用法解释"},
        {"word": "单词或语法点2", "explanation": "词性与用法解释"}
    ],
    "example_sentence": {
        "japanese": "包含核心语法或单词的日文例句",
        "chinese": "例句的中文翻译"
    }
}"""

# 模拟数据（用于测试模式）
MOCK_RESPONSE = {
    "original_text": "こんにちは、今日は良い天気ですね。",
    "translation": "你好，今天天气真好啊。",
    "furigana": "こんにちは、きょうはよいてんきですね。",
    "grammar_analysis": [
        {"word": "こんにちは", "explanation": "问候语，意为'你好'，用于白天见面时"},
        {"word": "今日(きょう)", "explanation": "名词，意为'今天'"},
        {"word": "良い(よい)", "explanation": "形容词，意为'好的'，修饰后面的名词"},
        {"word": "天気(てんき)", "explanation": "名词，意为'天气'"},
        {"word": "です", "explanation": "判断助动词，用于礼貌体陈述句结尾"},
        {"word": "ね", "explanation": "终助词，表示确认、感叹或征求对方同意"},
    ],
    "example_sentence": {"japanese": "こんにちは、お元気ですか。", "chinese": "你好，你还好吗？"},
}


class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"

        if not api_key and not self.mock_mode:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. Set MOCK_MODE=true for testing."
            )

        if not self.mock_mode:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        else:
            print("🧪 Running in MOCK MODE - AI responses will be simulated")

    def analyze_image(self, image_base64: str) -> AnalyzeData:
        """分析图片中的日语文本"""
        # 模拟模式：直接返回模拟数据
        if self.mock_mode:
            import time

            time.sleep(0.5)  # 模拟网络延迟
            return self._parse_response(MOCK_RESPONSE)

        # 移除 base64 前缀（如果有）
        if image_base64.startswith("data:image"):
            image_base64 = image_base64.split(",")[1]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                            }
                        ],
                    },
                ],
                max_tokens=2000,
                temperature=0.3,
            )

            content = response.choices[0].message.content.strip()

            # 解析 JSON 响应
            try:
                data = json.loads(content)
                return self._parse_response(data)
            except json.JSONDecodeError as e:
                # 尝试从 markdown 代码块中提取
                import re

                json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
                if json_match:
                    data = json.loads(json_match.group(1))
                    return self._parse_response(data)
                raise ValueError(f"Failed to parse LLM response as JSON: {e}")

        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")

    def _parse_response(self, data: dict) -> AnalyzeData:
        """解析响应数据"""
        grammar_analysis = [
            GrammarPoint(word=item["word"], explanation=item["explanation"])
            for item in data.get("grammar_analysis", [])
        ]

        example = data.get("example_sentence", {})
        example_sentence = ExampleSentence(
            japanese=example.get("japanese", ""), chinese=example.get("chinese", "")
        )

        return AnalyzeData(
            original_text=data.get("original_text", ""),
            translation=data.get("translation", ""),
            furigana=data.get("furigana", ""),
            grammar_analysis=grammar_analysis,
            example_sentence=example_sentence,
        )
