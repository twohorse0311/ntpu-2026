import time

import redis

cache = redis.Redis(host="localhost", port=6379, decode_responses=True)
cache.ping()

cache_key = "demo:room-list"
started_at = time.perf_counter()
rooms = cache.get(cache_key)

if rooms is None:
    print("CACHE MISS：快取沒有資料，模擬查詢資料庫…")
    time.sleep(2)
    rooms = "週五練習室、系學會麻將房、期末專案討論室"
    cache.set(cache_key, rooms, ex=60)
else:
    print("CACHE HIT：直接從 Redis 讀取資料。")

elapsed = time.perf_counter() - started_at
print(f"Room 列表：{rooms}")
print(f"本次耗時：{elapsed:.2f} 秒")
print(f"快取剩餘秒數：{cache.ttl(cache_key)}")
