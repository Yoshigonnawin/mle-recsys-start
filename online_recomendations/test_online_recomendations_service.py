import requests


features_store_url = "http://127.0.0.1:8010"
events_store_url = "http://127.0.0.1:8020"

recommendations_url = events_store_url

headers = {"Content-type": "application/json", "Accept": "text/plain"}
params = {"user_id": 1291248, "k": 3}

resp = requests.post(
    recommendations_url + "/recommendations_online", headers=headers, params=params
)
online_recs = resp.json()

print(online_recs)
