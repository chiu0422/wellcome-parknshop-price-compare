"""
消委會格價自動更新工具
======================
自動下載「網上價格一覽通」開放數據,篩出惠康 vs 百佳兩間店都有賣嘅貨品,
輸出做 wellcome_parknshop_import.json,拎去個「格價器.html」度撳「匯入」就得。

用法:
  1. 確保部電腦有裝 Python 3 (Windows 可以喺 Microsoft Store 裝)
  2. 雙擊呢個檔案,或者喺命令提示字元 (cmd) 打:
         python 更新格價.py
  3. 完成之後,同一個資料夾會有一個 wellcome_parknshop_import.json
  4. 開返個格價器.html,撳「匯入 JSON 檔案」揀呢個新檔案就會自動更新價錢

如果想日日自動跑(唔使自己撳):
  - Windows: 用「工作排程器」(Task Scheduler) 新增一個每日任務,
    「動作」揀執行 python.exe,「引數」填呢個 .py 檔案嘅完整路徑
"""

import csv
import io
import json
import re
import sys
import urllib.request
from datetime import date

CSV_URL = "https://online-price-watch.consumer.org.hk/opw/opendata/pricewatch_zh-Hant.csv"
OUTPUT_FILE = "wellcome_parknshop_import.json"

UNIT_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(公斤|毫升|公升|公克|克|升|kg|ml|g|L)", re.IGNORECASE)
UNIT_MAP = {
    "公克": "g", "克": "g", "公斤": "kg",
    "毫升": "ml", "公升": "L", "升": "L",
    "kg": "kg", "ml": "ml", "g": "g", "L": "L",
}


def extract_qty_unit(name):
    m = UNIT_PATTERN.search(name)
    if m:
        qty = float(m.group(1))
        unit = UNIT_MAP.get(m.group(2), m.group(2))
        return qty, unit
    return 1, "件"


def download_csv(url):
    print(f"下載緊資料... {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    # CSV 有 UTF-8 BOM
    return raw.decode("utf-8-sig")


def main():
    try:
        text = download_csv(CSV_URL)
    except Exception as e:
        print(f"下載失敗: {e}")
        print("可以嘗試自己喺瀏覽器開返個網址,手動下載個 CSV,")
        print("再改呢個程式,將 CSV_URL 改做本地檔案路徑讀取。")
        sys.exit(1)

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"共讀到 {len(rows)} 行資料")

    wc = {}
    ps = {}
    for r in rows:
        key = (r.get("品牌", "").strip(), r.get("貨品名稱", "").strip())
        if r.get("超市代號") == "WELLCOME":
            wc[key] = r
        elif r.get("超市代號") == "PARKNSHOP":
            ps[key] = r

    common_keys = set(wc.keys()) & set(ps.keys())
    print(f"兩間店都有賣嘅貨品: {len(common_keys)} 件")

    today = date.today().isoformat()
    products = []
    for brand, name in common_keys:
        wc_row = wc[(brand, name)]
        ps_row = ps[(brand, name)]
        try:
            wc_price = float(wc_row["價格"])
            ps_price = float(ps_row["價格"])
        except (ValueError, TypeError):
            continue

        qty, unit = extract_qty_unit(name)
        full_name = f"{brand} {name}".strip()

        products.append({
            "name": full_name,
            "qty": qty,
            "unit": unit,
            "wc": wc_price,
            "ps": ps_price,
            "wcPromo": (wc_row.get("優惠") or "").strip(),
            "psPromo": (ps_row.get("優惠") or "").strip(),
            "history": [],
            "addedAt": today,
        })

    products.sort(key=lambda p: p["name"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"完成!已經寫低 {len(products)} 件貨品去 {OUTPUT_FILE}")
    print("開返格價器.html,撳「匯入 JSON 檔案」揀呢個檔案就得。")


if __name__ == "__main__":
    main()
