import streamlit as st
import pandas as pd
import google.generativeai as genai

# ページ基本設定
st.set_page_config(
    page_title="スロット即判別ナビ Pro",
    page_icon="🎰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 有料アプリクオリティのCSSデザイン
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .stApp { max-width: 550px; margin: 0 auto; }
    
    .brand-header {
        text-align: center;
        padding: 14px 0 8px 0;
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }
    .brand-title { color: #f8fafc; font-size: 1.6rem; font-weight: 900; }
    .brand-badge { background: #ef4444; color: white; font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; vertical-align: middle; }
    
    .status-go { background: linear-gradient(135deg, #059669, #10b981); color: white; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; }
    .status-warning { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; }
    .status-stay { background: linear-gradient(135deg, #334155, #475569); color: white; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; }

    .stat-box {
        background: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 10px 12px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .stat-label { color: #94a3b8; font-size: 0.75rem; font-weight: bold; }
    .stat-val { color: #f8fafc; font-size: 1.1rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Googleスプレッドシート公開CSV URL
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1uz8zjUxJUEIqw92yal84WL-ShOAMK_oNnKri6vnVq4MoYh-WB6Jd2gck6rawYpB6P-CXmyqqzJUP/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)
    df = df.fillna("解析中・未公表")
    return df

try:
    df = load_data()
    
    # 1. ヘッダー
    st.markdown("""
    <div class="brand-header">
        <div class="brand-title">🎰 即判別ナビ <span class="brand-badge">PRO AI</span></div>
        <div style="color: #94a3b8; font-size: 0.75rem;">ホール実戦専用・AIアシスタント搭載立ち回りエンジン</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. 機種選択
    machine_list = df["機種名"].tolist()
    selected_machine = st.selectbox("🔍 打つ機種を選択してください", machine_list)
    
    row = df[df["機種名"] == selected_machine].iloc[0]
    
    # 画像表示
    img_url = row.get("画像URL", None)
    if img_url and str(img_url).startswith("http"):
        st.image(img_url, use_column_width=True)

    # 3. リアルタイム立ち回り判定
    st.markdown("##### ⚡ リアルタイムボーダー判別")
    c1, c2 = st.columns(2)
    with c1:
        current_g = st.number_input("現在ゲーム数 (G)", min_value=0, max_value=2000, value=0, step=10)
    with c2:
        current_diff = st.number_input("現在差枚数 (枚)", min_value=-5000, max_value=5000, value=0, step=100)

    try:
        target_g = int(str(row["通常天井G"]).replace("G", "").replace("G+α", "").strip())
        remain_g = target_g - current_g
        
        if current_g == 0:
            st.markdown('<div class="status-stay">⚪ ゲーム数を入力すると判定されます</div>', unsafe_allow_html=True)
        elif remain_g <= 150:
            st.markdown(f'<div class="status-go">🚀 即打ち推奨！ (天井まであと {remain_g} G)</div>', unsafe_allow_html=True)
        elif remain_g <= 300:
            st.markdown(f'<div class="status-warning">⚠️ ボーダー付近 (天井まであと {remain_g} G)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-stay">🛑 見送り推奨 (天井まであと {remain_g} G)</div>', unsafe_allow_html=True)
    except:
        st.info("📌 詳細ボーダーは「狙い目」タブをご確認ください")

    # 4. カードタブ切り替え（全5タブ）
    t1, t2, t3, t4, t5 = st.tabs(["🎯 狙い目", "🛑 やめ時", "📊 小役・設定差", "🔍 演出示唆", "🤖 AIナビ"])
    
    with t1:
        st.markdown("#### 🎯 天井・ゾーン狙い目")
        st.error(f"**【天井恩恵】**\n\n{row.get('天井恩恵・期待枚数', '')}")
        st.warning(f"**【スルー数・ゾーン狙い】**\n\n{row.get('スルー数別狙い目', '')}\n\n{row.get('ゾーン・スポット狙いG', '')}")
        st.info(f"💡 **ゾーン別詳細期待値:**\n\n{row.get('ゾーン別期待値・ボーダー', 'データ準備中')}")
        
    with t2:
        st.markdown("#### 🛑 やめ時＆ツラヌキ条件")
        st.error(f"**【やめ時詳細】**\n\n{row.get('やめ時詳細', '')}")
        st.success(f"🔄 **【有利区間・ツラヌキ条件】**\n\n{row.get('有利区間・ツラヌキ条件', '')}")
        st.write(f"⚡ **切断時恩恵・期待値:** {row.get('有利区間切断・ツラヌキ期待値', row.get('有利区間切断時の恩恵', ''))}")

    with t3:
        st.markdown("#### 📊 小役確率・設定判別・モード")
        st.info(f"**【小役確率・設定差一覧】**\n\n{row.get('小役確率・設定差一覧', '解析データ準備中')}")
        st.warning(f"**【モード移行率・滞在特徴】**\n\n{row.get('モード移行率・滞在特徴', '解析データ準備中')}")
        st.write(f"📈 **総合設定判別ポイント:**\n{row.get('設定判別ポイント', '')}")

    with t4:
        st.markdown("#### 🔍 演出示唆＆確定パターン")
        st.markdown(f"**👀 アイキャッチ・示唆:**\n{row.get('アイキャッチ・演出示唆', '')}")
        st.markdown(f"**🗣️ ボイス・液晶表示:**\n{row.get('ボイス・液晶示唆', '')}")
        st.markdown(f"**🏆 終了画面・確定演出:**\n{row.get('終了画面・トロフィー', '')}\n\n{row.get('AT中・確定演出法則', '')}")

    # 5. 🤖 AIチャットナビ機能（Gemini API連動）
    with t5:
        st.markdown("#### 🤖 専属スロットAIナビ")
        st.caption("ホール実戦中の迷いをAIが即解決します。「600Gから打てる？」「この示唆は設定いくつ？」など自由に質問してください。")
        
        # APIキーの設定（Secretsまたは画面入力）
        api_key = st.secrets.get("GEMINI_API_KEY", None)
        if not api_key:
            api_key = st.text_input("🔑 Gemini APIキーを入力してください", type="password")

        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeAIModel('gemini-1.5-flash')

            # チャット履歴保持
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # 過去ログ描画
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # ユーザー入力
            if user_prompt := st.chat_input("例: 現在550G、差枚-1000枚だけど打ってOK？"):
                st.session_state.messages.append({"role": "user", "content": user_prompt})
                with st.chat_message("user"):
                    st.markdown(user_prompt)

                # AI用プロンプト構築（スプレッドシートの全解析データを注入）
                system_instruction = f"""
                あなたはパチスロプロの専属立ち回りAIアドバイザーです。
                現在ユーザーが選択している機種は【{selected_machine}】です。
                以下の公式・解析データベース情報のみに基づき、ホール実戦で即判断できるよう「結論（打つべきか/やめるべきか）」を明確かつ簡潔に回答してください。

                【解析データベース情報】
                - 朝一リセット天井: {row.get('朝一リセット天井G', '')}
                - 通常天井: {row.get('通常天井G', '')}
                - 天井恩恵: {row.get('天井恩恵・期待枚数', '')}
                - 狙い目: {row.get('スルー数別狙い目', '')} / {row.get('ゾーン・スポット狙いG', '')}
                - やめ時: {row.get('やめ時詳細', '')}
                - 有利区間・ツラヌキ: {row.get('有利区間・ツラヌキ条件', '')} / {row.get('有利区間切断・ツラヌキ期待値', '')}
                - 小役・設定差: {row.get('小役確率・設定差一覧', '')}
                - 演出・示唆: {row.get('アイキャッチ・演出示唆', '')} / {row.get('終了画面・トロフィー', '')} / {row.get('AT中・確定演出法則', '')}
                """

                full_prompt = f"{system_instruction}\n\nユーザーの質問: {user_prompt}"

                with st.chat_message("assistant"):
                    with st.spinner("AI解析中..."):
                        try:
                            response = model.generate_content(full_prompt)
                            st.markdown(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"AIエラー: {e}")
        else:
            st.info("💡 AI機能を使用するにはGoogle AI Studio等で取得したGemini APIキーを入力してください。（[無料取得はこちら](https://aistudio.google.com/)）")

except Exception as e:
    st.error(f"データ読み込みエラー: {e}")
