import json
import traceback

from utils.parser import str_to_bool
from openai import AsyncOpenAI
from openai.types.shared_params import FunctionDefinition
from openai.types.chat import ChatCompletionToolParam, ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam


class ModeratorService:
    def __init__(self, model_name: str, open_ai_client: AsyncOpenAI):
        self.timeout = 30
        self.model_name = model_name
        self.open_ai_client = open_ai_client

    async def evaluate_user_query(self, user_query: str) -> tuple[bool, str, str | None]:
        sys_prompt = f"""
        Ты высококвалифицированный AI ассистент для глубокой аналитики данных. У тебя есть доступ к базе данных PostgreSQL.
        Ты анализируешь вопрос пользователя и генерируешь SQL запрос к базе данных PostgreSQL.
        Так же ты можешь рекомендовать тип диаграммы для визуализации ответа пользователю."""

        chat_messages = [
            ChatCompletionSystemMessageParam(role="system", content=sys_prompt),
            ChatCompletionUserMessageParam(role="user", content=user_query)
        ]

        try:
            completion = await self.open_ai_client.chat.completions.create(
                top_p=1,
                temperature=0.1,
                max_tokens=1000,
                tools=ModeratorService.create_moderator_tools(),
                tool_choice="required",
                messages=chat_messages,
                parallel_tool_calls=False,
                model=self.model_name,
                timeout=self.timeout
            )
        except Exception as e:
            traceback.print_exc()
            return False, "Произошла ошибка при оценке запроса.", None

        try:
            result = json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
            answer = result["answer"]
            chart_type = result["chart_type"]
            decision = str_to_bool(result["moderator_decision"])
            return decision, answer, chart_type
        except Exception as ex:
            print(completion)
            traceback.print_exc()
            return False, "Произошла ошибка в процессе декодирования ответа.", None

    @staticmethod
    def create_moderator_description() -> str:
        return """
Оцени вопрос пользователя и определи, является ли он запросом к базе данных или общим запросом.
Если вопрос пользователя ЯВЛЯЕТСЯ запросом к базе данных, то определи тип диаграммы, который лучше всего подходит для визуализации данных.
Если вопрос пользователя НЕ ЯВЛЯЕТСЯ запросом к базе данных, то НЕ ОТВЕЧАЙ НА НЕГО, НЕ РАССУЖДАЙ.

Вопрос считается запросом к базе данных, если он:
1. Запрашивает любую информацию о данных (статистика, метрики, показатели).
2. Содержит ссылки на конкретные данные или их характеристики.
3. Подразумевает получение аналитической информации.

Вопрос считается общим, если он:
1. Является приветствием или прощанием.
2. Содержит общие фразы без запросов конкретных данных.
3. Является повседневным запросом (как дела, что ты умеешь и т. д.).
4. Не связан с анализом данных."""

    @staticmethod
    def create_moderator_tools():
        return [ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                strict=True,
                name="evaluate_user_query",
                description=ModeratorService.create_moderator_description(),
                parameters={
                    "type": "object",
                    "properties": {
                        "answer": {
                            "type": "string",
                            "description": "Краткое обоснование дальнейших действий."
                        },
                        "moderator_decision": {
                            "type": "boolean",
                            "description": "True, если вопрос пользователя запросом к базе данных. Иначе False."
                        },
                        "chart_type": {
                            "type": "string",
                            "enum": ["pie", "bar", "line", "doughnut", "area", "histogram", "bubble", "time series", "funnel"],
                            "description": "Тип диаграммы, который лучше всего использовать для визуализации данных, если вопрос пользователя представляет собой запрос к базе данных."
                        }
                    },
                    "required": ["answer", "moderator_decision", "chart_type"],
                    "additionalProperties": False
                }
            )
        )]
