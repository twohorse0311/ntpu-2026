## Context

目前 Django 已啟用 app template discovery，且全域 `templates/` 目錄用於 django-allauth 覆寫模板；因此各 app 與帳號頁都可透過 `core/base.html` 共用同一個基底模板。房間列表與詳情頁目前載入 `majon/css/base.css`，首頁在模板內嵌入相同紙張視覺的部分規則，其餘正式頁面則各自載入 Tailwind CDN。此次重構跨越 `core`、`majon` 與全域 account 模板，先確立資源擁有者與區塊邊界，可避免只消除部分重複後再次分歧。

## Goals / Non-Goals

目標：

- 讓 `core` 擁有全站共用的文件骨架、navbar 與基礎樣式。
- 讓正式使用者頁面以一致的 Django 模板繼承規則表達頁面差異。
- 保留每個頁面的標題、內容、表單提交路徑及既有功能。
- 將首頁專屬 CSS 與 JavaScript 與跨頁資源分開，避免共用檔案載入不相關行為。

非目標：

- 不改變 URL、view、context 資料、allauth 設定、表單欄位或權限規則。
- 不納入教學用 `core/greeting.html`。
- 不導入 Tailwind 編譯、前端框架或資產打包工具。

## Decisions

### 以 `core/base.html` 作為跨 app 的基底模板

基底模板位於 `apps/core/templates/core/base.html`，子模板以 `{% extends "core/base.html" %}` 引用。它負責 `<!doctype html>`、語言與 viewport meta、Tailwind CDN、`{% load static %}`、`core/css/base.css`，並定義 `title`、`extra_head`、`navbar`、`content` 與 `extra_js` 區塊。

這比將基底模板放在全域 `templates/` 更符合共用網站殼屬於 `core` 的責任，同時不影響 allauth 在全域目錄覆寫其頁面模板的既有慣例。

### 將 navbar 做成可替換的 partial

`apps/core/templates/core/_navbar.html` 透過 `navbar` 區塊被基底模板 include。它連到 `core:home` 與 `majon:room-list`，匿名使用者看到登入與註冊連結，已登入使用者看到 `user.profile.display_name|default:user.username` 與以 POST 送出的登出表單。所有正式頁面預設使用此 navbar；子模板如有未來的版面需求，能覆寫空白或替代內容，但本次不建立第二套 navbar。

替代方案是在每個子模板 include partial；這會保留重複的版面定位與使用條件，無法保證文件骨架與導覽列一併一致，故不採用。

### 依資源責任拆分 CSS 與 JavaScript

跨頁的字型、顏色變數、背景與 `.paper-card` 搬到 `apps/core/static/core/css/base.css`。首頁目前只為功能介紹與輪播存在的樣式與 JavaScript，移入 `apps/core/static/core/css/home.css` 與 `apps/core/static/core/js/home.js`，並由首頁透過 `extra_head` 與 `extra_js` 載入。`majon/css/base.css` 在其內容已被遷移後移除，避免兩份共用設計規則分別演化。

不把首頁的完整樣式放入 `base.css`，因為房間與帳號頁不需要輪播、手機模型或首頁按鈕規則。

### 以內容區塊保留頁面特有的佈局

`majon` 模板與 account 模板只覆寫 `title` 與 `content`，並在需要時覆寫額外資源區塊。房間列表原本在頁首顯示的登入狀態控制，改由 navbar 提供；房間數量、搜尋與房間清單仍保留在列表內容。首頁保留 Hero、功能、輪播與頁尾，但由基底模板提供文件外殼與導覽列。

## Implementation Contract

範圍內：`apps/core` 共用模板與靜態資源、`apps/majon` 房間模板與重複基礎 CSS、全域 account 模板。

範圍外：`apps/core/templates/core/greeting.html`、URLconf、views、models、forms、settings、資料庫與第三方相依。

完成後，首頁、房間列表／詳情／建立頁及登入／註冊／登出頁都應以 `core/base.html` 為父模板。每一頁可載入且保留原本對應的標題、內容與連結／表單行為；navbar 的首頁與房間連結可反向解析，登入狀態的連結或登出 POST 表單正確呈現。未登入時不可顯示使用者名稱或登出操作，登入時不可顯示登入與註冊連結。

此次為內部模板與資產重構，能力層級可觀察功能不變；使用者仍透過原網址完成瀏覽首頁、進入房間、搜尋／建立房間與登入／註冊／登出。

實作前須檢查並保留工作目錄中既有、未追蹤或未提交的 `majon` 模板與靜態檔變更；不得以舊版本覆蓋它們。

## Risks / Trade-offs

- [CSS 搬移後有頁面漏載或視覺退化] -> 在模板渲染檢查與既有開發伺服器中逐頁確認共用背景、字型與 `.paper-card` 均存在。
- [navbar 依 `user.profile` 存取時資料不完整] -> 沿用目前房間列表已採用的 `user.profile.display_name|default:user.username` 表達式，並以匿名與已登入兩種情境驗證渲染。
- [重構覆蓋使用者進行中的 `majon` 變更] -> 先檢視 Git diff 與檔案內容，將共用化建構在目前版本上，限制修改至本提案列出的重複區塊。
- [帳號頁與 app 模板搜尋規則混淆] -> 以 Django 現有 `APP_DIRS=True` 和全域 `DIRS` 設定驗證 `core/base.html` 可被 account 模板解析。

## Migration Plan

1. 先新增 `core` 的基底模板、navbar 與靜態檔，不移除舊資源。
2. 逐頁改為繼承基底模板，從首頁與房間頁開始，再處理 account 模板；每批後以 Django 檢查與目標頁面測試確認渲染。
3. 確認所有正式頁面已改用 `core` 資源後，移除已無引用的 `majon/css/base.css` 與模板內重複規則。
4. 若發現渲染或樣式回歸，暫時恢復受影響頁面對既有資源的引用，保留新的 `core` 資源，定位缺少的共用規則後再完成遷移。

## Open Questions

無。現有首頁與房間頁的文字、路由名稱及登入狀態行為已足以定義本次共用 navbar；視覺重設計留待獨立變更處理。
