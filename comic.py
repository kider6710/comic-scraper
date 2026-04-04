import requests
from bs4 import BeautifulSoup

print("報告主人，僕人已換上『人類偽裝服』，準備再次潛入偵察...")

# 1. 告訴僕人目標網址（如果您的漫畫是在特定的新書頁面看到的，請把網址替換成那個頁面）
url = "https://www.tongli.com.tw/webpagebooks.aspx?page=1&s=1"

# 2. 為僕人準備一件逼真的「人類偽裝服」
# 這樣警衛就會以為我們是一般的 Windows 電腦與 Chrome 瀏覽器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 3. 這次敲門時，穿上偽裝服 (加入 headers)
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

# 4. 拿出放大鏡（BeautifulSoup）
soup = BeautifulSoup(response.text, "html.parser")

# 5. 找出所有貼著 "pk_txt" 貼紙的大紙盒
comic_boxes = soup.find_all("div", class_="pk_txt")

print(f"\n突破防線！主人，僕人這次總共為您找到了 {len(comic_boxes)} 本漫畫情報！")
print("以下是為您整理的專屬清單：")
print("=" * 40)

# 6. 請僕人把紙盒一個一個打開
for box in comic_boxes:
    # 拿出 <em> 標籤裡的書名
    title_tag = box.find("em")
    title = title_tag.text if title_tag else "未知書名"
    
    # 拿出所有的 <span> 標籤
    spans = box.find_all("span")
    author = spans[0].text if len(spans) > 0 else "未知作者"
    volume = spans[1].text if len(spans) > 1 else ""
    
    # 向主人報告
    print(f"📘 書名：{title} {volume}")
    print(f"✍️ 作者：{author}")
    print("-" * 40)

print("\n報告完畢！主人，您的匿蹤爬蟲系統已完美升級！")