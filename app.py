import streamlit as st
import pandas as pd

# ページ基本設定（スマホ画面最適化）
st.set_page_config(
    page_title="スロット即判別ナビ Pro",
    page_icon="🎰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 有料アプリ感のあるスタイリッシュなダークテーマCSS
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .stApp { max-width: 500px; margin: 0 auto; }
    
    /* ブランドヘッダー */
    .brand-header {
        text-align: center;
        padding: 12px 0 6px 0;
        background: linear-gradient(130deg, #1e293b, #0f172a);
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }
    .brand-title { color: #f8fafc; font-size: 1.5rem; font-weight: 900; letter-spacing: 1px; }
    .brand-badge { background: #ef4444; color: white; font-size: 0.65rem; padding: 2px 8px; border-radius: 10px; vertical-align: middle; }
    
    /* シグナル判定カード */
    .status-go { background: linear-gradient(135deg, #059669, #10b981); color: white; padding: 14px; border-radius: 12px; text-align: center; font-weight: bold; margin-bottom: 12px; }
    .status-warning { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; padding: 14px; border-radius: 12px; text-align: center; font-weight: bold; margin-bottom: 12px; }
    .status-stay { background: linear-gradient(135deg, #334155, #475569); color: white; padding: 14px; border-radius: 12px; text-align: center; font-weight: bold; margin-bottom: 12px; }

    /* 数値ハイライトカード */
    .stat-box {
        background: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .stat-label { color: #94a3b8; font-size: 0.75rem; font-weight: bold; }
    .stat-val { color: #f8fafc; font-size: 1.1rem; font-weight: bold; margin-top: 2px; }
    
    /* タブの視認性改善 */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { background-color: #1e293b; border-radius: 8px 8px 0 0; color: #94a3b8; padding: 8px 12px; }
    .stTabs [aria-selected="true"] { background-color: #ef4444 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1uz8zjUxJUEIqw92yal84WL-ShOAMK_oNnKri6vnVq4MoYh-WB6Jd2gck6rawYpB6P-CXmyqqzJUP/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)
    df = df.fillna("非該当・解析中")
    return df

try:
    df = load_data()
    
    # 1. ブランドヘッダー
    st.markdown("""
    <div class="brand-header">
        <div class="brand-title">🎰 即判別ナビ <span class="brand-badge">PRO</span></div>
        <div style="color: #64748b; font-size: 0.75rem;">ホール実戦専用 リアルタイム立ち回りエンジン</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. 機種クイック検索
    machine_list = df["機種名"].tolist()
    selected_machine = st.selectbox("🔍 機種を選択（タップして検索）", machine_list)
    
    row = df[df["機種名"] == selected_machine].iloc[0]
    
    # 機種画像
    img_url = row.get("画像URL", None)
    if img_url and str(img_url).startswith("http"):
        st.image(img_url, use_column_width=True)

    # 3. インタラクティブ判別カウンター（立ち回り判定）
    st.markdown("##### ⚡ リアルタイムボーダー判別")
    c1, c2 = st.columns(2)
    with c1:
        current_g = st.number_input("現在ゲーム数", min_value=0, max_value=2000, value=0, step=10)
    with c2:
        current_diff = st.number_input("現在差枚数", min_value=-5000, max_value=5000, value=0, step=100)

    # 判定アルゴリズム（自動計算）
    try:
        target_g = int(str(row["通常天井G"]).replace("G", "").replace("G+α", "").strip())
        remain_g = target_g - current_g
        
        if current_g == 0:
            st.markdown('<div class="status-stay">⚪ ゲーム数を入力してください</div>', unsafe_allow_html=True)
        elif remain_g <= 150:
            st.markdown(f'<div class="status-go">🚀 打てる！ (天井まで残り {remain_g} G)</div>', unsafe_allow_html=True)
        elif remain_g <= 300:
            st.markdown(f'<div class="status-warning">⚠️ ボーダー付近 (天井まで残り {remain_g} G)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-stay">🛑 見送り推奨 (天井まで残り {remain_g} G)</div>', unsafe_allow_html=True)
    except:
        st.info("📌 詳細ボーダーは下記の狙い目タブをご確認ください")

    # 4. ひと目でわかる要点スタッツ（2×2レイアウト）
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f'''
        <div class="stat-box">
            <div class="stat-label">朝一リセット天井</div>
            <div class="stat-val">{row["朝一リセット天井G"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    with m2:
        st.markdown(f'''
        <div class="stat-box" style="border-left-color: #ef4444;">
            <div class="stat-label">通常最大天井</div>
            <div class="stat-val">{row["通常天井G"]}</div>
        </div>
        ''', unsafe_allow_html=True)

    # 5. タブ別・カード型情報整理
    t1, t2, t3, t4 = st.tabs(["🎯 狙い目", "🛑 やめ時", "🔍 演出示唆", "📊 判別・打ち方"])
    
    with t1:
        st.markdown("#### 🎯 狙い目＆ボーダー")
        st.error(f"**【天井恩恵】**\n\n{row['天井恩恵・期待枚数']}")
        st.warning(f"**【スルー数・ゾーン狙い】**\n\n{row['スルー数別狙い目']}\n\n{row['ゾーン・スポット狙いG']}")
        st.info(f"💡 **現金投資ボーダー:** {row['現金投資・非等価ボーダー']}")
        
    with t2:
        st.markdown("#### 🛑 やめ時＆有利区間（ツラヌキ）")
        st.error(f"**【即やめ厳禁・やめ時詳細】**\n\n{row['やめ時詳細']}")
        st.success(f"🔄 **【有利区間・ツラヌキ条件】**\n\n{row['有利区間・ツラヌキ条件']}\n\n**切断時恩恵:** {row['有利区間切断時の恩恵']}")
        
    with t3:
        st.markdown("#### 🔍 演出・サブ液晶・示唆")
        st.markdown(f"**👀 アイキャッチ・演出**\n\n{row['アイキャッチ・演出示唆']}")
        st.markdown(f"**🗣️ ボイス・液晶表示**\n\n{row['ボイス・液晶示唆']}")
        st.markdown(f"**🏆 終了画面・トロフィー**\n\n{row['終了画面・トロフィー']}")
        
    with t4:
        st.markdown("#### 📊 設定判別＆注意事項")
        st.markdown(f"**📈 設定判別ポイント**\n\n{row['設定判別ポイント']}")
        st.markdown(f"**⚠️ 立ち回り注意メモ**\n\n{row['立ち回り要注意メモ']}")
        st.markdown(f"**🎰 推奨打ち方**\n\n{row['通常時の打ち方（推奨押し順）']}")

except Exception as e:
    st.error(f"データ読み込みエラー: {e}")
