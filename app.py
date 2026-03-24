import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai

# --- 1. アプリの基本設定 ---
st.set_page_config(page_title="成瀬投資分析システム", layout="wide", initial_sidebar_state="expanded")

# カスタムCSSで見た目を少しリッチに
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. APIキーの設定 (Secretsから読み込み) ---
try:
    GENAI_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.sidebar.error("⚠️ Gemini APIキーがSecretsに設定されていません。")

# --- 3. サイドバー：銘柄の選択 ---
st.sidebar.header("🔍 銘柄選択")

# お気に入り銘柄（成瀬さんの好みに合わせて書き換え可能）
favorites = {
    "三菱商事": "8058.T",
    "三井住友FG": "8316.T",
    "日本郵船": "9101.T",
    "ソフトバンク": "9434.T",
    "三菱HCキャピタル": "8593.T",
    "トヨタ自動車": "7203.T"
}

selection = st.sidebar.selectbox("お気に入りから選ぶ", ["直接入力"] + list(favorites.keys()))

if selection == "直接入力":
    ticker_symbol = st.sidebar.text_input("銘柄コードを入力 (例: 7203.T)", "8058.T")
else:
    ticker_symbol = favorites[selection]

# --- 4. メインコンテンツ ---
if ticker_symbol:
    try:
        with st.spinner("最新データを取得中..."):
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            name = info.get('shortName', ticker_symbol)
            
        st.title(f"📈 {name} ({ticker_symbol})")

        # ★ タブ機能の構築
        tab1, tab2, tab3 = st.tabs(["📊 基本指標", "📈 チャート", "🤖 AI詳細診断"])

        # --- タブ1: 基本指標 ---
        with tab1:
            st.subheader("現在の主要データ")
            col1, col2, col3 = st.columns(3)
            
            # 指標の表示
            price = info.get('currentPrice', 'N/A')
            per = info.get('trailingPE', 'N/A')
            div_yield = info.get('dividendYield', 0) * 100
            
            col1.metric("株価", f"¥{price}")
            col2.metric("PER (株価収益率)", f"{per}倍")
            col3.metric("配当利回り", f"{div_yield:.2f}%")

            with st.expander("詳細な財務情報を表示"):
                c1, c2 = st.columns(2)
                c1.write(f"**PBR (株価純資産倍率):** {info.get('priceToBook', 'N/A')}倍")
                c1.write(f"**時価総額:** {info.get('marketCap', 0):,}円")
                c2.write(f"**52週高値:** ¥{info.get('fiftyTwoWeekHigh', 'N/A')}")
                c2.write(f"**52週安値:** ¥{info.get('fiftyTwoWeekLow', 'N/A')}")

        # --- タブ2: チャート ---
        with tab2:
            st.subheader("株価推移 (直近1年間)")
            hist = stock.history(period="1y")
            
            if not hist.empty:
                fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='終値', line=dict(color='#1f77b4', width=2))])
                fig.update_layout(
                    hovermode='x unified',
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=500,
                    xaxis=dict(title="日付"),
                    yaxis=dict(title="株価 (円)")
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("チャートデータを取得できませんでした。")

        # --- タブ3: AI詳細診断 ---
        with tab3:
            st.subheader("Gemini AI による投資判断")
            st.write("最新の指標と市場動向に基づき、AIが分析レポートを作成します。")
            
            if st.button("AIレポートを生成する"):
                with st.spinner("AIが思考中..."):
                    # 分析用プロンプト
                    prompt = f"""
                    あなたは経験豊富な証券アナリストです。
                    銘柄: {name} ({ticker_symbol})
                    PER: {per}倍、配当利回り: {div_yield:.2f}%、PBR: {info.get('priceToBook')}倍
                    
                    上記の指標を踏まえ、以下の構成で簡潔に分析してください：
                    1. 現状の割安性の評価
                    2. 直近のニュースや業界動向から見たリスク
                    3. 投資判断（買い・待ち）とその理由
                    """
                    
                    try:
                        response = model.generate_content(prompt)
                        st.info(response.text)
                    except Exception as e:
                        st.error(f"AI分析中にエラーが発生しました: {e}")

    except Exception as e:
        st.error(f"データの取得に失敗しました。銘柄コードが正しいか確認してください。: {e}")
else:
    st.info("左側のサイドバーから銘柄を選択、またはコードを入力してください。")
