## Why

目前 `room_list.html` 與 `room_detail.html` 各自內嵌相同的專案自訂樣式，使模板同時承擔結構與外觀，重複樣式難以維護。將共用樣式移至 majon app 的靜態資源目錄，可讓後續調整只需修改一處，並預先建立 JavaScript 的固定位置。

## What Changes

- 在 `apps/majon/static/majon/css/` 建立共用樣式檔，集中紙張背景、色彩變數與 `.paper-card` 外觀。
- 調整 `apps/majon/templates/majon/room_list.html` 與 `apps/majon/templates/majon/room_detail.html`，使用 Django static 標籤載入共用樣式，移除重複的內嵌 `<style>`。
- 建立 `apps/majon/static/majon/js/` 並以版本控制保留檔維持目錄；目前沒有內嵌 JavaScript，因此不新增空白的 script 載入。
- 保留現有 Tailwind CDN 與頁面既有 class，避免在本次整理中改變版面或樣式系統。

## Non-Goals (optional)

- 不將 Tailwind CDN 改為本機編譯或調整其版本。
- 不重新設計房間列表、房間詳情或建立房間頁面。
- 不新增互動式 JavaScript，也不修改 majon 的資料、路由、視圖或模型。
- 不改動目前沒有專案自訂內嵌 CSS／JS 的 `room_form.html`。

## Impact

- Affected specs: none
- Affected code:
  - New: `apps/majon/static/majon/css/base.css`、`apps/majon/static/majon/js/.gitkeep`
  - Modified: `apps/majon/templates/majon/room_list.html`、`apps/majon/templates/majon/room_detail.html`
  - Removed: 兩個模板中的重複內嵌 `<style>` 區塊
- Compatibility: no capability-level observable behavior changes
