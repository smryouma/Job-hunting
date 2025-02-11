import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

st.title("就活タスク管理アプリ「タスカン！！」")

# 🔹 Firebaseの認証方法を変更（GitHub Actions対応）
if not firebase_admin._apps:
    firebase_key_env = os.getenv("FIREBASE_PRIVATE_KEY")  # 環境変数から読み込み
    firebase_key_path = "firebase_key.json"  # ローカル用

    try:
        if firebase_key_env:  # GitHub Actions 環境
            firebase_credentials = json.loads(firebase_key_env.replace("\\n", "\n"))  # 改行を適切に処理
            cred = credentials.Certificate(firebase_credentials)
            st.write("✅ Firebase 認証（GitHub Actions 経由）")
        elif os.path.exists(firebase_key_path):  # ローカル環境にファイルがある場合
            cred = credentials.Certificate(firebase_key_path)
            st.write("✅ Firebase 認証（ローカル firebase_key.json 経由）")
        else:
            st.warning("⚠️ Firebase 認証情報が見つかりませんが、アプリは動作します。")
            cred = None  # Firebase を使わない場合も考慮
    except Exception as e:
        st.error(f"❌ Firebase 認証エラー: {str(e)}")
        cred = None

    if cred:
        firebase_admin.initialize_app(cred)

# 🔹 Firestore クライアントを作成（Firebase が使える場合のみ）
db = None
if cred:
    db = firestore.client()

# 🔹 企業追加フォームの処理
if db:
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
if db:
    docs = db.collection("companies").stream()
    companies = {doc.id: doc.to_dict() for doc in docs}
else:
    companies = {}

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
            "ES URL": f"[リンク]({company_data.get('es_url', '')})" if company_data.get("es_url") else "",
            "採用ページURL": f"[リンク]({company_data.get('recruit_url', '')})" if company_data.get("recruit_url") else "",
            "企業HP": f"[リンク]({company_data.get('company_hp', '')})" if company_data.get("company_hp") else "",
            "メモURL": f"[リンク]({company_data.get('memo_url', '')})" if company_data.get("memo_url") else "",
            "ID": company_id  
        })

    df = pd.DataFrame(data)

    # 🔹 Firestoreを更新（変更があった場合のみ）
    edited_df = st.data_editor(df, num_rows="fixed", key="company_table")

    for index, row in edited_df.iterrows():
        original_row = df.loc[index]
        company_id = original_row["ID"]

        update_data = {}
        for col in ["選考状況", "ES", "企業分析"]:
            if row[col] != original_row[col]:  
                update_data[col] = row[col]

        if update_data and db:
            db.collection("companies").document(company_id).update(update_data)
            st.experimental_rerun()
