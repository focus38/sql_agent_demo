import os
from dotenv import load_dotenv

load_dotenv()

AI_TIMEOUT = 60
AI_GATEWAY_URL = os.getenv("AI_GATEWAY_URL")
AI_GATEWAY_API_KEY = os.getenv("AI_GATEWAY_API_KEY")
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

SCHEMA_NAME = "public"
DEFAULT_LLM_MODEL = "qwen3-coder"
SYSTEM_TABLE_NAMES = ["__EFMigrationsHistory", "__VersionedTaskHistory", "debezium_heartbeat", "debezium_signal",
                      "SignalOutbox", "InboxState", "OutboxMessage", "OutboxState"]
ANALYTICAL_HINTS = [
    "департамент, управление, заказчик, отдел - это все клиенты системы закупок. Описываются таблицей Organization. Связь 1:N с Purchase осуществляется по полям Purchase.CustomerOrganizationID=Organization.OrganizationID",
    "поставщик, снабжающая организация, продавец - это организации, которые продают товары или услуги клиентам. Описываются так же таблицей Organization. Связь 1:N с ContractorOffer осуществляется по полям ContractorOffer.ContractorOrganizationID=Organization.OrganizationID",
    "Уторговывание - это этап конкурентной процедуры закупки, на котором участники получают возможность улучшить первоначальное предложение: снизить цену, изменив другие коммерческие условия.",
    "Голосование не завершилось - это значит статус протокола (поле ProtocolStatusID) меньше чем 4 (Подписан).",
    "Член комиссии проголосовал ЗА или пользователь проголосовал положительно - это значит поле Decision равно True в таблице ProtocolDecisionAccounts для соответствующего пользователя и решения протокола.",
    "Сторонний пользователь или сторонний участник комиссии - это значит, что пользователь не относится к организации с кодом 21",
    "Предложение не изменилось относительно результатов голосования - это значит дата изменения предложения до (меньше или равно) даты голосования.",
    "Если предложение победило после уторговывания, но в период уторговывания не было изменений ни в ContractorOffer, ни в ContractorOfferProduct, то это можно рассматривать, как махинация и подтасовка результатов под определенного поставщика.",
    "Поле Decision в таблице ProtocolDecisionAccounts имеет тип данных boolean",
    "Используй запрос к view public.SimilarPurchases для определения списка закупок, которые потенциально можно объединить в одну закупку."
]

DB_METADATA = {
    "Account": {
        "comment": "Пользователи системы."
    },
    "Bargaining": {
        "comment": "Перечень закупок, где была уторговка. Таблица содержит идентификатор закупки и длительность уторговки в часах."
    },
    "ContractorOffer": {
        "comment": "Предложение поставщика."
    },
    "Need": {
        "comment": "Потребность в товаре или услуги клиента торговой площадки."
    },
    "ContractorOfferProduct": {
        "comment": "Предложение по товару или услуги поставщика для закрытия конкретной потребности клиента."
    },
    "ContractorOfferStatus": {
        "comment": "Справочник статусов предложений поставщика."
    },
    "DecisionType": {
        "comment": "Справочник типов решений, отраженных в решении по протоколу."
    },
    "DeliveryKind": {
        "comment": "Справочник способов доставки товара от поставщика до клиента."
    },
    "DeliveryType": {
        "comment": "Справочник, отражающий возможность доставки товара от поставщика до клиента."
    },
    "Organization": {
        "comment": "Справочник организаций, работающих на торговой площадке (и поставщики, и клиенты)."
    },
    "Protocol": {
        "comment": "Протоколы торговой комиссии."
    },
    "ProtocolCommission": {
        "comment": "Состав комиссии для каждого протокола."
    },
    "ProtocolDecision": {
        "comment": "Решение комиссии по каждому предложению в рамках протокола."
    },
    "ProtocolDecisionAccounts": {
        "comment": "Решение каждого члена комиссии в рамках решения комиссии."
    },
    "ProtocolStatus": {
        "comment": "Справочник статусов протоколов."
    },
    "Purchase": {
        "comment": "Перечень закупок, которые осуществляются торговой площадкой."
    },
    "PurchaseStatus": {
        "comment": "Справочник статусов закупки."
    },
    "PurchaseStatusHistory": {
        "comment": "Таблица описывает историю изменения статусов закупки."
    },
    "SimilarPurchases": {
        "comment": "Перечень закупок, которые потенциально можно объединить в одну закупку."
    }
}
