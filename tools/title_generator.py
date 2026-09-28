from google import genai
from tools.config import GEMINI_MODEL


def generate_titles(
    client: genai.Client,
    content_type: str,
    topic: str,
    target_audience: str,
    num_titles: int,
    style: str,
) -> str:
    type_map = {
        "ブログ記事タイトル": "ブログ記事",
        "メールの件名": "メールの件名",
        "SNS投稿タイトル": "SNS投稿",
        "商品・サービスのキャッチコピー": "キャッチコピー",
        "プレゼンタイトル": "プレゼンテーション",
        "YouTube動画タイトル": "YouTube動画",
    }

    style_map = {
        "クリック率重視（curiosity gap）": "読者の好奇心を刺激し、思わずクリックしたくなるような",
        "SEO重視（検索流入狙い）": "検索エンジンで上位表示されやすいキーワードを含む",
        "感情訴求（共感・驚き）": "感情に訴えかけ、共感や驚きを引き出す",
        "数字・具体性重視": "具体的な数字や実績を含む",
        "シンプル・直接的": "シンプルで直接的な",
    }

    prompt = f"""以下の条件で{type_map.get(content_type, content_type)}を{num_titles}案作成してください。

テーマ・内容: {topic}
ターゲット: {target_audience}
スタイル: {style_map.get(style, style)}タイトル

各案を番号付きリストで出力してください。タイトルのみ（説明不要）を出力してください。"""

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text
