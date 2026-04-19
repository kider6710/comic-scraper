import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime, timezone, timedelta

print("報告主人，僕人正準備執行深度搜索任務（已啟動替身使者防護機制）...")

# 1. 資安防護與替身使者設定
# 從環境變數讀取密碼，保護主人的資安
proxy_url = os.environ.get("PROXY_URL")

proxies = None
if proxy_url:
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    print("✨ 替身使者已連線，準備出發！")
else:
    print("⚠️ 尚未設定替身，僕人將以真面目出勤 (本機測試用)")

# 2. 鎖定台灣時區 (UTC+8) 與帳本
tw_tz = timezone(timedelta(hours=8))
target_date = datetime.now(tw_tz).strftime("%Y-%m-%d")
json_file = "data.json"

if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        all_data = json.load(f)
else:
    all_data = {}

# 3. 設定基礎網址與目標網址
clean_base_url = "https://www.tongli.com.tw"
url = "https://www.tongli.com.tw/webpagebooks.aspx?page=1&s=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 4. 取得列表頁 (掛載替身防護)
try:
    response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
except Exception as e:
    print(f"❌ 大門連線失敗，請檢查網路或替身使者狀態：{e}")
    exit()

img_boxes = soup.find_all("div", class_="pk_img")
txt_boxes = soup.find_all("div", class_="pk_txt")

tongli_list = []

# 5. 開始深度巡視
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
    full_detail_url = clean_base_url + "/" + detail_link if not detail_link.startswith("/") else clean_base_url + detail_link

    print(f"正在開門進入《{title}》的房間蒐集情報...")
    
    # 6. 進入內頁抓取 (務必也掛載替身防護，避免內頁被擋)
    try:
        detail_res = requests.get(full_detail_url, headers=headers, proxies=proxies, timeout=15)
        detail_res.encoding = 'utf-8'
        detail_soup = BeautifulSoup(detail_res.text, "html.parser")

        # 抓取封面網址
        cover_tag = img_box.find("img")
        cover_url = clean_base_url + cover_tag["src"] if cover_tag else ""

        # 抓取系列別
        series_tag = detail_soup.find("span", id="ContentPlaceHolder1_ReaderTxt")
        series_name = series_tag.text.strip() if series_tag else "無系列資訊"
    except Exception as e:
        print(f"⚠️ 進入《{title}》房間時發生錯誤: {e}")
        cover_url = ""
        series_name = "無系列資訊"

    # 7. 將資料整理裝箱
    tongli_list.append({
        "title": title,
        "author": author,
        "volume": volume,
        "series": series_name,
        "cover": cover_url
    })
    
    # 休息 0.5 秒，避免過度頻繁敲門
    time.sleep(0.5)

# 8. 寫入總帳本
if target_date not in all_data:
    all_data[target_date] = {}
    
all_data[target_date]["東立"] = tongli_list

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"報告完畢！主人，總共 {len(tongli_list)} 本漫畫的全彩深度情報，已完美存入 {target_date} 的帳本中！")