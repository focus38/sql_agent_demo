import config
from typing import List


class AnalyticsHintService:
    def __init__(self): pass

    @staticmethod
    def create_hints(user_query: str) -> List[str]:
        # TODO тут можно дополнительно обрабатывать запрос пользователя и добавлять в контекст к LLM аналитическую информацию
        return config.ANALYTICAL_HINTS