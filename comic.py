import requests
from bs4 import BeautifulSoup
import json
import os
import time

print("報告主人，僕人已換上時光回溯裝備，準備為您補齊這幾天的歷史情報...")

json_file = "data.json"

# 1. 讀取現有帳本
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        all_data = json.load(f)
else:
    all_data = {}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
base_url = "https://www.tongli.com.tw"

# 2. 為了補資料，我們讓僕人多巡邏幾頁 (這裡設定爬取前 3 頁)
for page_num in range(1, 4):
    print(f"正在巡邏第 {page_num} 頁的書架...")
    url = f"https://www.tongli.com.tw/webpagebooks.aspx?page={page_num}&s=1"
    
    try:
        # 人工執行時，通常不需要 Proxy 也能順利連線
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        
        img_boxes = soup.find_all("div", class_="pk_img")
        txt_boxes = soup.find_all("div", class_="pk_txt")

        for img_box, txt_box in zip(img_boxes, txt_boxes):
            # 獲取基本資訊
            title = txt_box.find("em").text if txt_box.find("em") else "未知書名"
            spans = txt_box.find_all("span")
            author = spans[0].text if len(spans) > 0 else "未知作者"
            volume = spans[1].text if len(spans) > 1 else ""
            
            # 【關鍵】獲取該書的「實際出版日期」 (格式通常為 YYYY/MM/DD)
            # 東立的列表通常在第三個或第四個 span
            pub_date_raw = "未知日期"
            for s in spans:
                if "/" in s.text and len(s.text) >= 8: # 簡單判斷日期格式
                    pub_date_raw = s.text.strip().replace("/", "-") # 轉為 YYYY-MM-DD
                    break
            
            if pub_date_raw == "未知日期":
                continue

            # 3. 檢查帳本中該日期的資料是否已存在，避免重複
            if pub_date_raw not in all_data:
                all_data[pub_date_raw] = {"東立": []}
            elif "東立" not in all_data[pub_date_raw]:
                all_data[pub_date_raw]["東立"] = []

            # 檢查這本書是否已經在該日期的名單裡了
            is_duplicate = any(b['title'] == title and b['volume'] == volume for b in all_data[pub_date_raw]["東立"])
            
            if not is_duplicate:
                print(f"✨ 發現歷史遺珠！補入日期 {pub_date_raw}：《{title}》")
                
                # 進入內頁抓取系列別 (略，保持之前的內頁抓取邏輯...)
                # 為了簡化展示，這裡示範補入基本資訊，您可以將之前的 detail 邏輯放入此處
                all_data[pub_date_raw]["東立"].append({
                    "title": title,
                    "author": author,
                    "volume": volume,
                    "series": "待更新", # 若要更完美，可在此處加入之前的內頁抓取邏輯
                    "cover": base_url + img_box.find("img")["src"] if img_box.find("img") else ""
                })
        
        time.sleep(1) # 優雅的間隔
    except Exception as e:
        print(f"❌ 巡邏第 {page_num} 頁時發生阻礙: {e}")

# 4. 重新整理帳本並存檔 (按日期排序)
sorted_data = dict(sorted(all_data.items(), reverse=True))

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(sorted_data, f, ensure_ascii=False, indent=2)

print(f"報告完畢！僕人已完成回溯任務，帳本已更新至最新狀態。")