## Summary

快取目前已由 Django Redis backend 設定，但房間列表 API 每次請求仍直接查詢資料庫，且房間資料異動後沒有對應的失效機制。本變更為使用者專屬的房間列表資料加入可安全失效的快取，讓快取命中不犧牲建立、更新或刪除後的資料正確性。

## Motivation

`GET /majon/rooms/data/` 的結果依登入使用者、搜尋字詞和頁碼而異。若以單一或未分隔使用者的快取鍵快取，可能造成資料外洩；若僅依 TTL 到期，建立或刪除房間後最多會維持 60 秒的過期列表。因此需要以擁有者範圍隔離的快取鍵，並在資料庫交易成功後立即使該使用者的列表快取失效。

## Proposed Solution

- 為房間列表 API 加入使用者、已正規化搜尋條件與頁碼範圍的 Redis 快取鍵。
- 用每位擁有者的快取版本號作為快取鍵的一部分；房間變更時只需推進版本號，毋須列舉所有搜尋與頁碼組合。
- 以 Room model 的儲存與刪除事件處理失效，並延後至資料庫交易成功提交後執行，使建立、管理後台、未來 API 和任何 `Room.delete()` 的資料異動都有一致行為。
- 保留 `CACHES["default"]` 的 60 秒 TTL；僅快取資料端點的成功 JSON 結果，不快取認證失敗或錯誤回應。

## Non-Goals (optional)

- 不新增房間刪除的 UI、URL 或權限流程。
- 不對其他既有列表頁加入快取；它們可在未來各自變更時採用相同模式。
- 不建立需要記錄每個搜尋字詞與每個頁碼的逐鍵刪除清單。

## Alternatives Considered (optional)

- 只使用 60 秒 TTL：實作較少，但建立或刪除後會讓使用者看到過期列表。
- 每次變更時呼叫 `cache.delete_many()`：無法可靠列舉曾使用的任意搜尋與頁碼鍵，且維護成本高。

## Impact

- Affected specs: `room-list-api`（modified）
- Affected code:
  - Modified: `apps/majon/views.py`, `apps/majon/apps.py`, `apps/majon/tests.py`
  - New: `apps/majon/cache.py`, `apps/majon/signals.py`
  - Removed: none
