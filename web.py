import requests
from bs4 import BeautifulSoup

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)


from flask import Flask, render_template,request
from datetime import datetime
import random

app = Flask(__name__) # 建立一個網站應用程式

@app.route("/")
def index():
    link = "<h1>歡迎進入小嵐的網站首頁</h1>"
    link += "<a href=/spider>查詢即將上映電影</a><hr>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今天日期時間</a><hr>"
    link += "<a href=/about>關於小嵐</a><hr>"
    link += "<a href=/welcome?u=小嵐&dep=靜宜資管>GET傳值</a><hr>"
    link += "<a href=/account>POST傳值(帳號密碼)</a><hr>"
    link += "<a href=/math>數學運算</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<a href=/search>查詢老師</a><hr>"
    link += "<br><a href=/read>讀取Firestore資料(根據lab遞減排序，取前四筆)</a><br>"
    link += "<br><a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    link += "<a href=/searchQ>搜尋電影(Firestore查詢)</a><hr>"
    link += "<a href=/road>查詢台中市易肇事路口</a><hr>"
    link += "<a href=/weather>查詢縣市天氣預報</a><hr>"
    return link


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        db = firestore.client()
        # 取得所有老師資料
        collection_ref = db.collection("靜宜資管2026")
        docs = collection_ref.stream()
        
        result = f"<h1>查詢關鍵字：{keyword}</h1>"
        found = False
        for doc in docs:
            user = doc.to_dict()
            if keyword in user.get("name", ""):
                result += f"<p>{user['name']} 老師的研究室是在 {user['lab']}</p>"
                found = True
        
        if not found:
            result += "<p>找不到符合條件的老師。</p>"
        result += '<br><a href="/search">重新查詢</a> | <a href="/">回首頁</a>'
        return result

    # 這是原本顯示在網頁上的輸入框
    return """
        <h1>查詢老師研究室</h1>
        <form method="POST">
            請輸入老師姓名關鍵字：
            <input type="text" name="keyword">
            <button type="submit">查詢</button>
        </form>
        <br><a href="/">回首頁</a>
    """

@app.route("/spider")
def spider():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"

    sp = BeautifulSoup(Data.text, "html.parser")
    # 開眼電影網的結構中，電影資訊通常在 .filmListAllX 的 li 標籤內
    result = sp.select(".filmListAllX li")

    output = "<h2>即將上映電影</h2>"
    output += "<ul>" # 使用列表讓排版更整齊

    for item in result:
        # 1. 嘗試抓取 <a> 標籤獲取連結與名稱
        a_tag = item.find("a")
        if a_tag:
            # 獲取連結 (加上開眼官網的前綴網址)
            link = "http://www.atmovies.com.tw" + a_tag.get("href")
            
            # 2. 獲取電影名稱 (通常在 img 的 alt 屬性或是 a 標籤的 text)
            img_tag = item.find("img")
            if img_tag and img_tag.get("alt"):
                title = img_tag.get("alt")
            else:
                title = a_tag.text.strip()
            
            # 3. 組合超連結 HTML
            output += f"<li><a href='{link}' target='_blank'>{title}</a></li>"
            
    output += "</ul>"
    output += "<br><a href='/'>回首頁</a>"
    return output


@app.route("/read")
def read():
    db = firestore.client()

    temp = ""
    collection_ref = db.collection("靜宜資管2026")
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).limit(4).get()
    for doc in docs:
        temp += str(doc.to_dict()) + "<br>"

    return temp

@app.route("/mis")
def course():
    return "<h1>資訊管理導論課程</h1>"

@app.route("/today")
def today():
    now_dt = datetime.now()
    year = str(now_dt.year)
    month = str(now_dt.month)
    day = str(now_dt.day)
    hour = str(now_dt.hour)
    minute = str(now_dt.minute)
    second = str(now_dt.second)

    now_str = year + "年" + month + "月" + day + "日 " + hour + "時" + minute + "分" + second + "秒"
    return render_template("today.html", datetime=now_str)

@app.route("/about")
def about():
    return render_template("Mis2a.html")

@app.route("/welcome",methods=["GET"])
def welcome():
    x= request.values.get("u")
    y= request.values.get("dep")
    return render_template("welcome.html",name = x,dep = y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math_calc():
    if request.method == "POST":
        # 取得表單傳來的資料
        try:
            x = float(request.form["x"]) # 使用 float 支援小數，避免剛剛的型別錯誤
            opt = request.form["opt"]
            y = float(request.form["y"])
            
            if opt == "/" and y == 0:
                result = "除數不能為0"
            else:
                if opt == "+": result = x + y
                elif opt == "-": result = x - y
                elif opt == "*": result = x * y
                elif opt == "/": result = x / y
                else: result = "未知運算符"
            
            # 將結果傳回同一個頁面顯示
            response_text = f"{x} {opt} {y} 的結果是：{result}"
            return render_template("math.html", result=response_text)
        except:
            return render_template("math.html", result="請輸入有效的數字")
            
    return render_template("math.html")

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)

@app.route("/movie")
def movie():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)    
  return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 

@app.route("/road", methods=["GET", "POST"])
def road():
    url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"
    results_list = []
    road_query = ""

    # 當使用者按下「查詢」按鈕（發送 POST 請求）時執行
    if request.method == "POST":
        road_query = request.form.get("RoadName") # 取得網頁輸入框的內容
        
        try:
            # 爬取政府開放資料並轉為 JSON 格式
            data = requests.get(url)
            json_data = json.loads(data.text)
            
            # 過濾符合路名的資料並整理成清單
            for item in json_data:
                if road_query and road_query in item["路口名稱"]:
                    results_list.append({
                        "location": item["路口名稱"],
                        "count": item["總件數"],
                        "reason": item["主要肇因"]
                    })
        except Exception as e:
            print(f"資料讀取失敗: {e}")

    # 將結果送到前端網頁渲染
    return render_template("traffic.html", results=results_list, road_name=road_query)

@app.route("/weather", methods=["GET", "POST"])
def weather():
    city = ""
    weather_info = None
    
    if request.method == "POST":
        city = request.form.get("city").replace("台", "臺")
        token = "rdec-key-123-45678-011121314" # 建議換成你申請的真實 Token
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={token}&format=JSON&locationName={city}"
        
        try:
            data = requests.get(url)
            json_data = json.loads(data.text)
            
            # 解析資料
            location_data = json_data["records"]["location"][0]
            weather_state = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            rain_chance = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
            temp_min = location_data["weatherElement"][2]["time"][0]["parameter"]["parameterName"]
            temp_max = location_data["weatherElement"][4]["time"][0]["parameter"]["parameterName"]
            
            weather_info = {
                "city": city,
                "state": weather_state,
                "rain": rain_chance,
                "temp": f"{temp_min}~{temp_max} °C"
            }
        except Exception as e:
            print(f"氣象資料抓取失敗: {e}")

    return render_template("weather.html", info=weather_info)

@app.route("/searchQ", methods=["POST", "GET"])
def searchQ():
    if request.method == "POST":
        # 1. 取得使用者在表單輸入的片名
        MovieTitle = request.form["MovieTitle"]
        info = ""
        
        # 2. 連接 Firebase
        db = firestore.client()
        collection_ref = db.collection("電影")
        
        # 3. 讀取所有電影資料，並按上映日期排序
        docs = collection_ref.order_by("showDate").get()
        
        found = False
        for doc in docs:
            movie_data = doc.to_dict()
            # 4. 判斷輸入的關鍵字是否在電影標題中
            if MovieTitle in movie_data.get("title", ""):
                info += "片名：" + movie_data.get("title") + "<br>"
                info += "影片介紹：" + movie_data.get("hyperlink") + "<br>"
                info += "片長：" + movie_data.get("showLength") + " 分鐘<br>"
                info += "上映日期：" + movie_data.get("showDate") + "<br><br>"
                found = True
        
        if not found:
            info = f"抱歉，找不到包含「{MovieTitle}」的電影。<br><br>"
            
        info += '<a href="/searchQ">重新查詢</a> | <a href="/">回首頁</a>'
        return info
    else:
        # 如果是 GET 請求（剛進網頁時），顯示輸入框頁面
        return render_template("input.html")

if __name__ == "__main__":
    app.run()
