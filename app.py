import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import time  # ← ★新たに追加：時間をコントロールする部品

# --- 1. アプリの基本設定とロック ---
st.set_page_config(page_title="なるちゃん投資分析システム", layout="wide")

# パスワードロック
if "APP_PASSWORD" in st.secrets:
    entered_password = st.sidebar.text_input("🔑 起動パスワード", type="password")
    if entered_password != st.secrets["APP_PASSWORD"]:
        st.warning("左のメニューにパスワードを入力してください。")
        st.stop()

# AIの設定
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
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
        try:
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
                        try:
                            prompt = f"{name}({ticker_symbol})のPER{info.get('trailingPE')}倍、利回り{info.get('dividendYield',0)*100:.1f}%から、今後の見通しを分析して。"
                            res = model.generate_content(prompt)
                            st.info(res.text)
                        except Exception as e:
                            st.error(f"AI分析失敗: {e}")
        except Exception as e:
            st.error(f"データ取得エラー: {e}")

# --- 4. 【ページB】掘り出し物探し ---
elif menu == "🏆 掘り出し物探し":
    st.title("🏆 お宝銘柄スクリーニング")
    st.write("指定したカテゴリの銘柄から、条件に合う株を抽出します。")

    categories = {
        "🔥 日経225 フルスキャン (約3〜4分)": [
            "1332.T", "1605.T", "1721.T", "1801.T", "1802.T", "1803.T", "1808.T", "1812.T", "1925.T", "1928.T",
            "2269.T", "2282.T", "2413.T", "2432.T", "2501.T", "2502.T", "2503.T", "2531.T", "2768.T", "2801.T",
            "2802.T", "2871.T", "2914.T", "3086.T", "3092.T", "3099.T", "3100.T", "3103.T", "3141.T", "3289.T",
            "3382.T", "3401.T", "3402.T", "3405.T", "3407.T", "3436.T", "3659.T", "3861.T", "3863.T", "3993.T",
            "4004.T", "4005.T", "4021.T", "4041.T", "4042.T", "4043.T", "4061.T", "4063.T", "4151.T", "4183.T",
            "4188.T", "4204.T", "4208.T", "4324.T", "4452.T", "4502.T", "4503.T", "4506.T", "4507.T", "4519.T",
            "4523.T", "4543.T", "4568.T", "4578.T", "4631.T", "4661.T", "4689.T", "4704.T", "4736.T", "4751.T",
            "4901.T", "4902.T", "4911.T", "5019.T", "5020.T", "5101.T", "5108.T", "5201.T", "5202.T", "5214.T",
            "5232.T", "5233.T", "5301.T", "5332.T", "5333.T", "5401.T", "5406.T", "5411.T", "5541.T", "5631.T",
            "5703.T", "5706.T", "5711.T", "5713.T", "5714.T", "5801.T", "5802.T", "5803.T", "5831.T", "6098.T",
            "6103.T", "6113.T", "6301.T", "6302.T", "6305.T", "6326.T", "6361.T", "6367.T", "6471.T", "6472.T",
            "6473.T", "6501.T", "6503.T", "6504.T", "6506.T", "6594.T", "6645.T", "6701.T", "6702.T", "6724.T",
            "6752.T", "6758.T", "6762.T", "6770.T", "6841.T", "6857.T", "6861.T", "6902.T", "6952.T", "6954.T",
            "6971.T", "6976.T", "6981.T", "6988.T", "7011.T", "7012.T", "7013.T", "7182.T", "7186.T", "7201.T",
            "7202.T", "7203.T", "7205.T", "7211.T", "7259.T", "7261.T", "7267.T", "7269.T", "7270.T", "7272.T",
            "7731.T", "7733.T", "7735.T", "7741.T", "7751.T", "7752.T", "7762.T", "7832.T", "7911.T", "7912.T",
            "7951.T", "7974.T", "8001.T", "8002.T", "8015.T", "8031.T", "8035.T", "8053.T", "8058.T", "8233.T",
            "8242.T", "8252.T", "8267.T", "8304.T", "8306.T", "8308.T", "8309.T", "8316.T", "8331.T", "8354.T",
            "8411.T", "8591.T", "8601.T", "8604.T", "8628.T", "8630.T", "8697.T", "8725.T", "8750.T", "8766.T",
            "8795.T", "8801.T", "8802.T", "8804.T", "8830.T", "8901.T", "9001.T", "9005.T", "9007.T", "9008.T",
            "9009.T", "9020.T", "9021.T", "9022.T", "9064.T", "9101.T", "9104.T", "9107.T", "9147.T", "9202.T",
            "9301.T", "9432.T", "9433.T", "9434.T", "9501.T", "9502.T", "9503.T", "9531.T", "9532.T", "9602.T",
            "9613.T", "9735.T", "9766.T", "9843.T", "9983.T", "9984.T"
        ],
        "🌟 お気に入り高配当 (10社)": ["8058.T", "8316.T", "9101.T", "8593.T", "9434.T", "7203.T", "8001.T", "1928.T", "8053.T", "2914.T"],
        "🏢 総合商社 (7社)": ["8058.T", "8001.T", "8002.T", "8031.T", "8053.T", "2768.T", "8015.T"],
        "🏦 銀行・金融 (8社)": ["8306.T", "8316.T", "8411.T", "8308.T", "8309.T", "7182.T", "8593.T", "8766.T"]
    }

    selected_category = st.selectbox("スキャンする業界・グループを選択してください", list(categories.keys()))
    check_list = categories[selected_category]

    if st.button(f"{selected_category} をスキャン開始"):
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        total = len(check_list)

        with st.spinner("データを取得・計算しています..."):
            for i, t in enumerate(check_list):
                progress_bar.progress((i + 1) / total)
                status_text.text(f"スキャン中... {i+1}/{total}社完了")

                try:
                    s = yf.Ticker(t)
                    info = s.info
                    
                    if 'trailingPE' not in info or 'dividendYield' not in info:
                        time.sleep(0.5) # ★データが無い時も0.5秒休む
                        continue
                        
                    per = info.get('trailingPE', 100)
                    div = info.get('dividendYield', 0) * 100
                    
                    if per < 15 and div > 3.5:
                        results.append({
                            "銘柄": info.get('shortName', t),
                            "コード": t,
                            "PER": f"{per:.1f}倍",
                            "利回り": f"{div:.2f}%",
                            "価格": f"¥{info.get('currentPrice', 'N/A')}"
                        })
                except:
                    pass
                
                # ★最大のポイント：1社調べるごとに0.5秒の深呼吸を入れる
                time.sleep(0.5)
        
        status_text.text("✨ スキャン完了！")

        if results:
            st.success(f"条件に合う銘柄が {len(results)} 件見つかりました！")
            st.table(pd.DataFrame(results))
            
            st.subheader("🤖 AIのピックアップ")
            try:
                ai_res = model.generate_content(f"以下のリストから、初心者が長期で持つべき銘柄を1つ選んで理由を教えて：{results}")
                st.info(ai_res.text)
            except Exception as e:
                st.error(f"AI分析中にエラーが発生しました: {e}")
        else:
            st.warning("現在は条件に合う銘柄がありませんでした。")
