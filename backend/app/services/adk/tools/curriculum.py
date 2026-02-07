"""カリキュラム参照ツール

学年・教科に応じたカリキュラム情報を提供する。
Phase 2aではインメモリの静的データで実装。将来的にFirestoreに移行。
"""

from google.adk.tools import FunctionTool  # type: ignore[attr-defined]

# カリキュラムデータ: (grade, subject, topic) → 情報
# Phase 2a: 静的辞書。Phase 2c以降でFirestoreに移行予定
_CURRICULUM_DATA: dict[tuple[int, str, str], dict[str, list[str]]] = {
    # ===== 算数 1年生 =====
    (1, "math", "addition"): {
        "prerequisites": ["10までの数の理解", "数の順序"],
        "learning_objectives": [
            "1桁の足し算ができる",
            "繰り上がりのある足し算ができる",
            "合わせていくつの意味がわかる",
        ],
        "common_mistakes": [
            "繰り上がりを忘れる",
            "指を使って数え間違える",
            "数字の読み間違い",
        ],
        "teaching_strategies": [
            "ブロックや指を使って具体的に数える",
            "10のまとまりを意識させる",
            "身近な場面（おかしを合わせる等）で説明する",
        ],
        "related_topics": ["subtraction", "number_sense"],
    },
    (1, "math", "subtraction"): {
        "prerequisites": ["足し算の理解", "10までの数の理解"],
        "learning_objectives": [
            "1桁の引き算ができる",
            "繰り下がりのある引き算ができる",
            "残りはいくつの意味がわかる",
        ],
        "common_mistakes": [
            "繰り下がりを忘れる",
            "大きい数から小さい数を引けない",
            "足し算と混同する",
        ],
        "teaching_strategies": [
            "ブロックを実際に取り除いて見せる",
            "足し算との関係を教える",
            "「あと何個？」の場面で練習する",
        ],
        "related_topics": ["addition", "number_sense"],
    },
    # ===== 算数 2年生 =====
    (2, "math", "multiplication"): {
        "prerequisites": ["足し算の理解", "同じ数のまとまり"],
        "learning_objectives": [
            "九九を覚える",
            "かけ算の意味がわかる（○個ずつ△組）",
            "九九を使って問題が解ける",
        ],
        "common_mistakes": [
            "九九の覚え間違い（特に7の段、8の段）",
            "かけ算の順序を間違える",
            "足し算と混同する",
        ],
        "teaching_strategies": [
            "同じ数のまとまりを図で見せる",
            "九九カードで繰り返し練習",
            "日常の場面（お菓子の袋等）と結びつける",
        ],
        "related_topics": ["addition", "division"],
    },
    (2, "math", "addition"): {
        "prerequisites": ["1年生の足し算", "位の概念"],
        "learning_objectives": [
            "2桁＋2桁の筆算ができる",
            "繰り上がりが複数回ある計算ができる",
        ],
        "common_mistakes": [
            "位をそろえずに計算する",
            "繰り上がりの処理を忘れる",
        ],
        "teaching_strategies": [
            "筆算の手順を丁寧に教える",
            "位取り表を使う",
        ],
        "related_topics": ["subtraction", "number_sense"],
    },
    # ===== 算数 3年生 =====
    (3, "math", "division"): {
        "prerequisites": ["九九の理解", "かけ算の意味"],
        "learning_objectives": [
            "割り算の意味がわかる（等分除・包含除）",
            "九九を使った割り算ができる",
            "あまりのある割り算ができる",
        ],
        "common_mistakes": [
            "かけ算と割り算の関係がわからない",
            "あまりの処理を間違える",
            "割る数と割られる数を逆にする",
        ],
        "teaching_strategies": [
            "実際にものを分ける活動をする",
            "かけ算との関係を図で示す",
            "「○個を△人で分けると？」の場面で練習する",
        ],
        "related_topics": ["multiplication", "fractions"],
    },
    # ===== 国語 1年生 =====
    (1, "japanese", "hiragana"): {
        "prerequisites": ["文字への興味", "なぞり書きの経験"],
        "learning_objectives": [
            "ひらがな46文字を読める",
            "ひらがな46文字を書ける",
            "濁音・半濁音がわかる",
        ],
        "common_mistakes": [
            "鏡文字になる（特に「さ」「き」「な」）",
            "似た文字を混同する（「は」と「ほ」等）",
            "書き順を間違える",
        ],
        "teaching_strategies": [
            "なぞり書きから始める",
            "大きく書く練習をする",
            "言葉と結びつけて覚える（「あ」→あめ）",
        ],
        "related_topics": ["katakana", "reading"],
    },
    # ===== 国語 2年生 =====
    (2, "japanese", "kanji"): {
        "prerequisites": ["ひらがな・カタカナの読み書き"],
        "learning_objectives": [
            "2年生の漢字160字を読める",
            "2年生の漢字160字を書ける",
            "漢字の部首がわかる",
        ],
        "common_mistakes": [
            "似た漢字を混同する",
            "書き順を間違える",
            "読み方を間違える（音読み・訓読み）",
        ],
        "teaching_strategies": [
            "部首に注目させる",
            "漢字の成り立ちを教える",
            "文章の中で使う練習をする",
        ],
        "related_topics": ["reading", "writing"],
    },
}

# 一般的なフォールバックデータ
_GENERAL_FALLBACK: dict[str, list[str]] = {
    "prerequisites": ["基本的な学習習慣"],
    "learning_objectives": ["該当トピックの基礎理解"],
    "common_mistakes": ["問題の読み間違い", "ケアレスミス"],
    "teaching_strategies": [
        "問題をよく読むことを促す",
        "前に学んだことと結びつける",
        "具体的な例で説明する",
    ],
    "related_topics": [],
}


def check_curriculum(
    grade_level: int,
    subject: str,
    topic: str,
) -> dict[str, list[str]]:
    """学年・教科に応じたカリキュラム情報を返す

    Args:
        grade_level: 学年（1-3）
        subject: 教科（"math", "japanese"）
        topic: トピック（"addition", "kanji" 等）
    """
    key = (grade_level, subject, topic)
    data = _CURRICULUM_DATA.get(key)

    if data is not None:
        return data

    return dict(_GENERAL_FALLBACK)


check_curriculum_tool = FunctionTool(func=check_curriculum)
