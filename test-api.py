import requests
import json

url = "https://api.open-meteo.com/v1/forecast"
params = {
    # 國立臺北大學三峽校區附近的座標
    "latitude": 24.9442,
    "longitude": 121.3717,
    # 要回傳目前的哪些天氣資料
    "current": "temperature_2m",
    # 將這個值改為 "celsius"，觀察 response 的差異
    "temperature_unit": "fahrenheit",
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()

data = response.json()
print("實際請求網址：", response.url)
print("--------------------------------")
print(json.dumps(data, indent=4))
print("--------------------------------")
print("目前資料：", data["current"])
print("資料單位：", data["current_units"])
