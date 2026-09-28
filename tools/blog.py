from google import genai
from tools.config import GEMINI_MODEL


def generate_blog_post(
    client: genai.Client,
    topic: str,
    tone: str,
    target_audience: str,
    word_count: int,
    keywords: str,
) -> str:
    keywords_text = f"キーワード: {keywords}" if keywords else ""
    prompt = f"""以下の条件でブログ記事を執筆してください。

テーマ: {topic}
文体・トーン: {tone}
ターゲット読者: {target_audience}
目標文字数: 約{word_count}文字
{keywords_text}

記事の構成:
- 魅力的なタイトル
- 導入文（読者の興味を引く）
- 本文（見出しを使って整理）
- まとめ

マークダウン形式で出力してください。"""

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text
