import os
import streamlit as st
from google import genai
from dotenv import load_dotenv

from tools.blog import generate_blog_post
from tools.email_reply import generate_email_reply
from tools.summarizer import summarize_text
from tools.rewriter import rewrite_text
from tools.sns_post import generate_sns_post
from tools.title_generator import generate_titles

load_dotenv()

st.set_page_config(
    page_title="AI ライティングツール",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .tool-header { font-size: 1.6rem; font-weight: 700; margin-bottom: 0.2rem; }
    .tool-desc { color: #888; font-size: 0.9rem; margin-bottom: 1.5rem; }
    .result-box {
        background: #f8f9fa;
        border-left: 4px solid #4CAF50;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
    }
    .stTextArea textarea { font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)


def _load_api_key() -> str:
    if key := st.session_state.get("api_key", ""):
        return key
    try:
        if key := st.secrets.get("GEMINI_API_KEY", ""):
            return key
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", "")


def get_client() -> genai.Client | None:
    api_key = _load_api_key()
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


# ── サイドバー ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("✍️ AI ライティングツール")
    st.markdown("---")

    tool = st.radio(
        "ツールを選択",
        [
            "📝 ブログ記事生成",
            "📧 メール返信文生成",
            "📋 文章要約",
            "🔄 文章リライト・校正",
            "📱 SNS 投稿文生成",
            "💡 タイトル・キャッチコピー生成",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### ⚙️ API 設定")
    api_key_input = st.text_input(
        "Gemini API キー",
        type="password",
        placeholder="AIza...",
        help="Google AI Studio で取得した API キーを入力してください",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input

    _secrets_key = ""
    try:
        _secrets_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass
    _env_key = os.getenv("GEMINI_API_KEY", "")

    if _secrets_key:
        st.success("✅ Secrets から API キー読み込み済み")
    elif _env_key:
        st.success("✅ .env から API キー読み込み済み")
    elif st.session_state.get("api_key"):
        st.success("✅ API キー設定済み")
    else:
        st.warning("API キーを入力してください")
        st.markdown(
            "[Google AI Studio でキーを取得](https://aistudio.google.com/app/apikey)",
            unsafe_allow_html=False,
        )


# ── ヘルパー ─────────────────────────────────────────────────────────────────
def require_client() -> genai.Client | None:
    client = get_client()
    if client is None:
        st.error("Gemini API キーが設定されていません。サイドバーで設定してください。")
    return client


def show_result(text: str, label: str = "生成結果") -> None:
    st.markdown(f"### {label}")
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown(text)
    st.markdown("</div>", unsafe_allow_html=True)
    st.download_button(
        label="📥 テキストをダウンロード",
        data=text,
        file_name="result.txt",
        mime="text/plain",
    )


# ── ブログ記事生成 ────────────────────────────────────────────────────────────
if tool == "📝 ブログ記事生成":
    st.markdown('<div class="tool-header">📝 ブログ記事生成</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-desc">テーマを入力するだけで、構成付きのブログ記事を自動生成します。</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        topic = st.text_input("記事のテーマ *", placeholder="例: 在宅ワークの生産性を上げる5つの習慣")
        keywords = st.text_input("含めたいキーワード（任意）", placeholder="例: 集中力, タイムマネジメント, ツール")
    with col2:
        tone = st.selectbox("文体・トーン", ["フレンドリー", "プロフェッショナル", "カジュアル", "教育的", "エンタメ系"])
        target_audience = st.text_input("ターゲット読者", placeholder="例: 20〜30代の会社員")
        word_count = st.slider("目標文字数", 300, 3000, 1000, step=100)

    if st.button("✨ 記事を生成", type="primary", use_container_width=True):
        if not topic:
            st.warning("テーマを入力してください。")
        else:
            client = require_client()
            if client:
                with st.spinner("記事を生成中..."):
                    result = generate_blog_post(client, topic, tone, target_audience, word_count, keywords)
                show_result(result, "生成されたブログ記事")


# ── メール返信文生成 ──────────────────────────────────────────────────────────
elif tool == "📧 メール返信文生成":
    st.markdown('<div class="tool-header">📧 メール返信文生成</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-desc">受信したメールと返信内容を入力するだけで、自然な返信文を作成します。</div>', unsafe_allow_html=True)

    original_email = st.text_area("受信したメール *", height=180, placeholder="ここに受信メールの本文を貼り付けてください...")
    reply_intent = st.text_area("返信の意図・伝えたいこと *", height=100, placeholder="例: 来週の打ち合わせを承諾し、場所の詳細を確認したい")

    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("文体", ["丁寧（ビジネス）", "フレンドリー", "フォーマル（目上の方向け）", "カジュアル"])
    with col2:
        sender_name = st.text_input("送信者名（署名用）", placeholder="例: 山田 太郎")

    if st.button("✨ 返信文を生成", type="primary", use_container_width=True):
        if not original_email or not reply_intent:
            st.warning("受信メールと返信の意図を入力してください。")
        else:
            client = require_client()
            if client:
                with st.spinner("返信文を生成中..."):
                    result = generate_email_reply(client, original_email, reply_intent, tone, sender_name)
                show_result(result, "生成された返信文")


# ── 文章要約 ─────────────────────────────────────────────────────────────────
elif tool == "📋 文章要約":
    st.markdown('<div class="tool-header">📋 文章要約</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-desc">長い文章を素早く要約します。ニュース・議事録・レポートなどに。</div>', unsafe_allow_html=True)

    text = st.text_area("要約したい文章 *", height=250, placeholder="ここに要約したいテキストを貼り付けてください...")

    col1, col2, col3 = st.columns(3)
    with col1:
        summary_length = st.selectbox("要約の長さ", ["短め（3〜5文）", "普通（100〜200文字）", "詳しめ（300〜500文字）"])
    with col2:
        output_format = st.selectbox("出力形式", ["文章", "箇条書き", "見出し付き"])
    with col3:
        focus_points = st.text_input("注目ポイント（任意）", placeholder="例: コスト面, 課題, 結論")

    if st.button("✨ 要約する", type="primary", use_container_width=True):
        if not text:
            st.warning("要約したい文章を入力してください。")
        else:
            client = require_client()
            if client:
                with st.spinner("要約中..."):
                    result = summarize_text(client, text, summary_length, output_format, focus_points)
                col_orig, col_summ = st.columns(2)
                with col_orig:
                    st.markdown("**元の文章**")
                    st.info(f"文字数: {len(text)} 文字")
                with col_summ:
                    st.markdown("**要約後**")
                    st.info(f"文字数: {len(result)} 文字（{round(len(result)/len(text)*100)}%）")
                show_result(result, "要約結果")


# ── 文章リライト・校正 ────────────────────────────────────────────────────────
elif tool == "🔄 文章リライト・校正":
    st.markdown('<div class="tool-header">🔄 文章リライト・校正</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-desc">文章の校正・文体変換・簡潔化など、さまざまな書き直しに対応します。</div>', unsafe_allow_html=True)

    text = st.text_area("書き直したい文章 *", height=200, placeholder="ここに文章を貼り付けてください...")

    col1, col2 = st.columns(2)
    with col1:
        rewrite_type = st.selectbox(
            "変換タイプ",
            [
                "校正（誤字・脱字チェック）",
                "リライト（文体変換）",
                "簡潔化（冗長な表現を削除）",
                "フォーマル化（丁寧な表現に変換）",
                "カジュアル化（親しみやすい表現に変換）",
            ],
        )
    with col2:
        target_tone = st.text_input(
            "変換後の文体（「リライト」選択時）",
            placeholder="例: 学術論文風、ライトノベル風、ニュース記事風",
        )

    instructions = st.text_input("追加指示（任意）", placeholder="例: 敬語は使わない、できるだけ短く")

    if st.button("✨ 書き直す", type="primary", use_container_width=True):
        if not text:
            st.warning("書き直したい文章を入力してください。")
        else:
            client = require_client()
            if client:
                with st.spinner("書き直し中..."):
                    result = rewrite_text(client, text, rewrite_type, target_tone, instructions)
                col_orig, col_new = st.columns(2)
                with col_orig:
                    st.markdown("**元の文章**")
                    st.text_area("", value=text, height=200, disabled=True, label_visibility="collapsed")
                with col_new:
                    st.markdown("**書き直し後**")
                    st.text_area("", value=result, height=200, label_visibility="collapsed")
                st.download_button("📥 ダウンロード", data=result, file_name="rewritten.txt", mime="text/plain")


# ── SNS 投稿文生成 ────────────────────────────────────────────────────────────
elif tool == "📱 SNS 投稿文生成":
    st.markdown('<div class="tool-header">📱 SNS 投稿文生成</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-desc">各プラットフォームのルールに合わせた投稿文を複数パターン生成します。</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        topic = st.text_input("投稿テーマ・内容 *", placeholder="例: 新商品のコーヒーの美味しさを伝えたい")
    with col2:
        platform = st.selectbox("プラットフォーム", ["Twitter / X", "Instagram", "LinkedIn", "Facebook", "Threads"])

    col3, col4, col5 = st.columns(3)
    with col3:
        tone = st.selectbox("トーン", ["フレンドリー", "プロフェッショナル", "エンタメ系", "感情訴求", "情報提供"])
    with col4:
        num_variations = st.slider("生成パターン数", 1, 5, 3)
    with col5:
        include_hashtags = st.checkbox("ハッシュタグを含める", value=True)
        include_emoji = st.checkbox("絵文字を使う", value=True)

    if st.button("✨ 投稿文を生成", type="primary", use_container_width=True):
        if not topic:
            st.warning("投稿テーマを入力してください。")
        else:
            client = require_client()
            if client:
                with st.spinner("投稿文を生成中..."):
                    result = generate_sns_post(client, platform, topic, tone, include_hashtags, include_emoji, num_variations)
                show_result(result, f"{platform} 投稿文案")


# ── タイトル・キャッチコピー生成 ──────────────────────────────────────────────
elif tool == "💡 タイトル・キャッチコピー生成":
    st.markdown('<div class="tool-header">💡 タイトル・キャッチコピー生成</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-desc">ブログ・メール・SNS・商品など、あらゆるコンテンツのタイトルを生成します。</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        content_type = st.selectbox(
            "コンテンツの種類",
            [
                "ブログ記事タイトル",
                "メールの件名",
                "SNS投稿タイトル",
                "商品・サービスのキャッチコピー",
                "プレゼンタイトル",
                "YouTube動画タイトル",
            ],
        )
        topic = st.text_input("テーマ・内容 *", placeholder="例: 毎日5分で英語が話せるようになるアプリ")
    with col2:
        style = st.selectbox(
            "スタイル",
            [
                "クリック率重視（curiosity gap）",
                "SEO重視（検索流入狙い）",
                "感情訴求（共感・驚き）",
                "数字・具体性重視",
                "シンプル・直接的",
            ],
        )
        target_audience = st.text_input("ターゲット読者・顧客", placeholder="例: 英語学習に挫折した社会人")
        num_titles = st.slider("生成案数", 3, 15, 8)

    if st.button("✨ タイトルを生成", type="primary", use_container_width=True):
        if not topic:
            st.warning("テーマ・内容を入力してください。")
        else:
            client = require_client()
            if client:
                with st.spinner("タイトルを生成中..."):
                    result = generate_titles(client, content_type, topic, target_audience, num_titles, style)
                show_result(result, "生成されたタイトル案")
