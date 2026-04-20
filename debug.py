import requests
from bs4 import BeautifulSoup

print("報告主人，探測僕人已出發，正在敲擊東立的歷史檔案室大門...")

url = "https://www.tongli.com.tw/webpagebooks.aspx?page=1&s=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. 檢查警衛是否有放行
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
print(f"【大門狀態報告】HTTP 狀態碼：{response.status_code} (200代表成功放行)")

# 2. 檢查房間裡的紙盒數量
soup = BeautifulSoup(response.text, "html.parser")
img_boxes = soup.find_all("div", class_="pk_img")
txt_boxes = soup.find_all("div", class_="pk_txt")

print(f"【視覺探測報告】發現 {len(img_boxes)} 個圖片盒，以及 {len(txt_boxes)} 個文字盒。")

# 3. 如果找不到紙盒，就把大門口看到的景象拍下來回傳
if len(img_boxes) == 0:
    print("\n⚠️ 警告！找不到任何紙盒。僕人拍下了網頁前 1000 個字元的景象：")
    print("-" * 50)
    print(response.text[:1000])
    print("-" * 50)
else:
    print("✨ 太好了！僕人成功看到了紙盒，網頁結構正常！")