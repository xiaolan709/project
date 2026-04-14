import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

collection_ref = db.collection("靜宜資管2026")
docs = collection_ref.get()

keyword = input("你要查詢的老師名子是?")
for doc in docs:
    user = doc.to_dict()
    if keyword in user["name"]:
        print(f"{user['name']}老師的研究室是在{user['lab']}")