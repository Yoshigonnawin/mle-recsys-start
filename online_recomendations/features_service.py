import logging
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI
from pathlib import Path

logger = logging.getLogger("uvicorn.error")


class SimilarItems:
    def __init__(self):
        self._similar_items = None

    def load(self, path, **kwargs):
        """
        Загружаем данные из файла
        """

        logger.info(f"Loading data, type: {type}")
        similar_items = pd.read_parquet(path)
        self._similar_items = similar_items[
            kwargs.get("columns", ["item_id_1", "item_id_2", "score"])
        ]
        logger.info(f"Loaded")

    def get(self, item_id: int, k: int = 10):
        """
        Возвращает список похожих объектов
        """
        try:
            i2i = self._similar_items.query(f"item_id_1 == {str(item_id)}").head(k)
            i2i = {
                "item_id_2": i2i["item_id_2"].to_list(),
                "score": i2i["score"].to_list(),
            }
        except KeyError:
            logger.error("No recommendations found")
            i2i = {"item_id_2": [], "score": {}}

        return i2i


sim_items_store = SimilarItems()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    sim_items_store.load(
        path=Path(__file__).parent.parent / "similar_items.parquet",
        columns=["item_id_1", "item_id_2", "score"],
    )
    logger.info("Ready!")
    # код ниже выполнится только один раз при остановке сервиса
    yield


# создаём приложение FastAPI
app = FastAPI(title="features", lifespan=lifespan)


@app.post("/similar_items")
async def recommendations(item_id: int, k: int = 10):
    """
    Возвращает список похожих объектов длиной k для item_id
    """

    i2i = sim_items_store.get(item_id, k)

    return i2i
