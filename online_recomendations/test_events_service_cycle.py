import requests

events_store_url = "http://127.0.0.1:8020"

headers = {"Content-type": "application/json", "Accept": "text/plain"}

user_id = 1127794

for i in [18734992, 18734992, 7785, 4731479]:
    params = {"user_id": user_id, "item_id": i}

    resp = requests.post(events_store_url + "/put", headers=headers, params=params)
    if resp.status_code == 200:
        result = resp.json()
    else:
        result = None
        print(f"status code: {resp.status_code}")

    print(result)

resp = requests.post(
    events_store_url + "/get", headers=headers, params={"user_id": user_id, "k": 3}
)
print(resp.json())
