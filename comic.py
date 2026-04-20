import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re

print("報告主人，僕人正帶著時光準心出發，準備精準獵取前四頁的每一份情報...")

json_file = "data.json"
base_url = "https://www.tongli.com.tw"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 1. 讀取現有帳本
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            all_data = json.load(f)
        except:
            all_data = {}
else:
    all_data = {}

# 2. 開啟跨時空巡邏：從第 1 頁到第 4 頁
for page_num in range(1, 5):
    print(f"正在掃描第 {page_num} 頁的書架資料...")
    url = f"https://www.tongli.com.tw/webpagebooks.aspx?page={page_num}&s=1"
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        
        img_boxes = soup.find_all("div", class_="pk_img")
        txt_boxes = soup.find_all("div", class_="pk_txt")

        for img_box, txt_box in zip(img_boxes, txt_boxes):
            # 獲取標題與作者
            title_tag = txt_box.find("em")
            title = title_tag.text.strip() if title_tag else "未知書名"
            spans = txt_box.find_all("span")
            author = spans[0].text.strip() if len(spans) > 0 else "未知作者"
            volume = spans[1].text.strip() if len(spans) > 1 else ""

            # 【核心修正】精準抓取書籍原始日期，而非執行日期
            book_real_date = ""
            for s in spans:
                # 尋找符合 YYYY/MM/DD 格式的字串
                date_match = re.search(r"(\d{4}/\d{1,2}/\d{1,2})", s.text)
                if date_match:
                    # 統一轉換為 YYYY-MM-DD 格式
                    book_real_date = date_match.group(1).replace("/", "-")
                    # 補齊月份與日期的零 (例如 2026-4-1 轉為 2026-04-01)
                    parts = book_real_date.split("-")
                    book_real_date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                    break
            
            if not book_real_date:
                continue

            # 進入內頁抓取系列別與封面
            a_tag = img_box.find("a")
            if not a_tag: continue
            detail_url = base_url + "/" + a_tag["href"].lstrip("/")
            
            print(f"正在為日期 {book_real_date} 採集：《{title}》的詳細內容...")
            
            try:
                # 若主人的電腦能連上，建議人工執行不加 Proxy 更快
                d_res = requests.get(detail_url, headers=headers, timeout=15)
                d_res.encoding = 'utf-8'
                d_soup = BeautifulSoup(d_res.text, "html.parser")
                
                # 抓取封面網址
                cover_tag = img_box.find("img")
                cover_url = base_url + cover_tag["src"] if cover_tag else ""

                # 抓取主人最重視的系列別
                series_tag = d_soup.find("span", id="ContentPlaceHolder1_ReaderTxt")
                series_name = series_tag.text.strip() if series_tag else "無系列資訊"
            except:
                series_name = "採集失敗"
                cover_url = ""

            # 3. 按照書籍原始日期歸檔
            if book_real_date not in all_data:
                all_data[book_real_date] = {"東立": []}
            elif "東立" not in all_data[book_real_date]:
                all_data[book_real_date]["東立"] = []

            # 檢查重複性，避免同一天重複抓取
            if not any(b['title'] == title and b['volume'] == volume for b in all_data[book_real_date]["東立"]):
                all_data[book_real_date]["東立"].append({
                    "title": title,
                    "author": author,
                    "volume": volume,
                    "series": series_name,
                    "cover": cover_url
                })
        
        # 每一頁巡邏完稍微喘口氣
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ 巡邏第 {page_num} 頁時發生意外：{e}")

# 4. 重新整理帳本 (依日期降序排列，最新日期在最上面)
sorted_data = dict(sorted(all_data.items(), key=lambda x: x[0], reverse=True))

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(sorted_data, f, ensure_ascii=False, indent=2)

print(f"報告完畢！僕人已成功補齊前四頁情報，所有書籍已回歸原始出版日期金庫。")