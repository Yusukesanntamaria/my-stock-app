import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai

# --- 1. アプリの基本設定とロック ---
st.set_page_config(page_title="成瀬投資分析システム", layout="wide")

# パスワードロック
if "APP_PASSWORD" in st.secrets:
    entered_password = st.sidebar.text_input("🔑 起動パスワード", type="password")
    if entered_password != st.secrets["APP_PASSWORD"]:
        st.warning("左のメニューにパスワードを入力してください。")
        st.stop()

# AIの設定 (最新の 2.0-flash を指定)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("APIキーの設定を確認してください。")

# --- 2. ページ切り替えメニュー ---
st.sidebar.title("メニュー")
menu = st.sidebar.radio("機能を選択", ["🔍 個別銘柄分析", "🏆 掘り出し物探し"])

# --- 3. 【ページA】個別銘柄分析 ---
if menu == "🔍 個別銘柄分析":
    st.sidebar.markdown("---")
    st.sidebar.subheader("銘柄選択")
    favorites = {
        "三菱商事": "8058.T", "三井住友FG": "8316.T", "日本郵船": "9101.T", 
        "ソフトバンク": "9434.T", "三菱HCキャピタル": "8593.T", "トヨタ": "7203.T"
    }
    selection = st.sidebar.selectbox("お気に入り", ["直接入力"] + list(favorites.keys()))
    ticker_symbol = st.sidebar.text_input("コード入力", "8058.T" if selection == "直接入力" else favorites[selection])

    if ticker_symbol:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        name = info.get('shortName', ticker_symbol)
        st.title(f"📈 {name} ({ticker_symbol})")

        tab1, tab2, tab3 = st.tabs(["📊 基本指標", "📈 チャート", "🤖 AI詳細診断"])

        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("株価", f"¥{info.get('currentPrice', 'N/A')}")
            c2.metric("PER", f"{info.get('trailingPE', 'N/A')}倍")
            c3.metric("配当利回り", f"{info.get('dividendYield', 0)*100:.2f}%")
            with st.expander("もっと詳しく"):
                st.write(f"PBR: {info.get('priceToBook', 'N/A')}倍")
                st.write(f"時価総額: {info.get('marketCap', 0):,}円")

        with tab2:
            hist = stock.history(period="1y")
            fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='終値')])
            fig.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            if st.button("AIレポートを生成"):
                with st.spinner("分析中..."):
                    prompt = f"{name}({ticker_symbol})のPER{info.get('trailingPE')}倍、利回り{info.get('dividendYield',0)*100:.1f}%から、今後の見通しを分析して。"
                    res = model.generate_content(prompt)
                    st.info(res.text)

# --- 4. 【ページB】掘り出し物探し ---
elif menu == "🏆 掘り出し物探し":
    st.title("🏆 お宝銘柄スクリーニング")
    st.write("現在、特定の「高配当・割安」候補リストから条件に合う株を抽出します。")

    if st.button("スキャン開始"):
        # 調査対象（成瀬さんが気になるセクターを並べています）
        check_list = ["8058.T", "8316.T", "9101.T", "8593.T", "9434.T", "7203.T", "8001.T", "1928.T", "8053.T"]
        results = []

        with st.spinner("市場データを照合中..."):
            for t in check_list:
                s = yf.Ticker(t)
                info = s.info
                per = info.get('trailingPE', 100)
                div = info.get('dividendYield', 0) * 100
                
                # 条件：PER 15倍以下 且つ 利回り 3.5%以上
                if per < 15 and div > 3.5:
                    results.append({
                        "銘柄": info.get('shortName'),
                        "コード": t,
                        "PER": f"{per:.1f}倍",
                        "利回り": f"{div:.2f}%",
                        "価格": f"¥{info.get('currentPrice')}"
                    })

        if results:
            st.success(f"{len(results)}件見つかりました！")
            st.table(pd.DataFrame(results))
            
            st.subheader("🤖 AIのピックアップ")
            ai_res = model.generate_content(f"以下のリストから、初心者が長期で持つべき銘柄を1つ選んで理由を教えて：{results}")
            st.info(ai_res.text)
        else:
            st.warning("現在は条件に合う銘柄がありません。")

    except Exception as e:
        st.error(f"データの取得に失敗しました。銘柄コードが正しいか確認してください。: {e}")
else:
    st.info("左側のサイドバーから銘柄を選択、またはコードを入力してください。")
