import requests
from bs4 import BeautifulSoup
from datetime import datetime

print("報告主人，僕人正在為您繪製精美的網頁...")

today_str = datetime.now().strftime("%Y年%m月%d日")
url = "https://www.tongli.com.tw/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, "html.parser")
comic_boxes = soup.find_all("div", class_="pk_txt")

# 準備網頁的骨架 (HTML) 與美化服裝 (CSS)
html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的專屬漫畫情報站</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif, '微軟正黑體';
            background-color: #f4f7f6;
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 30px;
            max-width: 800px;
            width: 100%;
        }}
        h1 {{ color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #3498db; color: white; }}
        tr:hover {{ background-color: #f1f1f1; }}
        .footer {{ margin-top: 20px; text-align: center; color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📅 {today_str} 台灣漫畫新書情報</h1>
        <p>早安，主人！以下是僕人為您整理的最新漫畫清單：</p>
        <table>
            <thead>
                <tr>
                    <th>📘 書名</th>
                    <th>✍️ 作者</th>
                    <th>🏷️ 集數</th>
                </tr>
            </thead>
            <tbody>
"""

# 把每一本書的資料填入網頁表格中
for box in comic_boxes:
    title_tag = box.find("em")
    title = title_tag.text if title_tag else "未知書名"
    spans = box.find_all("span")
    author = spans[0].text if len(spans) > 0 else "未知作者"
    volume = spans[1].text if len(spans) > 1 else ""
    
    html_content += f"""
                <tr>
                    <td><strong>{title}</strong></td>
                    <td>{author}</td>
                    <td>{volume}</td>
                </tr>
    """

# 補上網頁的結尾
html_content += """
            </tbody>
        </table>
        <div class="footer">管家敬上：您的專屬自動化收集系統每日為您更新</div>
    </div>
</body>
</html>
"""

# 吩咐僕人將排版好的內容，寫入名為 index.html 的網頁大門檔案中
with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("報告完畢！主人，專屬網頁 index.html 已繪製完成！")