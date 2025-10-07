import asyncio
import decimal
import traceback

from smolagents import Tool
from typing import Any, Dict, List
from database.sql_executor import SqlExecutor
from database.db_schema_service import DbSchemaService
from llm.sql_generator_service import SqlGeneratorService
from analytics.analytics_hint_service import AnalyticsHintService


class DataBaseSchemaTool(Tool):
    name = "get_database_schema"
    description = "Возвращает схему базы данных со списком таблиц и полей."
    inputs = {}
    output_type = "string"

    def __init__(self, db_schema_service: DbSchemaService):
        super().__init__()
        self.db_schema_service = db_schema_service

    def forward(self):
        try:
            return asyncio.run(self.db_schema_service.get_schema())
        except Exception as ex:
            print(f"Error in db_schema_service forward: {ex}")
            traceback.print_exc()

class TableInfoTool(Tool):
    name = "get_table_info"
    description = "Возвращает детальную информацию о конкретной таблице."
    inputs = {
        "table_name": {"type": "string", "description": "Table name."}
    }
    output_type = "any"

    def __init__(self, db_schema_service: DbSchemaService):
        super().__init__()
        self.db_schema_service = db_schema_service

    def forward(self, table_name: str):
        return asyncio.run(self.db_schema_service.get_table_info(table_name))

class AnalyticsHintTool(Tool):
    name = "generate_analytics_hints"
    description = "Генерирует аналитические подсказки на основе запроса пользователя"
    inputs = {
        "user_query": {"type": "string", "description": "User input query."}
    }
    output_type = "any"

    def __init__(self, analytics_hint_service: AnalyticsHintService):
        super().__init__()
        self.analytics_hint_service = analytics_hint_service

    def forward(self, user_query: str):
        return self.analytics_hint_service.create_hints(user_query)

class GenerateSqlTool(Tool):
    name = "generate_sql_query"
    description = "Генерирует SQL запрос на основе схемы, подсказок и запроса пользователя"
    inputs = {
        "schema": {"type": "string", "description": "Database schema."},
        "hints": {"type": "any", "description": "Analytics hints."},
        "user_query": {"type": "string", "description": "User input query."}
    }
    output_type = "string"

    def __init__(self, sql_generator_service: SqlGeneratorService):
        super().__init__()
        self.sql_generator_service = sql_generator_service

    def forward(self, schema: str, hints: List[str], user_query: str):
        return self.sql_generator_service.generate_sql_prompt(schema, hints, user_query)

class SqlExecutorTool(Tool):
    name = "execute_sql_query"
    description = "Выполняет SQL запрос и возвращает результат"
    inputs = {
        "sql_query": {"type": "string", "description": "SQL-query for execution."}
    }
    output_type = "any"

    def __init__(self, sql_executor: SqlExecutor):
        super().__init__()
        self.sql_executor = sql_executor

    def forward(self, sql_query: str):
        return asyncio.run(self.sql_executor.execute_query(sql_query))

class ExplainQueryResultTool(Tool):
    name = "explain_query_results"
    description = "Анализирует и объясняет результаты запроса"
    inputs = {
        "results": {"type": "any", "description": "Result of executing the SQL query."}
    }
    output_type = "any"

    def __init__(self):
        super().__init__()

    def forward(self, results: Dict[str, Any]):
        if not results['success']:
            return f"Ошибка выполнения запроса: {results['error']}"

        data = results['data']
        row_count = results['row_count']

        if row_count == 0:
            return "Запрос вернул 0 строк. Возможно, нужно изменить условия."

        # Простой анализ результатов
        analysis = f"Запрос выполнен успешно. Возвращено {row_count} строк.\n"

        if row_count > 100:
            analysis += "Результат содержит много строк. Рассмотри возможность агрегации или фильтрации.\n"

        # Анализ первых нескольких строк для понимания структуры
        if data:
            sample_columns = list(data[0].keys())
            analysis += f"Полей в результате: {', '.join(sample_columns)}\n"

            # Проверяем наличие числовых данных
            numeric_fields = []
            for key, value in data[0].items():
                if isinstance(value, (int, float, decimal.Decimal)):
                    numeric_fields.append(key)

            if numeric_fields:
                analysis += f"Числовые поля для анализа: {', '.join(numeric_fields)}"

        return analysis