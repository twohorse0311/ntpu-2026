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

## 1. 建立 core 共用網站殼與資源

- [x] 1.1 在 `apps/core/templates/core/base.html` 與 `apps/core/templates/core/_navbar.html` 建立可跨 app 繼承的文件骨架與「可替換的 partial」預設導覽列；匿名與已登入情境分別呈現正確的帳號操作，且首頁與房間連結可由 Django 反向解析。以 Django template render 測試或開發伺服器手動確認兩種登入狀態的 navbar 輸出。[after: none]
- [x] 1.2 依資源責任在 `apps/core/static/core/css/base.css` 建立跨頁共用的紙張背景、字型、色彩變數與 `.paper-card` 規則；基底模板載入後，房間頁與帳號頁都能使用這些樣式而不依賴 `majon/css/base.css`。以瀏覽器檢視房間列表與登入頁確認背景、字型與卡片樣式。[after: 1.1]
- [x] 1.3 依資源責任將首頁限定的 CSS 與輪播 JavaScript 自 `apps/core/templates/core/home.html` 移至 `apps/core/static/core/css/home.css` 與 `apps/core/static/core/js/home.js`，並僅由首頁額外載入；首頁輪播與「開始使用」導向維持可用。以桌面與窄螢幕手動檢查首頁互動與版面。[after: 1.1]

## 2. 將正式頁面遷移至模板繼承

- [x] 2.1 將 `apps/core/templates/core/home.html` 改為繼承 `core/base.html`，以內容區塊保留原有首頁標題、Hero、功能介紹、頁尾與首頁專屬資源；以首頁請求確認 HTTP 成功、頁面標題正確且 navbar 顯示。[after: 1.1, 1.3]
- [x] 2.2 將 `apps/majon/templates/majon/room_list.html`、`room_detail.html` 與 `room_form.html` 改為繼承 `core/base.html`，以內容區塊保留搜尋、房間資訊、建立房間表單、回列表連結與原有 URL／POST 行為；以匿名及登入使用者瀏覽列表、詳情與建立頁確認內容及 navbar 正確。[after: 1.1, 1.2]
- [x] 2.3 將 `templates/account/login.html`、`signup.html` 與 `logout.html` 改為繼承 `core/base.html`，以內容區塊保留 allauth 表單 action、CSRF token、登入／註冊互鏈與登出 POST 操作；以開發伺服器請求三個帳號頁並提交安全的表單流程確認模板可渲染。[after: 1.1, 1.2]

## 3. 移除重複資源並驗證重構

- [ ] 3.1 在所有正式頁面完成遷移後，移除不再被引用的 `apps/majon/static/majon/css/base.css` 與模板內重複的文件骨架／共用基礎規則，不修改 `apps/core/templates/core/greeting.html`；以 `rg` 確認正式頁面不再引用舊共用 CSS，並檢視 Git diff 確認既有未提交的麻將模板變更未被覆蓋。[after: 2.1, 2.2, 2.3]
- [ ] 3.2 執行 `uv run python manage.py check`，並在開發環境逐一確認首頁、房間列表／詳情／建立頁及登入／註冊／登出頁可渲染、導覽與既有連結／表單流程不回歸；記錄任何因環境設定而無法執行的驗證結果。[after: 3.1]
