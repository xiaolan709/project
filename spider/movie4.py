import firebase_admin
from firebase_admin import credentials, firestore

# 1. 初始化 Firebase (建議放在最外面)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

import requests
from bs4 import BeautifulSoup

url = "http://www.atmovies.com.tw/movie/next/"
Data = requests.get(url)
Data.encoding = "utf-8"

sp = BeautifulSoup(Data.text, "html.parser")
# 取得更新時間
updateDate = sp.find("div", class_="smaller09").text.replace("更新時間：", "")
result = sp.select(".filmListAllX li")
info = ""

for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")

    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    
    # 2. 修正縮排與判斷邏輯
    if "片長" in show:
        show = show.replace("片長：", "").replace("分", "")
        showDate = show[0:10]
        showLength = show[13:].replace(" ", "")
    else:
        showDate = show[0:10]
        showLength = "尚無片長資訊"

    # 3. 整理要上傳的資料
    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": updateDate  # 修正變數名稱：將 updateDate 存入 lastUpdate 欄位
    }

    # 4. 寫入資料庫
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)

    info += f"{movie_id}\n{picture}\n{title}\n{hyperlink}\n{showDate}\n{showLength}\n\n"

# 5. 最後再把更新時間加上去
info += updateDate
print(info)