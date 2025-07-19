from fastapi import FastAPI
import requests


features_store_url = "http://127.0.0.1:8010"
events_store_url = "http://127.0.0.1:8020"


class EventStore:
    def __init__(self, max_events_per_user=10):
        self.events = {}
        self.max_events_per_user = max_events_per_user

    def put(self, user_id, item_id):
        """
        Сохраняет событие
        """

        user_events = self.events.get(user_id, [])
        self.events[user_id] = [item_id] + user_events[: self.max_events_per_user]

    def get(self, user_id, k):
        """
        Возвращает события для пользователя
        """
        user_events = self.events.get(user_id, [])[:k]

        return user_events


events_store = EventStore()

# создаём приложение FastAPI
app = FastAPI(title="events")


@app.post("/put")
async def put(user_id: int, item_id: int):
    """
    Сохраняет событие для user_id, item_id
    """

    events_store.put(user_id, item_id)

    return {"result": "ok"}


@app.post("/get")
async def get(user_id: int, k: int = 10):
    """
    Возвращает список последних k событий для пользователя user_id
    """

    events = events_store.get(user_id, k)

    return {"events": events}


@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 100):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """

    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    # получаем последнее событие пользователя
    params = {"user_id": user_id, "k": 1}
    resp = requests.post(events_store_url + "/get", headers=headers, params=params)
    events = resp.json()
    events = events["events"]

    # получаем список похожих объектов
    if len(events) > 0:
        item_id = events[0]
        params = {"item_id": item_id, "k": k}
        resp = requests.post(
            features_store_url + "/similar_items", headers=headers, params=params
        )
        if resp.status_code == 200:
            item_similar_items = resp.json().get("item_id_2",[])
        else:
            item_similar_items = []
        recs = item_similar_items[:k]
    else:
        recs = []

    return {"recs": recs}
