from pydantic import BaseModel, Field
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    """分析请求体"""

    image_base64: str = Field(..., description="Base64编码的图片数据")
    context: str = Field(default="", description="上下文信息（预留）")


class GrammarPoint(BaseModel):
    """语法点分析"""

    word: str = Field(..., description="单词或语法点")
    explanation: str = Field(..., description="词性与用法解释")


class ExampleSentence(BaseModel):
    """例句"""

    japanese: str = Field(..., description="日文例句")
    chinese: str = Field(..., description="中文翻译")


class AnalyzeData(BaseModel):
    """分析结果数据"""

    original_text: str = Field(..., description="提取出的日文原文")
    translation: str = Field(..., description="对应的中文翻译")
    furigana: str = Field(..., description="原文的平假名注音")
    grammar_analysis: List[GrammarPoint] = Field(..., description="语法分析列表")
    example_sentence: ExampleSentence = Field(..., description="例句")


class AnalyzeResponse(BaseModel):
    """分析响应体"""

    status: str = Field(..., description="状态: success/error")
    data: Optional[AnalyzeData] = Field(default=None, description="分析结果数据")
    error: Optional[str] = Field(default=None, description="错误信息")
