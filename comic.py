import requests
from bs4 import BeautifulSoup
from datetime import datetime

print("報告主人，僕人正在為您抓取並排版今日的漫畫清單...")

# 1. 取得今日日期，讓標題更有質感
today_str = datetime.now().strftime("%Y年%m月%d日")

url = "https://www.tongli.com.tw/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, "html.parser")
comic_boxes = soup.find_all("div", class_="pk_txt")

# 2. 準備要寫入展示牆的「Markdown 排版內容」
md_content = f"# 📅 {today_str} 台灣漫畫新書情報\n\n"
md_content += "早安，主人！以下是僕人為您整理的最新漫畫清單：\n\n"
md_content += "| 📘 書名 | ✍️ 作者 | 🏷️ 集數 |\n"
md_content += "| :--- | :--- | :--- |\n"

# 3. 把每一本書的資料填入表格中
for box in comic_boxes:
    title_tag = box.find("em")
    title = title_tag.text if title_tag else "未知書名"
    
    spans = box.find_all("span")
    author = spans[0].text if len(spans) > 0 else "未知作者"
    volume = spans[1].text if len(spans) > 1 else ""
    
    # 寫入表格的每一列
    md_content += f"| **{title}** | {author} | {volume} |\n"

md_content += "\n---\n*管家敬上：您的專屬自動化收集系統每日為您更新*"

# 4. 吩咐僕人將排版好的內容，寫入名為 README.md 的展示牆檔案中
with open("README.md", "w", encoding="utf-8") as file:
    file.write(md_content)

print("報告完畢！主人，精美展示牆已繪製完成！")