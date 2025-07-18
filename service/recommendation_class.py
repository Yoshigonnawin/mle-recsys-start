import logging as logger
import pandas as pd


class Recommendations:
    def __init__(self):
        self._recs = {"personal": None, "default": None}
        self._stats = {
            "request_personal_count": 0,
            "request_default_count": 0,
        }

    def load(self, type, path, **kwargs):
        """
        Загружает рекомендации из файла
        """

        logger.info(f"Loading recommendations, type: {type}")
        self._recs[type] = pd.read_parquet(path, **kwargs)
        if type == "personal":
            self._recs[type] = self._recs[type].set_index("user_id")
        logger.info(f"Loaded")

    def get(self, user_id: int, k: int = 100):
        """
        Возвращает список рекомендаций для пользователя
        """
        try:
            recs = self._recs["personal"].loc[user_id]
            recs = recs["book_id"].to_list()[:k]
            self._stats["request_personal_count"] += 1
        except KeyError:
            recs = self._recs["default"]
            recs = recs["book_id"].to_list()[:k]
            self._stats["request_default_count"] += 1
        except:
            logger.error("No recommendations found")
            recs = []

        return recs

    def stats(self):
        logger.info("Stats for recommendations")
        for name, value in self._stats.items():
            logger.info(f"{name:<30} {value} ")


if __name__ == "__main__":
    rec_store = Recommendations()

    rec_store.load(
        "personal",
        r"/home/yoh/project/mle-recsys-start/events.par",
        columns=["user_id", "book_id"],
    )
    rec_store.load(
        "default",
        r"/home/yoh/project/mle-recsys-start/events.par",
        columns=["book_id"],
    )

    rec_store.get(user_id=100, k=5)
    print(rec_store.get(user_id=100, k=5))
