<!--
Each task description MUST state:
- the behavior or contract being delivered (what is observably true when the
  task is complete), and
- the verification target that proves completion (test, CLI invocation,
  analyzer check, manual assertion, or content review).

File paths are supporting context for locating the work, never the task
itself. "Edit file X" is not a valid task — it is missing both behavior and
verification.
-->

## 1. 建立可重用的靜態資源

- [x] 1.1 在 `apps/majon/static/majon/css/base.css` 提供房間列表與詳情共用的紙張背景、色彩變數及 `.paper-card` 樣式，並以 `apps/majon/static/majon/js/.gitkeep` 保留未來 JavaScript 目錄；以 `.venv/bin/python manage.py findstatic majon/css/base.css` 找到樣式檔，並以檔案檢查確認 JS 目錄受版本控制為完成條件。

## 2. 讓模板載入共用樣式

- [x] 2.1 [after: 1.1] 修改 `apps/majon/templates/majon/room_list.html` 與 `apps/majon/templates/majon/room_detail.html`，使兩頁透過 Django static 標籤載入 `majon/css/base.css`，且不再保留重複的內嵌 `<style>`；以模板內容檢查確認兩頁各有 static 載入與 stylesheet link、沒有內嵌 style 區塊為完成條件。

## 3. 驗證不影響既有頁面

- [x] 3.1 [after: 2.1] 驗證靜態檔與模板設定可由 Django 載入，且不改變既有路由、視圖、資料模型、Tailwind CDN 或 `room_form.html`；執行 `.venv/bin/python manage.py check`、`.venv/bin/python manage.py findstatic majon/css/base.css` 與既有 majon 測試為完成條件。
