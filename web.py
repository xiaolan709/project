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
    result=sp.find(".filmListAllX li")

    output = "<h2>即將上映電影</h2>"
    for item in result:
        img_tag = item.find("img")
        # 檢查是否有抓到 img 標籤以及 alt 屬性
        if img_tag and img_tag.get("alt"):
            title = img_tag.get("alt")
            output += f"{title}<br>"
            
    output += "<a href='/'>回首頁</a>"
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


if __name__ == "__main__":
    app.run()
