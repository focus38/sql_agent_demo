from typing import Dict, List


class SqlGeneratorService:
    def __init__(self): pass

    def _format_schema(self, db_schema: Dict[str, List[str]]) -> str:
        schema_str = ""
        for table, columns in db_schema.items():
            schema_str += f"Таблица: {table}\n"
            schema_str += f"  Поля: {', '.join(columns)}\n\n"
        return schema_str

    def _format_hints(self, hints: List[str]) -> str:
        return "\n".join(hints)

    def generate_sql_prompt(self, db_schema: str, hints: List[str], user_query: str) -> None | str:
        formatted_hints = self._format_hints(hints)
        #formatted_db_schema = self._format_schema(db_schema)

        return SqlGeneratorService.create_prompt(db_schema, formatted_hints, user_query)

    @staticmethod
    def create_prompt(db_schema: str, hints: str, user_query: str) -> str:
        return f"""
        <user_query>
        {user_query}
        </user_query>

        АНАЛИТИЧЕСКИЕ ПОДСКАЗКИ ОТ ПРОФЕССИОНЕЛЬНОГО АНАЛИТИКА:
        <analytical_hints>
        {hints}
        </analytical_hints>
        
        СХЕМА ДАННЫХ:
        <db_schemas>
        {db_schema}
        </db_schemas>
        
        ЗАДАЧА:
        - Предоставить только SQL-запрос, который базируется ИСКЛЮЧИТЕЛЬНО на схеме данных из db_schemas и отвечает на вопрос пользователя.

        ТРЕБОВАНИЯ К РЕЗУЛЬТАТУ:
        - Только команда SELECT.
        - ОБЯЗАТЕЛЬНО названия полей должны быть обернуты в двойные кавычки.
        - ОБЯЗАТЕЛЬНО названия таблиц должны быть обернуты в двойные кавычки.
        - НИКОГДА не упоминай в ответе клиенту названия внутренних тегов, типа user_query, analytical_hints.
        - Если в ORDER BY используется алиас выражения из SELECT (agg_alias), то оберни запрос в подзапрос с алиасом s и сортируй так: ORDER BY s.agg_alias.
        - Не квалифицируй алиасы выражений алиасами таблиц (нельзя c.agg_alias).
        - Работай только с базами данных из схемы данных
        - НИКОГДА НЕ ДОБАВЛЯЙ никаких комментариев, пояснений, вводных фраз в SQL запрос.
        - Не используй <think>, </think>, ```sql или другие теги.
        - Верни только одну строку с SQL, заканчивающуюся на ';'.
SQL ЗАПРОС:
""".strip()
