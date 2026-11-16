## Why

目前首頁、麻將房間頁與帳號頁各自維護 HTML 文件骨架、Tailwind 載入與部分視覺樣式，讓導覽與登入狀態的呈現容易分歧。將真正跨功能的版面結構移至 `core`，可讓後續頁面以一致的模板繼承方式重用，且不改變既有房間、帳號或首頁的功能流程。

## What Changes

- 在 `apps/core/templates/core/` 建立可被所有 app 以名稱引用的基底模板，集中 HTML 文件骨架、共用靜態資源載入與可覆寫的 `title`、額外資源、導覽列與內容區塊。
- 在 `apps/core/templates/core/` 建立共用 navbar partial，提供首頁、我的房間，以及依登入狀態顯示登入／註冊或使用者名稱與登出操作。
- 將跨頁共用的紙張背景、字型、色彩變數及 `.paper-card` 規則移至 `apps/core/static/core/css/base.css`；將首頁限定的樣式與輪播行為拆至 `core` 的首頁靜態資源。
- 將正式使用者流程的首頁、房間列表／詳情／建立頁與帳號登入／註冊／登出頁改為繼承基底模板，只保留各頁標題、內容及必要的頁面專屬資源。
- 保留 `core/greeting.html` 作為最小的課程示範頁，不要求它使用正式網站的 navbar 或基底模板。

## Non-Goals (optional)

- 不重新設計首頁或房間頁的視覺風格，也不變更既有網址、表單欄位、登入／登出流程或房間資料存取。
- 不將 Tailwind CDN 改為編譯流程，亦不新增前端套件、建置工具或外部相依。
- 不處理與本次模板重構無關的權限、資料查詢或測試覆蓋率問題。

## Impact

- Affected specs: none
- Affected code:
  - New: `apps/core/templates/core/base.html`、`apps/core/templates/core/_navbar.html`、`apps/core/static/core/css/base.css`，以及首頁專屬靜態資源。
  - Modified: `apps/core/templates/core/home.html`、`apps/majon/templates/majon/room_list.html`、`apps/majon/templates/majon/room_detail.html`、`apps/majon/templates/majon/room_form.html`、`templates/account/login.html`、`templates/account/signup.html`、`templates/account/logout.html`。
  - Removed: 麻將 app 與各模板中被 `core` 共用資源取代的重複樣式與文件骨架。
- Compatibility: 不改變既有使用者可用功能、URL 或表單提交行為；僅統一共用版面與靜態資源的擁有位置。
