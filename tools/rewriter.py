from google import genai
from tools.config import GEMINI_MODEL


def rewrite_text(
    client: genai.Client,
    text: str,
    rewrite_type: str,
    target_tone: str,
    instructions: str,
) -> str:
    type_prompts = {
        "校正（誤字・脱字チェック）": "誤字・脱字・文法ミスを修正し、より自然な日本語に校正してください。修正箇所がわかるようにしてください。",
        "リライト（文体変換）": f"文章の意味を保ちながら、「{target_tone}」の文体にリライトしてください。",
        "簡潔化（冗長な表現を削除）": "冗長な表現を削除し、より簡潔でわかりやすい文章に書き直してください。",
        "フォーマル化（丁寧な表現に変換）": "文章をよりフォーマルで丁寧なビジネス文書向けの表現に変換してください。",
        "カジュアル化（親しみやすい表現に変換）": "文章をより親しみやすくカジュアルな表現に変換してください。",
    }

    base_instruction = type_prompts.get(rewrite_type, rewrite_type)
    extra = f"\n追加指示: {instructions}" if instructions else ""

    prompt = f"""以下の文章を書き直してください。

【元の文章】
{text}

【変換内容】
{base_instruction}{extra}

書き直した文章のみを出力してください。"""

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text
