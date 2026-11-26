## 1. 快取 helper 與資料端點

- [x] 1.1 實作「Owner-scoped versioned cache keys」、「Owner-scoped cached room-list responses」與「Cache outage fallback」：在 `apps/majon/cache.py` 封裝 per-owner version key、以 owner／正規化 query／正規化 page 建立資料 key、成功 payload 的讀寫及 `RedisError` fail-open；在 `apps/majon/views.py` 讓 `RoomListDataView` 僅快取成功 JSON 並保留既有 API 契約。驗證方式：在 `apps/majon/tests.py` 通過同 owner 重複請求命中快取、不同 owner／query／page 不共用 payload，以及模擬 Redis 讀寫失敗仍從資料庫回傳正確 JSON 的測試。

## 2. 交易提交後的失效

- [x] 2.1 [after: 1.1] 實作「Commit-time room-list invalidation」與「Commit-time room-list cache invalidation」：新增 `apps/majon/signals.py` 並由 `MajonConfig.ready()` 註冊，讓 Room create、save、owner transfer 與 delete 只在 transaction commit 後推進受影響 owner 的版本；Redis 失效錯誤僅記錄且不可中斷寫入。驗證方式：在 `apps/majon/tests.py` 通過建立、刪除、owner transfer 後下一次列表讀取不使用舊 payload、rollback 不推進版本，以及失效 RedisError 不阻止 Room 寫入的測試。

## 3. 整合驗證

- [x] 3.1 [after: 1.1, 2.1] 驗證快取不改變既有 `room-list-api` 的可觀察契約：執行 `uv run python manage.py test apps.majon` 與 `uv run python manage.py check`，並檢查成功回應仍有相同欄位、排序、搜尋、分頁及 owner 隔離。驗證方式：命令均通過，且新增 cache 測試與既有 RoomListApiTests 同時通過。
