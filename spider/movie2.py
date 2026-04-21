import requests
from bs4 import BeautifulSoup

# 1. 加入 Headers 偽裝成一般瀏覽器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "http://www.atmovies.com.tw/movie/next/"

# 2. 請求時帶入 headers
Data = requests.get(url, headers=headers)
Data.encoding = "utf-8"

sp = BeautifulSoup(Data.text, "html.parser")
result = sp.select(".filmListAllx li")

# 3. 檢查是否有抓到資料再跑迴圈
if result:
    for item in result:
        try:
            img = item.find("img")
            link = item.find("a")
            if img and link:
                print(img.get("alt"))
                print("http://www.atmovies.com.tw" + link.get("href"))
                print()
        except Exception as e:
            print(f"處理資料時發生錯誤: {e}")
else:
    print("找不到指定的標籤，請檢查網頁是否改版或被阻擋。")
    # 印出前100個字看看網頁回傳了什麼
    print(Data.text[:100])