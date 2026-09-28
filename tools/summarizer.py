from google import genai
from tools.config import GEMINI_MODEL


def summarize_text(
    client: genai.Client,
    text: str,
    summary_length: str,
    output_format: str,
    focus_points: str,
) -> str:
    length_map = {
        "短め（3〜5文）": "3〜5文程度",
        "普通（100〜200文字）": "100〜200文字程度",
        "詳しめ（300〜500文字）": "300〜500文字程度",
    }
    focus_text = f"特に以下の観点に注目して要約してください: {focus_points}" if focus_points else ""

    format_instructions = {
        "文章": "自然な文章形式で要約してください。",
        "箇条書き": "箇条書き（・）で要点を整理してください。",
        "見出し付き": "見出しと本文を使って構造的に整理してください。",
    }

    prompt = f"""以下の文章を要約してください。

【対象テキスト】
{text}

【要約の長さ】
{length_map.get(summary_length, summary_length)}

【出力形式】
{format_instructions.get(output_format, output_format)}

{focus_text}

要約のみを出力してください。"""

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text
