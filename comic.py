import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re

print("報告主人！雙引擎情報僕人已就緒，準備為您征服『東立』與『台灣角川』的歷史版圖...")

json_file = "data.json"
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

# ==========================================
# 任務一：潛入台灣角川 (兩段式深度爬取)
# ==========================================
print("\n=== 🚀 開始執行角川潛入任務 ===")
kadokawa_base_url = "https://www.kadokawa.com.tw"

# 巡邏角川前 3 頁
for page_num in range(1, 4):
    print(f"正在掃描台灣角川第 {page_num} 頁的書架...")
    k_url = f"{kadokawa_base_url}/categories/%E6%96%B0%E5%88%8A%E5%BF%AB%E5%A0%B1?page={page_num}"
    
    try:
        res = requests.get(k_url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 找出主人發現的最大外箱
        items = soup.find_all("product-item")
        
        for item in items:
            title_tag = item.find("div", class_="title")
            title = title_tag.text.strip() if title_tag else "未知書名"
            
            # 取得黃金鑰匙 (內頁網址)
            a_tag = item.find("a", class_="quick-cart-item")
            if not a_tag: continue
            
            detail_url = a_tag["href"]
            if not detail_url.startswith("http"):
                detail_url = kadokawa_base_url + detail_url
                
            print(f"  正在拿鑰匙進入房間探勘：《{title}》...")
            
            # 進入房間拿取寶箱
            try:
                d_res = requests.get(detail_url, headers=headers, timeout=15)
                d_res.encoding = 'utf-8'
                d_soup = BeautifulSoup(d_res.text, "html.parser")
                
                # 鎖定主人發現的黃金寶箱
                summary_tag = d_soup.find("p", class_="Product-summary")
                book_real_date = ""
                author = "未知作者"
                
                if summary_tag:
                    # 將 <br> 轉為換行符號，方便萃取
                    summary_text = summary_tag.get_text(separator='\n')
                    
                    # 萃取上市日期
                    date_match = re.search(r"上市日期：(\d{4}/\d{1,2}/\d{1,2})", summary_text)
                    if date_match:
                        book_real_date = date_match.group(1).replace("/", "-")
                        parts = book_real_date.split("-")
                        book_real_date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                        
                    # 萃取作者
                    author_match = re.search(r"作者：([^\n]+)", summary_text)
                    if author_match:
                        author = author_match.group(1).strip()
                
                if not book_real_date:
                    print(f"  ⚠️ 房間內找不到《{title}》的日期，跳過。")
                    continue
                
                # 抓取封面網址
                cover_tag = d_soup.find("img", class_="js-boxify-image")
                cover_url = cover_tag["src"] if cover_tag and "src" in cover_tag.attrs else ""
                # 角川圖片通常在 data-src 或是 src 裡，做個簡單防呆
                if not cover_url and cover_tag and "data-src" in cover_tag.attrs:
                    cover_url = cover_tag["data-src"]

                # 寫入帳本 (角川專區)
                if book_real_date not in all_data:
                    all_data[book_real_date] = {}
                if "台灣角川" not in all_data[book_real_date]:
                    all_data[book_real_date]["台灣角川"] = []
                    
                # 避免重複寫入
                if not any(b['title'] == title for b in all_data[book_real_date]["台灣角川"]):
                    all_data[book_real_date]["台灣角川"].append({
                        "title": title,
                        "author": author,
                        "volume": "",
                        "series": "角川新刊",
                        "cover": cover_url
                    })
                    print(f"  ✨ 成功尋獲並歸檔！日期：{book_real_date}")
                    
            except Exception as e:
                print(f"  ❌ 房間探索失敗: {e}")
                
            time.sleep(1) # 對角川溫柔一點
            
    except Exception as e:
        print(f"❌ 掃描角川第 {page_num} 頁發生意外：{e}")


# ==========================================
# 任務二：潛入東立 (原有的時光歸位邏輯)
# ==========================================
print("\n=== 🚀 開始執行東立潛入任務 ===")
tongli_base_url = "https://www.tongli.com.tw"

for page_num in range(1, 4):
    print(f"正在掃描東立第 {page_num} 頁的書架...")
    t_url = f"{tongli_base_url}/webpagebooks.aspx?page={page_num}&s=1"
    
    try:
        t_res = requests.get(t_url, headers=headers, timeout=20)
        t_res.encoding = 'utf-8'
        t_soup = BeautifulSoup(t_res.text, "html.parser")
        
        img_boxes = t_soup.find_all("div", class_="pk_img")
        txt_boxes = t_soup.find_all("div", class_="pk_txt")

        for img_box, txt_box in zip(img_boxes, txt_boxes):
            title_tag = txt_box.find("em")
            title = title_tag.text.strip() if title_tag else "未知書名"
            spans = txt_box.find_all("span")
            author = spans[0].text.strip() if len(spans) > 0 else "未知作者"
            volume = spans[1].text.strip() if len(spans) > 1 else ""

            a_tag = img_box.find("a")
            if not a_tag: continue
            detail_url = tongli_base_url + "/" + a_tag["href"].lstrip("/")
            
            print(f"  正在潛入東立房間：《{title}》...")
            try:
                d_res = requests.get(detail_url, headers=headers, timeout=15)
                d_res.encoding = 'utf-8'
                d_soup = BeautifulSoup(d_res.text, "html.parser")
                
                cover_tag = img_box.find("img")
                cover_url = tongli_base_url + cover_tag["src"] if cover_tag else ""
                series_tag = d_soup.find("span", id="ContentPlaceHolder1_ReaderTxt")
                series_name = series_tag.text.strip() if series_tag else "無系列資訊"

                book_real_date = ""
                date_match = re.search(r"(\d{4}/\d{1,2}/\d{1,2})", d_soup.text)
                if date_match:
                    book_real_date = date_match.group(1).replace("/", "-")
                    parts = book_real_date.split("-")
                    book_real_date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                else:
                    continue

                if book_real_date not in all_data:
                    all_data[book_real_date] = {}
                if "東立" not in all_data[book_real_date]:
                    all_data[book_real_date]["東立"] = []

                if not any(b['title'] == title and b['volume'] == volume for b in all_data[book_real_date]["東立"]):
                    all_data[book_real_date]["東立"].append({
                        "title": title,
                        "author": author,
                        "volume": volume,
                        "series": series_name,
                        "cover": cover_url
                    })
                    print(f"  ✨ 成功尋獲並歸檔！日期：{book_real_date}")

            except Exception as e:
                continue

            time.sleep(1)
            
    except Exception as e:
        print(f"❌ 掃描東立第 {page_num} 頁發生意外：{e}")


# ==========================================
# 任務三：整理帳本並存檔
# ==========================================
print("\n正在為您整理最終的情報帳本...")
sorted_data = dict(sorted(all_data.items(), key=lambda x: x[0], reverse=True))

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(sorted_data, f, ensure_ascii=False, indent=2)

print(f"🎉 報告完畢！僕人已成功完成雙城歷史歸檔任務！")