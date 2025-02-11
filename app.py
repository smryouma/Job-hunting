import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

st.title("就活タスク管理アプリ「タスカン！！」")

# 🔹 Firebaseの認証方法を変更（GitHub Actions対応）
if not firebase_admin._apps:
    firebase_key_env = os.getenv("FIREBASE_PRIVATE_KEY")  # 環境変数から読み込み

    if firebase_key_env:  # GitHub Actions で環境変数を使用
        firebase_credentials = json.loads(firebase_key_env.replace("\\n", "\n"))  # 改行を処理
        cred = credentials.Certificate(firebase_credentials)
    else:  # ローカル開発環境の場合
        firebase_key_path = "/Users/ooishikonryouma/株価分析/path/firebase_key.json"
        cred = credentials.Certificate(firebase_key_path)

    firebase_admin.initialize_app(cred)

db = firestore.client()

# 🔹 「企業を追加する」ボタンでフォームを表示・非表示
if "show_add_company_form" not in st.session_state:
    st.session_state.show_add_company_form = False

if st.button("企業を追加する"):
    st.session_state.show_add_company_form = not st.session_state.show_add_company_form

if st.session_state.show_add_company_form:
    st.subheader("企業を追加")
    new_company = st.text_input("企業名を入力してください:")
    es_url = st.text_input("ES URL:")
    recruit_url = st.text_input("採用ページURL:")
    company_hp = st.text_input("企業HP:")
    memo_url = st.text_input("メモURL:")

    if st.button("追加"):
        if new_company.strip():
            doc_ref = db.collection("companies").document()
            doc_ref.set({
                "name": new_company, 
                "status": "ES未提出",
                "es": "❌",
                "analysis": "❌",
                "es_url": es_url,
                "recruit_url": recruit_url,
                "company_hp": company_hp,
                "memo_url": memo_url
            })  
            st.success(f"✅ {new_company} を追加しました！")
            st.experimental_rerun()
        else:
            st.warning("⚠️ 企業名を入力してください！")

# 🔹 Firestoreから企業リストを取得
docs = db.collection("companies").stream()
companies = {doc.id: doc.to_dict() for doc in docs}

# 🔹 表データを作成
if companies:
    import pandas as pd
    data = []
    for company_id, company_data in companies.items():
        data.append({
            "企業名": company_data["name"],
            "選考状況": company_data.get("status", "ES未提出"),
            "ES": company_data.get("es", "❌"),
            "企業分析": company_data.get("analysis", "❌"),
            "ES URL": f"({company_data.get('es_url', '')})" if company_data.get("es_url") else "",
            "採用ページURL": f"({company_data.get('recruit_url', '')})" if company_data.get("recruit_url") else "",
            "企業HP": f"({company_data.get('company_hp', '')})" if company_data.get("company_hp") else "",
            "メモURL": f"({company_data.get('memo_url', '')})" if company_data.get("memo_url") else "",
            "ID": company_id  
        })

    df = pd.DataFrame(data)

    # 🔹 選択可能なオプション
    status_options = ["ES未提出", "一次面接", "内定", "お祈り"]
    es_options = ["⭕", "❌"]
    analysis_options = ["⭕", "❌"]

    # 🔹 表の編集（選考状況・ES提出・企業分析を選択可能に）
    edited_df = st.data_editor(
        df[["企業名", "選考状況", "ES", "企業分析", "ES URL", "採用ページURL", "企業HP", "メモURL"]],
        column_config={
            "選考状況": st.column_config.SelectboxColumn("選考状況", options=status_options),
            "ES": st.column_config.SelectboxColumn("ES", options=es_options),
            "企業分析": st.column_config.SelectboxColumn("企業分析", options=analysis_options),
            "ES URL": st.column_config.LinkColumn("ES URL"),
            "採用ページURL": st.column_config.LinkColumn("採用ページURL"),
            "企業HP": st.column_config.LinkColumn("企業HP"),
            "メモURL": st.column_config.LinkColumn("メモURL"),
        },
        num_rows="fixed",
        key="company_table"
    )

    # 🔹 Firestoreを更新（変更があった場合のみ）
    for index, row in edited_df.iterrows():
        original_row = df.loc[index]
        company_id = original_row["ID"]

        update_data = {}
        for col in ["選考状況", "ES", "企業分析"]:
            if row[col] != original_row[col]:  
                update_data[col] = row[col]

        if update_data:
            db.collection("companies").document(company_id).update(update_data)
            st.experimental_rerun()
