from google import genai
from tools.config import GEMINI_MODEL


def generate_sns_post(
    client: genai.Client,
    platform: str,
    topic: str,
    tone: str,
    include_hashtags: bool,
    include_emoji: bool,
    num_variations: int,
) -> str:
    platform_rules = {
        "Twitter / X": "140文字以内（日本語）。簡潔でインパクトのある文章。",
        "Instagram": "魅力的なキャプション。改行を活用した読みやすい構成。",
        "LinkedIn": "プロフェッショナルな文体。ビジネス的な価値を訴求。",
        "Facebook": "親しみやすい文体。詳しめの説明も可。",
        "Threads": "Twitter / X に近いが少し長めでもOK（500文字程度まで）。",
    }

    hashtag_instruction = "関連するハッシュタグを3〜5個含めてください。" if include_hashtags else "ハッシュタグは不要です。"
    emoji_instruction = "適切な絵文字を使って表現を豊かにしてください。" if include_emoji else "絵文字は使わないでください。"

    prompt = f"""以下の条件でSNS投稿文を{num_variations}パターン作成してください。

プラットフォーム: {platform}
ルール: {platform_rules.get(platform, "")}
投稿テーマ: {topic}
トーン・文体: {tone}
{hashtag_instruction}
{emoji_instruction}

各パターンを「--- パターン1 ---」のように区切って出力してください。"""

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text
