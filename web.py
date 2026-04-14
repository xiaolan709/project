from flask import Flask, render_template,request
from datetime import datetime
import random

app = Flask(__name__) # 建立一個網站應用程式

@app.route("/")
def index():
    link = "<h1>歡迎進入小嵐的網站首頁</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今天日期時間</a><hr>"
    link += "<a href=/about>關於小嵐</a><hr>"
    link += "<a href=/welcome?u=小嵐&dep=靜宜資管>GET傳值</a><hr>"
    link += "<a href=/account>POST傳值(帳號密碼)</a><hr>"
    link += "<a href=/math>數學運算</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    return link

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
