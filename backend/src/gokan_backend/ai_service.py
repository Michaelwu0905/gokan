import random
from typing import List, Dict, Tuple

# 10个预设场景
SCENARIOS = [
    {
        "id": 1,
        "name": "便利店购物",
        "name_jp": "コンビニ",
        "description": "在便利店购买商品",
        "character_name": "田中さん",
        "character_profile": "便利店店员，20岁，友善礼貌",
        "opening_line": "いらっしゃいませ。何かお探しですか？",
        "vocab_hints": ["これ", "お願いします", "いくら", "ありがとう"],
        "difficulty": "N5",
    },
    {
        "id": 2,
        "name": "自我介绍",
        "name_jp": "自己紹介",
        "description": "初次见面时的自我介绍",
        "character_name": "佐藤さん",
        "character_profile": "大学同学，性格开朗",
        "opening_line": "初めまして。佐藤です。どうぞよろしく。",
        "vocab_hints": ["名前", "学生", "趣味", "よろしく"],
        "difficulty": "N5",
    },
    {
        "id": 3,
        "name": "餐厅点餐",
        "name_jp": "レストラン",
        "description": "在餐厅点餐用餐",
        "character_name": "山田さん",
        "character_profile": "餐厅服务员，30岁，专业有礼",
        "opening_line": "いらっしゃいませ。何名様ですか？",
        "vocab_hints": ["メニュー", "おすすめ", "おいしい", "注文"],
        "difficulty": "N5",
    },
    {
        "id": 4,
        "name": "问路",
        "name_jp": "道案内",
        "description": "向路人询问方向",
        "character_name": "高橋さん",
        "character_profile": "路人，40岁，热心肠",
        "opening_line": "あのう、すみません。",
        "vocab_hints": ["駅", "近い", "遠い", "行く"],
        "difficulty": "N5",
    },
    {
        "id": 5,
        "name": "酒店入住",
        "name_jp": "ホテル",
        "description": "在酒店办理入住",
        "character_name": "鈴木さん",
        "character_profile": "酒店前台，25岁，专业",
        "opening_line": "いらっしゃいませ。ご予約はされていますか？",
        "vocab_hints": ["予約", "部屋", "鍵", "泊まる"],
        "difficulty": "N4",
    },
    {
        "id": 6,
        "name": "看医生",
        "name_jp": "病院",
        "description": "在医院就诊",
        "character_name": "伊藤先生",
        "character_profile": "医生，50岁，温和",
        "opening_line": "どうされましたか？",
        "vocab_hints": ["具合", "熱", "痛い", "薬"],
        "difficulty": "N4",
    },
    {
        "id": 7,
        "name": "银行办理业务",
        "name_jp": "銀行",
        "description": "在银行办理存取款等业务",
        "character_name": "渡辺さん",
        "character_profile": "银行职员，35岁，严谨",
        "opening_line": "いらっしゃいませ。何のご用件でしょうか？",
        "vocab_hints": ["口座", "振込", "現金", "手続き"],
        "difficulty": "N4",
    },
    {
        "id": 8,
        "name": "预约理发",
        "name_jp": "美容院",
        "description": "在理发店预约服务",
        "character_name": "小林さん",
        "character_profile": "理发师，28岁，时尚",
        "opening_line": "いらっしゃいませ。ご予約ですか？",
        "vocab_hints": ["予約", "カット", "シャンプー", "時間"],
        "difficulty": "N4",
    },
    {
        "id": 9,
        "name": "超市购物",
        "name_jp": "スーパー",
        "description": "在超市购买日用品",
        "character_name": "吉田さん",
        "character_profile": "超市店员，45岁，亲切",
        "opening_line": "いらっしゃいませ。袋はお持ちですか？",
        "vocab_hints": ["袋", "レジ", "安い", "高い"],
        "difficulty": "N5",
    },
    {
        "id": 10,
        "name": "邮局寄件",
        "name_jp": "郵便局",
        "description": "在邮局寄送包裹",
        "character_name": "山本さん",
        "character_profile": "邮局职员，55岁，耐心",
        "opening_line": "いらっしゃいませ。何をお届けしますか？",
        "vocab_hints": ["荷物", "送る", "切手", "航空便"],
        "difficulty": "N4",
    },
]

# 模拟回复模板
RESPONSE_TEMPLATES = {
    1: [  # 便利店
        "{content}、かしこまりました。{follow_up}",
        "はい、{content}。{follow_up}",
        "そうですね。{content}。{follow_up}",
    ],
    2: [  # 自我介绍
        "私も{topic}が好きです！{follow_up}",
        "へえ、{content}。{follow_up}",
        "そうなんですね。{follow_up}",
    ],
    3: [  # 餐厅
        "かしこまりました。{content}。{follow_up}",
        "おすすめは{recommendation}です。{follow_up}",
        "はい、{content}。{follow_up}",
    ],
    4: [  # 问路
        "あ、{location}ですね。{direction}",
        "{location}は{direction}",
        "{content}。{direction}",
    ],
    5: [  # 酒店
        "かしこまりました。{content}。{follow_up}",
        "はい、{content}。{follow_up}",
        "{content}をご用意いたします。{follow_up}",
    ],
    6: [  # 医院
        "{content}、了解しました。{follow_up}",
        "それは{symptom}ですね。{follow_up}",
        "{content}。{follow_up}",
    ],
    7: [  # 银行
        "かしこまりました。{content}。{follow_up}",
        "{content}ですね。{follow_up}",
        "はい、{content}。{follow_up}",
    ],
    8: [  # 理发店
        "かしこまりました。{content}。{follow_up}",
        "{content}ですね。{follow_up}",
        "{style}にしますか？{follow_up}",
    ],
    9: [  # 超市
        "はい、{content}。{follow_up}",
        "{content}ですね。{follow_up}",
        "かしこまりました。{follow_up}",
    ],
    10: [  # 邮局
        "かしこまりました。{content}。{follow_up}",
        "{content}ですね。{follow_up}",
        "はい、{content}。{follow_up}",
    ],
}

FOLLOW_UP_QUESTIONS = {
    1: [
        "他に何かいりますか？",
        "袋にお入れしますか？",
        "ポイントカードはお持ちですか？",
    ],
    2: ["趣味は何ですか？", "どこから来ましたか？", "日本語は難しいですか？"],
    3: [
        "お飲み物は何にされますか？",
        "ご注文は以上ですか？",
        "デザートもいかがですか？",
    ],
    4: ["分かりましたか？", "急いでいますか？", "他に質問はありますか？"],
    5: ["朝食はいかがですか？", "Wi-Fiのパスワードをお伝えしますね。", "何泊ですか？"],
    6: ["いつから具合が悪いですか？", "熱はありますか？", "お薬を出しますね。"],
    7: ["手数料は300円です。", "お通帳はお持ちですか？", "確認させていただきます。"],
    8: [
        "予約をお取りします。",
        "担当は私でよろしいですか？",
        "何時にいらっしゃいますか？",
    ],
    9: [
        "レジ袋はいりますか？",
        "ポイントカードはお持ちですか？",
        "現金でお支払いですか？",
    ],
    10: ["航空便でよろしいですか？", "中身は何ですか？", "保険はご加入ですか？"],
}


class VirtualAIService:
    def __init__(self):
        self.scenarios = SCENARIOS

    def get_scenarios(self):
        return self.scenarios

    def get_scenario(self, scenario_id: int):
        for s in self.scenarios:
            if s["id"] == scenario_id:
                return s
        return None

    def generate_response(
        self, scenario_id: int, user_message: str, conversation_history: List[Dict]
    ) -> Tuple[str, List[Dict]]:
        """生成AI回复和可能的错误标记"""
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return "すみません、もう一度お願いします。", []

        # 分析用户输入的错误
        errors = self._analyze_errors(user_message)

        # 生成回复
        templates = RESPONSE_TEMPLATES.get(scenario_id, RESPONSE_TEMPLATES[1])
        template = random.choice(templates)

        # 简单的模板填充
        follow_ups = FOLLOW_UP_QUESTIONS.get(scenario_id, ["そうですね。"])
        follow_up = random.choice(follow_ups)

        # 根据用户输入生成回复
        response = self._fill_template(template, user_message, follow_up)

        return response, errors

    def _analyze_errors(self, text: str) -> List[Dict]:
        """分析日语错误（简单规则版）"""
        errors = []

        # 检查常见助词错误
        particle_errors = [
            ("は", "が", "主語に「が」を使います"),
            ("に", "で", "場所に「で」を使います"),
            ("を", "に", "対象に「を」を使います"),
        ]

        # 简单的错误检测（演示用）
        if random.random() < 0.3:  # 30% 概率检测到一个错误
            wrong, correct, explanation = random.choice(particle_errors)
            errors.append(
                {
                    "error_type": "particle",
                    "original_text": f"{wrong}の使い方",
                    "correction": f"{correct}を使う",
                    "explanation": explanation,
                }
            )

        return errors

    def _fill_template(self, template: str, user_input: str, follow_up: str) -> str:
        """填充回复模板"""
        content = "はい" if len(user_input) < 5 else user_input[:10]

        response = template.format(
            content=content,
            follow_up=follow_up,
            topic="音楽",
            recommendation="ラーメン",
            location="駅",
            direction="まっすぐ行って、左です。",
            symptom="風邪",
            style="ショート",
        )

        return response

    def generate_summary(self, messages: List[Dict]) -> Dict:
        """生成对话总结"""
        errors = []
        user_messages = [m for m in messages if m.get("role") == "user"]

        for msg in user_messages:
            msg_errors = self._analyze_errors(msg.get("content", ""))
            errors.extend(msg_errors)

        suggestions = [
            "助詞の使い方にもう少し注意してください",
            "動詞の形を復習するとよいでしょう",
            "敬語の練習を続けましょう",
        ]

        return {
            "total_messages": len(messages),
            "errors": errors[:3],  # 最多显示3个错误
            "suggestions": random.sample(suggestions, min(2, len(suggestions))),
        }
