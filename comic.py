import requests
from bs4 import BeautifulSoup
import json
import os
import time

print("報告主人，僕人正準備執行深度搜索任務，潛入內頁為您奪取系列別與封面...")

# 1. 鎖定測試日期與帳本
target_date = "2026-04-01"
json_file = "data.json"

if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        all_data = json.load(f)
else:
    all_data = {}

# 2. 設定基礎網址與目標網址
clean_base_url = "https://www.tongli.com.tw" # 不帶結尾斜線，方便與圖片路徑拼接
url = "https://www.tongli.com.tw/webpagebooks.aspx?page=1&s=1"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# 3. 取得列表頁
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, "html.parser")

img_boxes = soup.find_all("div", class_="pk_img")
txt_boxes = soup.find_all("div", class_="pk_txt")

tongli_list = []

# 4. 開始同時巡視圖片盒與文字盒
for img_box, txt_box in zip(img_boxes, txt_boxes):
    title_tag = txt_box.find("em")
    title = title_tag.text if title_tag else "未知書名"
    
    spans = txt_box.find_all("span")
    author = spans[0].text if len(spans) > 0 else "未知作者"
    volume = spans[1].text if len(spans) > 1 else ""

    # 尋找進入內頁的金鑰匙
    a_tag = img_box.find("a")
    if not a_tag:
        continue
        
    detail_link = a_tag["href"]
    # 組合出完整的內頁網址
    full_detail_url = clean_base_url + "/" + detail_link if not detail_link.startswith("/") else clean_base_url + detail_link

    print(f"正在開門進入《{title}》的房間蒐集情報...")
    
    # 5. 進入內頁抓取
    try:
        detail_res = requests.get(full_detail_url, headers=headers)
        detail_res.encoding = 'utf-8'
        detail_soup = BeautifulSoup(detail_res.text, "html.parser")

        # 抓取封面網址
        cover_tag = img_box.find("img")
        cover_url = clean_base_url + cover_tag["src"] if cover_tag else ""

        # 抓取系列別
        series_tag = detail_soup.find("span", id="ContentPlaceHolder1_ReaderTxt")
        series_name = series_tag.text.strip() if series_tag else "無系列資訊"
    except Exception as e:
        print(f"驚動了警衛！進入《{title}》房間時發生錯誤: {e}")
        cover_url = ""
        series_name = "無系列資訊"

    # 6. 將資料整理裝箱
    tongli_list.append({
        "title": title,
        "author": author,
        "volume": volume,
        "series": series_name,
        "cover": cover_url
    })
    
    # 貼心提醒：為了不被警衛發現，每開一扇門稍微休息 0.5 秒
    time.sleep(0.5)

# 7. 寫入總帳本
if target_date not in all_data:
    all_data[target_date] = {}
    
all_data[target_date]["東立"] = tongli_list

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"報告完畢！主人，總共 {len(tongli_list)} 本漫畫的全彩深度情報，已完美存入 {target_date} 的帳本中！")