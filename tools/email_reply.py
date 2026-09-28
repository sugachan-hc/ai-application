from google import genai
from tools.config import GEMINI_MODEL


def generate_email_reply(
    client: genai.Client,
    original_email: str,
    reply_intent: str,
    tone: str,
    sender_name: str,
) -> str:
    prompt = f"""以下のメールに対する返信文を作成してください。

【受信したメール】
{original_email}

【返信の意図・内容】
{reply_intent}

【文体】
{tone}

【送信者名】
{sender_name if sender_name else "（未入力）"}

要件:
- 適切な挨拶文で始める
- 相手のメールの要点を踏まえた返信
- 自然で読みやすい日本語
- 署名欄は「{sender_name}」で締める（名前が未入力の場合は省略）

返信文のみを出力してください。"""

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text
