from pydantic import BaseModel, Field
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    """分析请求体"""

    image_base64: str = Field(..., description="Base64编码的图片数据")
    context: str = Field(default="", description="上下文信息（预留）")


class FuriganaToken(BaseModel):
    """振假名 token"""

    text: str = Field(..., description="表面形式（汉字或假名）")
    reading: str = Field(..., description="平假名读音，纯假名/标点时为空字符串")


class VocabItem(BaseModel):
    """词汇项"""

    word: str = Field(..., description="单词")
    reading: str = Field(..., description="平假名读音")
    meaning: str = Field(..., description="中文意思")
    part_of_speech: str = Field(..., description="词性，如 名詞/動詞/形容詞/副詞")


class GrammarPoint(BaseModel):
    """语法点分析"""

    word: str = Field(..., description="单词或语法点")
    reading: str = Field(default="", description="平假名读音")
    part_of_speech: str = Field(..., description="词性，如 助詞/助動詞/動詞")
    explanation: str = Field(..., description="词性与用法解释")


class ExampleSentence(BaseModel):
    """例句"""

    japanese: str = Field(..., description="日文例句")
    furigana: str = Field(default="", description="平假名全文")
    chinese: str = Field(..., description="中文翻译")


class AnalyzeData(BaseModel):
    """分析结果数据"""

    original_text: str = Field(..., description="提取出的日文原文")
    translation: str = Field(..., description="对应的中文翻译")
    furigana_tokens: List[FuriganaToken] = Field(..., description="原文振假名 token 列表")
    vocabulary: List[VocabItem] = Field(..., description="词汇列表（仅实词）")
    grammar_analysis: List[GrammarPoint] = Field(..., description="语法分析列表")
    example_sentences: List[ExampleSentence] = Field(..., description="例句列表")


class AnalyzeResponse(BaseModel):
    """分析响应体"""

    status: str = Field(..., description="状态: success/error")
    data: Optional[AnalyzeData] = Field(default=None, description="分析结果数据")
    error: Optional[str] = Field(default=None, description="错误信息")
