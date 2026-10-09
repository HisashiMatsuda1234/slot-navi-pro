import streamlit as st
import pandas as pd

# スマホ（iPhone/Android）表示に最適化
st.set_page_config(
    page_title="スロット即判別ナビ Pro",
    page_icon="🎰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# パチ屋の暗闇でも見やすいダーク系 ＆ タップしやすいデカボタンUI
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        font-size: 1.15rem !important;
        font-weight: bold;
        border-radius: 12px;
        background-color: #1F2937;
        color: #FFFFFF;
        border: 1px solid #374151;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        font-weight: bold;
        font-size: 0.95rem;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 発行されたスプレッドシートのCSV URL ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1uz8zjUxJUEIqw92yal84WL-ShOAMK_oNnKri6vnVq4MoYh-WB6Jd2gck6rawYpB6P-CXmyqqzJUP/pub?output=csv"

@st.cache_data(ttl=300) # 5分ごとに自動更新
def load_data():
    df = pd.read_csv(SPREADSHEET_URL)
    # 全列文字列型として読み込み（数値変換の不具合防止）
    df = df.astype(str)
    return df

try:
    df_machines = load_data()
except Exception as e:
    st.error("スプレッドシートの読み込みに失敗しました。URLをご確認ください。")
    st.stop()

# アプリヘッダー
st.title("🎰 即判別ナビ Pro")

# 1. 機種選択
machine_list = df_machines["機種名"].tolist()
selected_machine = st.selectbox("🎯 打ちたい機種を選択", machine_list)

# 選択データの取得
row = df_machines[df_machines["機種名"] == selected_machine].iloc[0]

# 信頼度・更新日時の表示
st.caption(f"🛡️ 信頼度: {row['情報の信頼度・データソース']} (更新: {row['最終更新日時']})")

st.markdown("---")

# 実戦フェーズ別 4大タブ
tab1, tab2, tab3, tab4 = st.tabs(["🎯 打つ前", "🔍 滞在・打ち方", "🛑 やめ時・ツラヌキ", "📊 設定判別・パチンコ"])

# --- TAB 1: 打つ前判定（狙い目・ボーダー） ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        status = st.radio("設定変更", ["通常/不明", "朝一リセット"])
    with col2:
        exchange = st.radio("換金率", ["等価/持ちメダル", "5.6枚現金"])
        
    g_val = st.slider("現在のゲーム数 (G)", 0, 1500, 250, step=10)
    
    # ボーダー算出ロジック
    try:
        raw_target = row["朝一リセット天井G"] if status == "朝一リセット" else row["通常天井G"]
        base_target = int(''.join(filter(str.isdigit, str(raw_target))))
    except ValueError:
        base_target = 600
        
    if exchange == "5.6枚現金":
        base_target += 50  # 現金投資時は自動でボーダーを50G厳しく計算
        
    if g_val >= base_target:
        st.success(f"🚀 **【 打てる！ 】 狙い目ライン到達**")
        st.markdown(f"**ボーダー目安:** {base_target} G〜 （現在 +{g_val - base_target} G）")
    elif g_val >= (base_target - 50):
        st.warning(f"⚠️ **【 様子見 】 あと少しで狙い目**")
        st.markdown(f"狙い目まであと **{base_target - g_val} G**")
    else:
        st.error(f"✋ **【 打つな 】 期待値マイナスゾーン**")
        st.markdown(f"狙い目まであと **{base_target - g_val} G** 必要")

    st.markdown("---")
    with st.expander("📌 スルー数・ゾーン・天井恩恵の詳細"):
        st.write(f"**スルー数狙い:** {row['スルー数別狙い目']}")
        st.write(f"**ゾーン/スポット狙い:** {row['ゾーン・スポット狙いG']}")
        st.write(f"**天井到達時の恩恵:** {row['天井恩恵・期待枚数']}")
        st.write(f"**現金投資・非等価ボーダー補足:** {row['現金投資・非等価ボーダー']}")
        st.write(f"**朝一のリセット判別:** {row['リセット判別方法']}")

# --- TAB 2: 滞在・打ち方・示唆 ---
with tab2:
    st.subheader("🎯 通常時の打ち方・レア役判別")
    st.info(f"**【基本押し順】**\n\n{row['通常時の打ち方（推奨押し順）']}")
    st.success(f"**【停止形・変則押し】**\n\n{row['レア役停止形・変則押し判別']}")
    
    st.markdown("---")
    st.subheader("👁️ ステージ・アイキャッチ示唆")
    st.write(row["アイキャッチ・演出示唆"])
    
    st.subheader("🗣️ サブ液晶・ボイス示唆")
    st.write(row["ボイス・液晶示唆"])
    
    st.subheader("🌀 モード移行・高確挙動")
    st.write(row["モード移行・滞在示唆"])

# --- TAB 3: やめ時・ツラヌキ・有利区間 ---
with tab3:
    st.subheader("🛑 最適なやめ時（即やめ厳禁チェック）")
    st.warning(row["やめ時詳細"])
    
    st.markdown("---")
    st.subheader("🔥 有利区間切断（ツラヌキ）条件＆恩恵")
    st.write(f"**切断条件:** {row['有利区間・ツラヌキ条件']}")
    st.write(f"**差枚数によるボーダー変化:** {row['差枚別ボーダー変化']}")
    st.write(f"**切断後の恩恵・次回狙い:** {row['有利区間切断時の恩恵']}")

# --- TAB 4: 設定判別・パチンコ ---
with tab4:
    st.subheader("📊 トロフィー・終了画面")
    st.info(row["終了画面・トロフィー"])
    
    st.subheader("🔢 重要設定判別要素")
    st.write(row["設定判別ポイント"])
    
    st.subheader("⚠️ 立ち回り要注意メモ")
    st.error(row["立ち回り要注意メモ"])
    
    st.markdown("---")
    st.subheader("🎰 パチンコ情報（ボーダー・遊タイム）")
    st.write(f"**回転率ボーダー:** {row['パチンコ・回転率ボーダー']}")
    st.write(f"**遊タイム天井・狙い目:** {row['パチンコ・遊タイム天井＆狙い目']}")

# --- 有料会員導線 (Stripe連携) ---
st.markdown("---")
with st.expander("👑 プレミアム会員（月額 500 円 / 7日間無料体験）"):
    st.write("・有利区間ツラヌキ『リアルタイム差枚自動計算機』の解放")
    st.write("・全最新台のデータ更新が導入当日に即時反映")
    st.write("・自分だけのマイホール設定傾向・クセ保存メモ機能")
    if st.button("7日間無料でプレミアム版を試す"):
        st.write("※ Stripe決済ページ（安全な決済システム）へ遷移します")
