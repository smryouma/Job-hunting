import streamlit as st
import pandas as pd

#仮のサンプルデータ
companese = []

# タイトル
st.title("就活管理！")

# 企業の追加
new_company = st.text_input("企業名を入力してください")
if st.button("追加"):
    if new_company:
        companese.append({"企業名": new_company})
        st.success(f"{new_company}を追加しました！")

# 企業の一覧
if companese:
    df = pd.DataFrame(companese)
    st.write("### 企業一覧")
    st.write(df)