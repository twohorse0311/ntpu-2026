## Context

`config/settings/base.py` 已將 default cache 設為 Redis，預設 TTL 為 60 秒，但 `RoomListDataView` 每次仍建立 QuerySet、分頁並序列化 JSON。資料端點的輸出由登入者、搜尋字詞與頁碼決定，因此不可共用跨使用者快取。`RoomCreateView` 是目前唯一的房間建立流程；目前沒有房間刪除 view，但 Room 可以由 Django admin、未來程式或 ORM 刪除。

這是跨越資料端點、cache helper、模型生命週期與 app 啟動註冊的模式。Django 的 `redis` 客戶端已是專案依賴，足以捕捉 Redis 操作失敗並讓 API 採用不使用快取的正常查詢流程。

## Goals / Non-Goals

**Goals:**

- 快取登入者可見的房間列表 JSON，且絕不讓一位使用者讀到另一位使用者的資料。
- 在 Room 建立、更新、擁有者轉移或刪除的資料庫交易成功後，使受影響擁有者的列表快取立即過期。
- Redis 暫時無法使用時，維持房間列表 API 可從資料庫回應。

**Non-Goals:**

- 不新增房間刪除 UI、URL、權限或批次刪除功能。
- 不快取 HTML 列表頁、401 回應或錯誤回應。
- 不處理 `QuerySet.update()` 或其他繞過 model signals 的批次 ORM 寫入；此變更的支援邊界是 `Room.save()` 與 `Room.delete()`。
- 不把這個 helper 抽象為所有 app 共用的通用快取框架。

## Decisions

### Owner-scoped versioned cache keys

資料端點先完成登入權限檢查及 `q`／`page` 的基本正規化，再建立資料快取鍵：

```text
room-list:data:v{version}:owner:{owner_id}:query:{sha256(normalized_q)}:page:{normalized_page}
```

`version` 由 `room-list:version:owner:{owner_id}` 取得，初始值為 1 並以 `timeout=None` 儲存；資料回應以既有 default cache TTL（60 秒）儲存。雜湊搜尋字詞讓長字詞與 cache key 安全可預測，同時保留不同查詢的隔離。空清單也屬於可快取的成功回應。

不使用單一資料端點 URL 作為鍵，因為它會忽略登入者並可能洩漏房間資料；不採用列舉鍵後刪除，因為查詢與頁碼組合沒有上限。

### Commit-time room-list invalidation

`apps.majon` 啟動時註冊 Room signals。Room 建立或更新的 `post_save` 與 Room 刪除的 `post_delete` 均使用 `transaction.on_commit()` 推進受影響 owner 的版本號。因為版本成為資料快取鍵的一部分，下一個讀取會使用新版本而不會命中舊 JSON；舊 JSON 最多依 60 秒 TTL 自然淘汰。

若既有 Room 的 owner 被修改，pre-save 會記錄原 owner，post-save 在提交後同時失效舊 owner 和新 owner 的版本。這避免房間轉移後兩人看到過期清單。

不在 view 內呼叫 `cache.delete()`，因為它會遺漏 Django admin、未來 API 及直接 `Room.delete()`。不在資料庫交易中立即失效，因為 rollback 後會不必要地捨棄仍有效的快取。

### Cache failures fail open

對 Redis `get`、`set`、版本讀寫或遞增的 `RedisError`，列表 API SHALL 忽略快取並改以資料庫建立成功 JSON 回應；快取失效處理的 Redis 失敗 SHALL 不讓 Room 儲存或刪除失敗。這些錯誤應由 Django logging 記錄，方便維運發現快取服務不可用。

不以廣泛 `except Exception` 隱藏程式錯誤，避免資料序列化或權限錯誤被誤認為可忽略的快取故障。

## Implementation Contract

**Behavior**

- 同一 owner、相同已正規化查詢及頁碼的連續成功 API 請求 SHALL 在快取可用時重用完整 JSON payload，且回應內容與未快取結果相同。
- 不同 owner 的請求 SHALL 使用不同 cache namespace；一方的快取項目不得成為另一方的回應。
- Room 的建立、一般儲存、owner 轉移或刪除交易提交後，受影響 owner 的下一個列表請求 SHALL 不使用變更前的快取 payload。
- Redis 不可用時，API 與房間資料異動 SHALL 繼續成功執行，只是不使用快取。

**Interface / data shape**

- 對瀏覽器而言，`GET /majon/rooms/data/` 的成功 JSON 欄位、排序、搜尋及分頁語意維持不變。
- 快取 helper SHALL 提供取得 owner 版本、建立資料鍵、讀取／儲存 payload 與失效 owner 版本的明確函式；view 與 signals 不直接自行拼接 key。

**Failure modes**

- 快取讀寫失敗 SHALL 被記錄並退回資料庫回應；禁止將失敗或未完整 payload 寫入快取。
- transaction rollback SHALL 不推進版本號，也不讓尚未成功的寫入失效快取。

**Acceptance criteria**

- Django 測試證明相同 owner 的重複請求命中快取，不同 owner 不共用快取，搜尋和頁碼建立不同鍵。
- Django 測試證明建立及刪除 Room 後的下一個請求取得新資料，並且 rollback 不失效快取。
- Django 測試模擬 `RedisError`，確認 API 與 Room 寫入仍成功。

**Scope boundaries**

- 範圍包含 Room list API 的 payload 快取與 Room model signal 的版本失效。
- 範圍不包含快取設定本身、其他 app 的列表，或任何繞過 signals 的 bulk update 支援。

## Risks / Trade-offs

- [版本 key 遺失會使舊 payload 有機會被重新採用] → 版本 key 以無期限 timeout 儲存，資料 payload 仍只存 60 秒；Redis 淘汰策略須讓維運者監控。
- [signals 在 import 時未註冊] → 在 `MajonConfig.ready()` 明確匯入 signals，並以測試驗證資料異動失效。
- [Redis 暫時不可用] → 僅捕捉 `RedisError`，記錄後退回資料庫，不影響資料正確性。
- [bulk ORM 寫入繞過 signals] → 在規格範圍外；若日後採用 bulk 寫入，該流程必須顯式失效受影響 owner。

## Migration Plan

1. 建立 cache helper 和 signal 註冊，並以單元測試驗證 key 範圍、快取命中與 commit-time 失效。
2. 將資料端點改為透過 helper 讀寫成功 payload，並驗證既有 JSON 契約未改變。
3. 部署後監控 Redis 連線錯誤與 API 延遲；若需要回復，移除 view 的 cache helper 呼叫與 signal 註冊即可，資料模型與 JSON API 不需要遷移。

## Open Questions

- 無；現有 60 秒 TTL、owner 範圍隔離及 versioned invalidation 已在本設計中固定。
