## 1. 房間資料契約

- [x] 1.1 實作「JSON 分頁端點與頁面殼層分離」、「Authenticated room list data endpoint」與「Dynamic list pagination contract」：在 `apps/majon/views.py` 與 `apps/majon/urls.py` 提供登入者專用的 `GET /majon/rooms/data/`，回傳每頁 10 筆、名稱搜尋、擁有者隔離、頁碼正規化與指定的 room/pagination JSON 欄位；未登入請求回傳 JSON 401。驗證方式：在 `apps/majon/tests.py` 新增並通過涵蓋登入、資料隔離、搜尋、回應欄位、每頁 10 筆及邊界頁碼的 Django 測試。
- [x] 1.2 [after: 1.1] 實作「動態資料列表的共通規範」的房間頁套用：調整 `apps/majon/templates/majon/room_list.html`，使初始 HTML 成為搜尋、狀態、列表及分頁控制的畫面殼層，而不是伺服器端輸出房間資料集合。驗證方式：以已登入使用者開啟 `/majon/rooms/`，確認 HTML 不含完整房間卡片資料且可供 JavaScript 初始化。

## 2. AJAX 列表互動

- [x] 2.1 [after: 1.1, 1.2] 實作「AJAX 搜尋與分頁的請求協調」與「Dynamic list data retrieval」：在 `apps/majon/static/majon/js/` 新增房間列表腳本，初次載入、表單提交、300 毫秒搜尋等待和分頁點擊均向資料端點請求；用 `AbortController` 與最新請求識別避免過期回應更新畫面，並以 `total_count` 顯示總數。驗證方式：手動快速輸入不同搜尋字詞及快速切換頁碼，確認最後輸入／頁碼的結果保持顯示且網址不發生完整文件重新載入。
- [x] 2.2 [after: 2.1] 實作「載入、空結果與錯誤狀態」與「Dynamic list request states」：首次載入顯示具有無障礙狀態的骨架，更新時保留既有資料並顯示更新中，空回應顯示空結果，失敗時提供重試且保留上次成功資料；取消的請求不可顯示錯誤。驗證方式：在瀏覽器檢查初次載入、搜尋無結果、後續請求失敗與重新載入，以及螢幕閱讀器可讀取的狀態區域。

## 3. 整合驗證

- [x] 3.1 [after: 1.1, 2.2] 驗證「Room list search and pagination」與「Room list response shape」在頁面和資料端點的一致性：執行房間 app 的測試與 `python manage.py check`，並以超過 10 筆屬於同一使用者的房間手動確認搜尋、上一頁／下一頁、總數與詳細頁連結。驗證方式：上述測試及檢查皆通過，且人工驗證的顯示項目與 API `items` 對應。
