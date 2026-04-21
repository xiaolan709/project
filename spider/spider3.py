import requests
from bs4 import BeautifulSoup

url = "https://project-two-tau-18.vercel.app/about"
Data = requests.get(url)
Data.encoding = "utf-8"
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.find("a")#找到符合條件的第一行

print(result)

