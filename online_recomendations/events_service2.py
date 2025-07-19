from fastapi import FastAPI, HTTPException
import requests
from typing import List

features_store_url = "http://127.0.0.1:8010"
events_store_url = "http://127.0.0.1:8020"

class EventStore:
    def __init__(self, max_events_per_user=10):
        self.events = {}
        self.max_events_per_user = max_events_per_user

    def put(self, user_id: int, item_id: int):
        """
        Сохраняет событие
        """
        user_events = self.events.get(user_id, [])
        self.events[user_id] = [item_id] + user_events[:self.max_events_per_user]

    def get(self, user_id: int, k: int) -> List[int]:
        """
        Возвращает события для пользователя
        """
        user_events = self.events.get(user_id, [])[:k]
        return user_events

events_store = EventStore()

app = FastAPI(title="events")

@app.post("/put")
async def put(user_id: int, item_id: int):
    """
    Сохраняет событие для user_id, item_id
    """
    events_store.put(user_id, item_id)
    return {"result": "ok"}

@app.post("/get")
async def get(user_id: int, k: int = 10) -> dict:
    """
    Возвращает список последних k событий для пользователя user_id
    """
    events = events_store.get(user_id, k)
    return {"events": events}

@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 100) -> dict:
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    
    try:
        # Получаем последнее событие пользователя
        params = {"user_id": user_id, "k": 1}
        resp = requests.post(
            f"{events_store_url}/get", 
            headers=headers, 
            params=params
        )
        resp.raise_for_status()  # Проверка на ошибки
        events = resp.json().get("events", [])
        
        if not events:
            return {"recs": []}
            
        item_id = events[0]
        
        # Получаем список похожих объектов
        params = {"item_id": item_id, "k": k}
        resp = requests.post(
            f"{features_store_url}/similar_items", 
            headers=headers, 
            params=params
        )
        resp.raise_for_status()
        
        data = resp.json()
        item_similar_items = data.get("item_id_2", [])
        recs = item_similar_items[:k]
        
        return {"recs": recs}
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при работе с API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")
