from typing import  List


class SqlGeneratorService:
    def __init__(self): pass

    @staticmethod
    def _format_hints(hints: List[str]) -> str:
        return "\n".join(hints)

    def generate_sql_prompt(self, db_schema: str, hints: List[str], user_query: str) -> None | str:
        formatted_hints = self._format_hints(hints)

        return SqlGeneratorService.create_prompt(db_schema, formatted_hints, user_query)

    @staticmethod
    def create_prompt(db_schema: str, hints: str, user_query: str) -> str:
        return f"""Опирайся исключительно на предоставленную схему данных из db_schemas.
        Сгенерируй ровно один SQL-запрос для PostgreSQL, который отвечает на вопрос пользователя.
        
        ВХОД
        
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
        
        ПРАВИЛА ГЕНЕРАЦИИ (ОБЯЗАТЕЛЬНО)
        Только одна команда SELECT в ответе (допустимы подзапросы/WITH, но это всё один SQL-стейтмент).
        НЕ используй комментарии и пояснения к фрагментам SQL запроса.
        
        Кавычки: все имена таблиц и колонок — в двойных кавычках, с точным регистром как в схеме. Если есть схема, квалифицируй как "schema"."table".
        Только из предоставленной схемы: не используй таблицы/поля, отсутствующие в <db_schemas>.
        
        JOIN: всегда указывай явный JOIN ... ON, не используй USING. Разрешены INNER/LEFT по смыслу.
        
        Колонки и алиасы:
        Не используй SELECT *. Указывай явные поля/выражения.
        Все алиасы выражений в SELECT тоже в двойных кавычках, например: COUNT(*) AS "orders_cnt".
        Запрещено квалифицировать алиасы выражений алиасами таблиц (нельзя t."orders_cnt").

        GROUP BY / агрегаты: при наличии агрегатов укажи корректный GROUP BY (не используй порядковые номера).
        
        ORDER BY и алиасы: если сортируешь по алиасу из SELECT, оберни всё в подзапрос s и применяй ORDER BY s.alias, например:
        SELECT ... FROM (SELECT ... AS "agg_alias" FROM ...) s ORDER BY s."agg_alias";
        
        Фильтры и даты:
        Даты/время задавай как DATE 'YYYY-MM-DD' или TIMESTAMP 'YYYY-MM-DD HH24:MI:SS'.
        Для таймзон при необходимости: TIMESTAMP ... AT TIME ZONE 'UTC'.
        
        Параметры: если требуются переменные, используй нейтральные плейсхолдеры вида :start_date, :end_date, :user_id.
        
        NULL/деление: избегай ошибок — при делении используй NULLIF(den,0), при форматировании — COALESCE(...).
        
        Запрещено: DDL/DML, комментарии, пояснения, любые внешние теги (user_query, analytical_hints и т.п.) в ответе.
        
        Формат ответа: верни одну строку с финальным SQL и заверши ;. Никаких бэктиков/тегов.
        
        ЕСЛИ НЕЛЬЗЯ ОТВЕТИТЬ ПО СХЕМЕ
        
        Если по предоставленной схеме данных невозможно однозначно ответить, верни корректный «пустой» селект с пояснением в данных (без комментариев), например:
        SELECT NULL::text AS "reason" WHERE FALSE;
        
        ВЫХОД
        
        Верни только одну строку с SQL, завершающуюся ;.
        
        SQL ЗАПРОС:""".strip()
