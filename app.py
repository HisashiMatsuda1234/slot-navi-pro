import streamlit as st
import pandas as pd

# ページ基本設定（ダークモード風・スマホ最適化）
st.set_page_config(
    page_title="即判別ナビ Pro",
    page_icon="🎰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# カスタムCSSでプロ仕様のカードUI＆装飾を追加
st.markdown("""
<style>
    .main { background-color: #0f172a; }
    .stApp { max-width: 600px; margin: 0 auto; }
    
    /* カード風スタイリング */
    .metric-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .metric-title { color: #94a3b8; font-size: 0.85rem; font-weight: bold; margin-bottom: 4px; }
    .metric-value { color: #38bdf8; font-size: 1.6rem; font-weight: 800; }
    .metric-sub { color: #f59e0b; font-size: 0.8rem; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# 動作確認済み・GoogleスプレッドシートWeb公開CSV URL
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1uz8zjUxJUEIqw92yal84WL-ShOAMK_oNnKri6vnVq4MoYh-WB6Jd2gck6rawYpB6P-CXmyqqzJUP/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)
    df = df.fillna("非該当・解析中")
    return df

try:
    df = load_data()
    
    # ヘッダーエリア
    st.markdown("<h1 style='text-align: center; color: #f8fafc; font-size: 1.8rem;'>🎰 即判別ナビ <span style='color: #ef4444;'>PRO</span></h1>", unsafe_allow_html=True)
    st.caption("⚡ ホール実戦専用・即判別＆期待値ボーダー検索")
    
    # 機種選択ドロップダウン
    machine_list = df["機種名"].tolist()
    selected_machine = st.selectbox("🎯 打つ機種を選択してください", machine_list)
    
    # 選択機種データの抽出
    row = df[df["機種名"] == selected_machine].iloc[0]
    
    # 画像表示（Y列「画像URL」があれば表示）
    img_url = row.get("画像URL", None)
    if img_url and str(img_url).startswith("http"):
        st.image(img_url, use_column_width=True)
    
    st.divider()
    
    # ----------------------------------------------------
    # 🧮 1. 即判別（簡易計算器）エリア
    # ----------------------------------------------------
    st.subheader("⚡ リアルタイム立ち回り判別")
    
    col1, col2 = st.columns(2)
    with col1:
        current_g = st.number_input("現在ゲーム数 (G)", min_value=0, max_value=2000, value=0, step=10)
    with col2:
        current_diff = st.number_input("現在差枚数 (枚)", min_value=-5000, max_value=5000, value=0, step=100)
        
    # 天井G数の数値判定
    try:
        target_g = int(str(row["通常天井G"]).replace("G", "").replace("G+α", "").strip())
        remain_g = target_g - current_g
        
        if remain_g <= 0:
            st.error("🚨 【狙い目到達】天井直前・または即発動ラインです！")
        elif remain_g <= 200:
            st.warning(f"🔥 【打てる！】天井まであと {remain_g} G！推奨ボーダー内です。")
        else:
            st.info(f"⏳ 天井まであと {remain_g} G (通常天井: {row['通常天井G']})")
    except:
        st.write(f"📌 **通常天井:** {row['通常天井G']}")

    st.divider()

    # ----------------------------------------------------
    # 📊 2. 重要指標のカード表示（ビジュアル重視）
    # ----------------------------------------------------
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">朝一リセット天井</div>
            <div class="metric-value">{row['朝一リセット天井G']}</div>
            <div class="metric-sub">朝一狙い目</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_b:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">通常天井</div>
            <div class="metric-value" style="color: #ef4444;">{row['通常天井G']}</div>
            <div class="metric-sub">最大ハマリ</div>
        </div>
        """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # 📑 3. タブ別カテゴリ表示（見やすさUP）
    # ----------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 狙い目・天井", "🔍 演出・示唆", "🛑 やめ時・ツラヌキ", "📊 設定判別"])
    
    with tab1:
        st.markdown("### 🎯 天井・ゾーン狙い目")
        st.success(f"**【天井恩恵】**\n\n{row['天井恩恵・期待枚数']}")
        st.info(f"**【スルー数狙い】**\n\n{row['スルー数別狙い目']}")
        st.warning(f"**【ゾーン・ピンポイント狙い】**\n\n{row['ゾーン・スポット狙いG']}")
        st.write(f"💡 **現金・非等価ボーダー:** {row['現金投資・非等価ボーダー']}")
        
    with tab2:
        st.markdown("### 🔍 画面・ボイス示唆まとめ")
        st.write(f"👀 **アイキャッチ・演出:**\n{row['アイキャッチ・演出示唆']}")
        st.write(f"🗣️ **ボイス・サブ液晶:**\n{row['ボイス・液晶示唆']}")
        st.write(f"🏆 **終了画面・トロフィー:**\n{row['終了画面・トロフィー']}")
        
    with tab3:
        st.markdown("### 🛑 やめ時＆有利区間（ツラヌキ）")
        st.error(f"**【やめ時詳細】**\n\n{row['やめ時詳細']}")
        st.write(f"🔄 **有利区間・ツラヌキ条件:**\n{row['有利区間・ツラヌキ条件']}")
        st.write(f"⚡ **切断時恩恵:**\n{row['有利区間切断時の恩恵']}")
        
    with tab4:
        st.markdown("### 📊 設定判別＆注意事項")
        st.write(f"📈 **設定判別ポイント:**\n{row['設定判別ポイント']}")
        st.write(f"⚠️ **立ち回り注意メモ:**\n{row['立ち回り要注意メモ']}")
        st.write(f"🎰 **推奨打ち方:**\n{row['通常時の打ち方（推奨押し順）']}")

except Exception as e:
    st.error(f"データの読み込み中にエラーが発生しました: {e}")
