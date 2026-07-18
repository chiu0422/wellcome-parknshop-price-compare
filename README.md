# 惠康 vs 百佳 格價器

自動比較惠康(Wellcome)同百佳(ParknShop)兩間超市貨品價錢嘅工具,資料源自消委會「網上價格一覽通」開放數據。

## 網上開啟

部署GitHub Pages之後,喺瀏覽器開:

```
https://<你嘅github user>.github.io/<repo名>/格價器.html
```

開頁會自動讀取 `wellcome_parknshop_import.json` 同步最新價錢,唔使人手做嘢。

## 檔案講解

- **格價器.html** — 主工具,顯示兩間店嘅價錢比較、每單位價錢、優惠標籤、價格歷史
- **更新格價.py** — 下載消委會CSV,篩出惠康vs百佳兩邊都有賣嘅貨品,輸出做 `wellcome_parknshop_import.json`
- **wellcome_parknshop_import.json** — 最新一次嘅比對結果(由GitHub Actions自動生成)
- **.github/workflows/update-price.yml** — 排程任務,每日香港時間早上8點自動跑 `更新格價.py`,將新結果commit返入repo

## 手動即刻更新一次

唔使等到聽日,想即刻攞新資料:

1. 入repo,揀「Actions」頁
2. 左邊揀「每日更新格價」
3. 撳「Run workflow」→ 「Run workflow」
4. 等大概1分鐘,repo入面嘅JSON就會更新

## 本機執行(唔經GitHub)

```
python 更新格價.py
```

會喺同一資料夾生成新嘅JSON,再喺格價器.html撳「匯入」揀嗰個檔案就得。

---
資料來源:[消委會網上價格一覽通](https://online-price-watch.consumer.org.hk/opw/) 開放數據,每日更新。
