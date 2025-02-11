import firebase_admin
from firebase_admin import credentials, firestore

# Firestore の初期化をチェック
if not firebase_admin._apps:
    cred = credentials.Certificate("job-hunting-cea79-firebase-adminsdk-fbsvc-57d47daaeb.json")  # 🔹 キーファイル名を正しく指定
    firebase_admin.initialize_app(cred)

# Firestoreのインスタンスを作成
db = firestore.client()

# 企業データを取得
def get_companies():
    docs = db.collection("companies").stream()
    return [doc.to_dict() for doc in docs]

# 取得したデータを表示
companies = get_companies()
print("Firestoreに保存されている企業一覧:")
for company in companies:
    print(company["name"])
