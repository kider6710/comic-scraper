import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re

print("報告主人，僕人已裝備『內頁深度掃描儀』，準備揭開真實日期的面紗...")

json_file = "data.json"
base_url = "https://www.tongli.com.tw"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            all_data = json.load(f)
        except:
            all_data = {}
else:
    all_data = {}

for page_num in range(1, 5):
    print(f"\n=== 正在強行突破第 {page_num} 頁的書架 ===")
    url = f"https://www.tongli.com.tw/webpagebooks.aspx?page={page_num}&s=1"
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        
        img_boxes = soup.find_all("div", class_="pk_img")
        txt_boxes = soup.find_all("div", class_="pk_txt")

        for img_box, txt_box in zip(img_boxes, txt_boxes):
            title_tag = txt_box.find("em")
            title = title_tag.text.strip() if title_tag else "未知書名"
            spans = txt_box.find_all("span")
            author = spans[0].text.strip() if len(spans) > 0 else "未知作者"
            volume = spans[1].text.strip() if len(spans) > 1 else ""

            # 進入內頁抓取 (這裡才是真正的寶庫)
            a_tag = img_box.find("a")
            if not a_tag: continue
            detail_url = base_url + "/" + a_tag["href"].lstrip("/")
            
            print(f"正在潛入《{title}》的房間，尋找真實出版日...")
            
            try:
                d_res = requests.get(detail_url, headers=headers, timeout=15)
                d_res.encoding = 'utf-8'
                d_soup = BeautifulSoup(d_res.text, "html.parser")
                
                # 抓取封面網址
                cover_tag = img_box.find("img")
                cover_url = base_url + cover_tag["src"] if cover_tag else ""

                # 抓取系列別
                series_tag = d_soup.find("span", id="ContentPlaceHolder1_ReaderTxt")
                series_name = series_tag.text.strip() if series_tag else "無系列資訊"

                # 【核心破解】在內頁全文中強制尋找真實日期
                book_real_date = ""
                # 利用正規表達式搜尋內頁裡長得像 2026/04/16 的字串
                date_match = re.search(r"(\d{4}/\d{1,2}/\d{1,2})", d_soup.text)
                if date_match:
                    book_real_date = date_match.group(1).replace("/", "-")
                    # 補齊月份與日期的零 (例如 2026-4-1 轉為 2026-04-01)
                    parts = book_real_date.split("-")
                    book_real_date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                else:
                    print(f"  ⚠️ 房間內找不到《{title}》的日期，忍痛跳過。")
                    continue
                    
                print(f"  ✨ 成功尋獲！真實出版日：{book_real_date}")

            except Exception as e:
                print(f"  ❌ 房間遭遇干擾: {e}")
                continue

            # 按照書籍原始日期歸檔
            if book_real_date not in all_data:
                all_data[book_real_date] = {"東立": []}
            elif "東立" not in all_data[book_real_date]:
                all_data[book_real_date]["東立"] = []

            # 檢查重複性，避免重複收錄
            if not any(b['title'] == title and b['volume'] == volume for b in all_data[book_real_date]["東立"]):
                all_data[book_real_date]["東立"].append({
                    "title": title,
                    "author": author,
                    "volume": volume,
                    "series": series_name,
                    "cover": cover_url
                })
        
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ 巡邏第 {page_num} 頁時發生意外：{e}")

# 重新整理帳本 (依日期降序排列)
sorted_data = dict(sorted(all_data.items(), key=lambda x: x[0], reverse=True))

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(sorted_data, f, ensure_ascii=False, indent=2)

print(f"\n報告完畢！僕人已徹底完成歷史歸檔任務。")