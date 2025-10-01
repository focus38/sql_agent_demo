import json
import asyncio
import logging

from typing import Any, Dict, List
from smolagents import CodeAgent, LiteLLMModel, Tool
from database.sql_executor import SqlExecutor
from database.db_schema_service import DbSchemaService
from analytics.analytics_hint_service import AnalyticsHintService
from llm.sql_generator_service import SqlGeneratorService
from agents.tools import DataBaseSchemaTool, TableInfoTool, GenerateSqlTool, AnalyticsHintTool, SqlExecutorTool


class DatabaseAgent:
    def __init__(self, db_config: Dict[str, Any], ai_config: Dict[str, Any]):
        self.api_key = ai_config["api_key"]
        self.model_name = ai_config["model_name"]
        self.ai_gateway_url = ai_config["ai_gateway_url"]
        self.schema_name: str = db_config["schema_name"]
        self.connection_string: str = db_config["connection_string"]
        self.excluded_table_names: List[str] = db_config["excluded_table_names"]
        self.db_metadata : Dict[str, Dict[str, str]] = db_config["db_metadata"]

        # Инициализация сервисов
        self.sql_executor = SqlExecutor(self.connection_string)
        self.db_schema_service = DbSchemaService(self.connection_string, self.schema_name, self.excluded_table_names, self.db_metadata)
        self.analytics_hint_service = AnalyticsHintService()
        self.sql_generator_service = SqlGeneratorService()

        # Создание инструментов для агента
        self.tools = self._create_tools()

        # Инициализация агента
        self.agent = CodeAgent(
            tools=self.tools,
            add_base_tools=True,
            model=self._setup_llm_model(),
            name="ai_assistant_purchase_system",
            additional_authorized_imports=["json"],
            description="Я ассистент, который помогает анализировать данные в системе закупок."
        )

        self.logger = logging.getLogger(__name__)

    def cleanup(self):
        del self.tools, self.sql_executor, self.db_schema_service, self.analytics_hint_service, self.sql_generator_service
        self.agent.cleanup()

    def _setup_llm_model(self) -> LiteLLMModel:
        # Базовые параметры для модели
        model_params = {
            'api_key': self.api_key,
            'model': f"litellm_proxy/{self.model_name}",
            'model_id': f"litellm_proxy/{self.model_name}",
            'api_base': self.ai_gateway_url,
            'temperature': 0.1,  # Низкая температура для более детерминированных SQL запросов
            'max_tokens': 2000
        }

        try:
            # Создаем модель LiteLLM с нашими параметрами
            return LiteLLMModel(**model_params)

        except Exception as e:
            self.logger.error(f"Error configuring LLM model: {e}")
            raise

    def _create_tools(self) -> List[Tool]:
        return [
            DataBaseSchemaTool(self.db_schema_service),
            #TableInfoTool(self.db_schema_service),
            AnalyticsHintTool(self.analytics_hint_service),
            GenerateSqlTool(self.sql_generator_service),
            SqlExecutorTool(self.sql_executor)
        ]

    def process_query(self, user_query: str) -> str:
        try:
            prompt = DatabaseAgent.create_prompt(user_query)
            return self.agent.run(prompt)
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return f"Произошла ошибка при обработке запроса: {str(e)}"

    async def process_query_async(self, user_query: str) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.process_query, user_query)

    @staticmethod
    def create_prompt(user_query: str) -> str:
        expected_data = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "title": "Формат данных для предоставления результата работы ai_assistant_purchase_system.",
            "description": "Описание JSON формата данных, который должен предоставить в ответ на вопрос пользователя ai_assistant_purchase_system",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Тут должен быть заголовок, который ты придумаешь."
                },
                "x": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Тут должен быть заголовок для данных оси абсцисс"
                        },
                        "values": {
                            "type": "array",
                            "items": {
                                "oneOf": [
                                    {"type": "number"},
                                    {"type": "string", "format": "date-time"}
                                ]
                            },
                            "description": "Тут должны быть значения из результата выполнения SQL запроса, которые можно использовать на оси абсцисс (ось X в декартовой системе координат)."
                        }
                    }
                },
                "y": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Тут должен быть заголовок для данных"
                            },
                            "values": {
                                "type": "array",
                                "items": {
                                    "oneOf": [
                                        {"type": "number"},
                                        {"type": "string"}
                                    ]
                                },
                                "description": "Тут должны быть значения из результата выполнения SQL запроса, которые можно использовать на оси ординат (ось Y в декартовой системе координат)."
                            }
                        }
                    }
                }
            }
        }
        expected_json_string = json.dumps(expected_data, indent=2)
        return f"""
        Ты - AI ассистент для аналитики данных. У тебя есть доступ к базе данных PostgreSQL через следующие инструменты:

        1. get_database_schema - получить схему БД.
        2. generate_analytics_hints - сгенерировать аналитические подсказки.
        3. generate_sql_query - сгенерировать SQL запрос.
        4. execute_sql_query - выполнить SQL запрос.

        ПОЛЬЗОВАТЕЛЬСКИЙ ЗАПРОС: {user_query}

        ДЕЙСТВИЯ:
        1. Сначала изучи схему базы данных.
        2. Сгенерируй аналитические подсказки на основе запроса.
        3. Создай соответствующий SQL запрос.
        4. Выполни запрос и проанализируй результаты.
        5. Подготовь ответ пользователю в JSON формате. JSON schema предоставлена ниже:
        {expected_json_string}
        6. Предоставь форматированный ответ пользователю.

        ВАЖНО: Всегда проверяй существование таблиц и полей перед выполнением запросов.
        Будь осторожен с большими наборами данных, поэтому используй LIMIT, где это уместно.
        """
