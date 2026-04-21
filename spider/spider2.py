import requests
from bs4 import BeautifulSoup

url = "https://project-two-tau-18.vercel.app/about"
Data = requests.get(url)
Data.encoding = "utf-8"
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.select("#pic")#抓id名稱

for item in result:
	print(item.text)
	print(item.get('src'))#圖形檔
	print()

