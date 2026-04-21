import os
import base64
import json
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

from .models import AnalyzeData, FuriganaToken, VocabItem, GrammarPoint, ExampleSentence

load_dotenv()

SYSTEM_PROMPT = """你是一个专业的日语教师。请分析图片中的日语文本，严格按以下JSON格式输出，不含markdown标记，不添加任何额外说明：

{
    "original_text": "提取出的日文原文",
    "translation": "对应的中文翻译",
    "furigana_tokens": [
        {"text": "今日", "reading": "きょう"},
        {"text": "は", "reading": ""},
        {"text": "良", "reading": "よ"},
        {"text": "い", "reading": ""},
        {"text": "天気", "reading": "てんき"},
        {"text": "です", "reading": ""},
        {"text": "ね", "reading": ""}
    ],
    "vocabulary": [
        {"word": "今日", "reading": "きょう", "meaning": "今天", "part_of_speech": "名詞"},
        {"word": "天気", "reading": "てんき", "meaning": "天气", "part_of_speech": "名詞"}
    ],
    "grammar_analysis": [
        {"word": "は", "reading": "", "part_of_speech": "助詞", "explanation": "主题助词，提示句子主题"},
        {"word": "です", "reading": "", "part_of_speech": "助動詞", "explanation": "礼貌体断定助动词，用于句末表示礼貌陈述"},
        {"word": "ね", "reading": "", "part_of_speech": "終助詞", "explanation": "终助词，表示确认或征求对方同意"}
    ],
    "example_sentences": [
        {"japanese": "今日は暑いですね。", "furigana": "きょうはあついですね。", "chinese": "今天真热啊。"},
        {"japanese": "明日も良い天気でしょう。", "furigana": "あしたもよいてんきでしょう。", "chinese": "明天也会是好天气吧。"}
    ]
}

规则：
- furigana_tokens：原文每个词/字符一个token，纯假名和标点的reading留空字符串
- vocabulary：仅列出实词（名词、动词、形容词、副词），2-6个
- grammar_analysis：列出助词、助动词、重要语法结构，2-5个
- example_sentences：提供2个例句，包含原文中的核心词汇或语法
- 所有字段必须存在，不可省略"""

# 模拟数据（用于测试模式）
MOCK_RESPONSE = {
    "original_text": "こんにちは、今日は良い天気ですね。",
    "translation": "你好，今天天气真好啊。",
    "furigana_tokens": [
        {"text": "こんにちは", "reading": ""},
        {"text": "、", "reading": ""},
        {"text": "今日", "reading": "きょう"},
        {"text": "は", "reading": ""},
        {"text": "良", "reading": "よ"},
        {"text": "い", "reading": ""},
        {"text": "天気", "reading": "てんき"},
        {"text": "です", "reading": ""},
        {"text": "ね", "reading": ""},
        {"text": "。", "reading": ""},
    ],
    "vocabulary": [
        {"word": "今日", "reading": "きょう", "meaning": "今天", "part_of_speech": "名詞"},
        {"word": "良い", "reading": "よい", "meaning": "好的", "part_of_speech": "形容詞"},
        {"word": "天気", "reading": "てんき", "meaning": "天气", "part_of_speech": "名詞"},
    ],
    "grammar_analysis": [
        {"word": "こんにちは", "reading": "", "part_of_speech": "感動詞", "explanation": "问候语，意为'你好'，用于白天见面时"},
        {"word": "は", "reading": "", "part_of_speech": "助詞", "explanation": "主题助词，提示句子主题"},
        {"word": "です", "reading": "", "part_of_speech": "助動詞", "explanation": "判断助动词，用于礼貌体陈述句结尾"},
        {"word": "ね", "reading": "", "part_of_speech": "終助詞", "explanation": "终助词，表示确认、感叹或征求对方同意"},
    ],
    "example_sentences": [
        {"japanese": "こんにちは、お元気ですか。", "furigana": "こんにちは、おげんきですか。", "chinese": "你好，你还好吗？"},
        {"japanese": "今日は良い天気なので、散歩しましょう。", "furigana": "きょうはよいてんきなので、さんぽしましょう。", "chinese": "今天天气好，去散步吧。"},
    ],
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
        if self.mock_mode:
            import time

            time.sleep(0.5)
            return self._parse_response(MOCK_RESPONSE)

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
                max_tokens=3000,
                temperature=0.3,
            )

            content = response.choices[0].message.content.strip()

            try:
                data = json.loads(content)
                return self._parse_response(data)
            except json.JSONDecodeError as e:
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
        furigana_tokens = [
            FuriganaToken(text=t["text"], reading=t.get("reading", ""))
            for t in data.get("furigana_tokens", [])
        ]
        vocabulary = [
            VocabItem(
                word=v["word"],
                reading=v.get("reading", ""),
                meaning=v["meaning"],
                part_of_speech=v.get("part_of_speech", ""),
            )
            for v in data.get("vocabulary", [])
        ]
        grammar_analysis = [
            GrammarPoint(
                word=g["word"],
                reading=g.get("reading", ""),
                part_of_speech=g.get("part_of_speech", ""),
                explanation=g["explanation"],
            )
            for g in data.get("grammar_analysis", [])
        ]
        example_sentences = [
            ExampleSentence(
                japanese=e["japanese"],
                furigana=e.get("furigana", ""),
                chinese=e["chinese"],
            )
            for e in data.get("example_sentences", [])
        ]
        return AnalyzeData(
            original_text=data.get("original_text", ""),
            translation=data.get("translation", ""),
            furigana_tokens=furigana_tokens,
            vocabulary=vocabulary,
            grammar_analysis=grammar_analysis,
            example_sentences=example_sentences,
        )
