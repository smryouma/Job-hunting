import firebase_admin
from firebase_admin import credentials, firestore

# Firebaseの認証情報を取得
cred = credentials.Certificate('/Users/ooishikonryouma/就活/job-hunting-cea79-firebase-adminsdk-fbsvc-57d47daaeb.json')
firebase_admin.initialize_app(cred)

# Firestoreのインスタンスを作成
db = firestore.client()
print('Firestoreに接続しました。')
