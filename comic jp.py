import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime

print("報告主人！honto 專屬情報僕人已就緒，正在為您搜刮日本漫畫新刊...")

url = "https://honto.jp/cp/ebook/recent/comic-calendar.html"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
json_file = "data.json"

# 讀取主人現有的金庫帳本
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            all_data = json.load(f)
        except:
            all_data = {}
else:
    all_data = {}

try:
    res = requests.get(url, headers=headers, timeout=15)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, "html.parser")
    
    # 找出主人發現的所有「連體嬰貨架 (tr)」
    rows = soup.find_all("tr")
    current_year = datetime.now().year
    count = 0
    
    for row in rows:
        tds = row.find_all("td")
        # 確保這個貨架上至少有兩個格子（有日期也有書本）
        if len(tds) >= 2:
            # 第一步：從左邊的格子拿出日期字串
            date_str = tds[0].text.strip()
            # 用正規表達式萃取出數字 (例如 4/1)
            date_match = re.search(r"(\d{1,2})/(\d{1,2})", date_str)
            if not date_match:
                continue
                
            month, day = date_match.groups()
            # 幫主人補齊為標準的 YYYY-MM-DD 格式
            book_real_date = f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # 第二步：從右邊的格子拿出所有書本寶藏
            info_td = tds[1]
            
            title_tag = info_td.find("a", class_="t")
            title = title_tag.text.strip() if title_tag else "未知書名"
            
            # 拔掉「著者：」的前綴
            author_tag = info_td.find("span", class_="a")
            author = author_tag.text.replace("著者：", "").strip() if author_tag else "未知作者"
            
            # 拔掉「出版社：」的前綴
            publisher_tag = info_td.find("span", class_="p")
            publisher = publisher_tag.text.replace("出版社：", "").strip() if publisher_tag else "未知出版社"
            
            img_tag = info_td.find("img")
            cover = img_tag["src"] if img_tag else ""
            
            # 寫入帳本的專屬抽屜
            if book_real_date not in all_data:
                all_data[book_real_date] = {}
            if publisher not in all_data[book_real_date]:
                all_data[book_real_date][publisher] = []
                
            # 檢查是否已經有同一本書，避免重複塞入
            if not any(b['title'] == title for b in all_data[book_real_date][publisher]):
                all_data[book_real_date][publisher].append({
                    "title": title,
                    "author": author,
                    "volume": "",
                    "series": "日本電子書", # 我們先給它一個帥氣的系列名
                    "cover": cover
                })
                count += 1

    # 將帳本照日期排好並存檔
    sorted_data = dict(sorted(all_data.items(), key=lambda x: x[0], reverse=True))
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
        
    print(f"🎉 報告完畢！僕人已成功為您奪回 {count} 筆日本漫畫新刊情報，並完美安放於金庫中！")

except Exception as e:
    print(f"❌ 搜刮任務發生意外：{e}")