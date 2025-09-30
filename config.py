AI_TIMEOUT = 60
AI_GATEWAY_URL = ""
AI_GATEWAY_API_KEY = ""

SCHEMA_NAME = "public"
LLM_MODEL = "qwen3-coder"
DB_CONNECTION_STRING = "dbname=PurchaseService user=postgres password=postgres host=localhost"
SYSTEM_TABLE_NAMES = ["__EFMigrationsHistory", "__VersionedTaskHistory", "debezium_heartbeat", "debezium_signal",
                      "SignalOutbox", "InboxState", "OutboxMessage", "OutboxState"]
ANALYTICAL_HINTS = [
    "департамент, управление, заказчик, отдел - это все клиенты системы закупок. Описываются таблицей Organization. Связь 1:N с Purchase осуществляется по полям Purchase.CustomerOrganizationID=Organization.OrganizationID",
    "поставщик, снабжающая организация, продавец - это организации, которые продают товары или услуги клиентам. Описываются так же таблицей Organization. Связь 1:N с ContractorOffer осуществляется по полям ContractorOffer.ContractorOrganizationID=Organization.OrganizationID",
    "Уторговывание - это этап конкурентной процедуры закупки, на котором участники получают возможность улучшить первоначальное предложение: снизить цену, изменив другие коммерческие условия.",
    "При уторговывании закупка (purchase) меняет статус с “Анализ предложений” (5) на “Сбор предложений” (4). Это отражается в таблице PurchaseStatusHistory. Если на этапе уторговывания было голосование “за” по одному из предложений, то статус закупки изменится на “Победитель определен” (7).",
    "Период уторговывания - это период между статусами Анализ предложений->Сбор предложений->Победитель определен.",
    "Для определения операции уторговывание через таблицу PurchaseStatusHistory необходимо смотреть min(CreationDate) для статуса 5, max(CreationDate) для статуса 4, min(CreationDate) для статуса 7.",
    "Если предложение победило после уторговывания, но в период уторговывания не было изменений ни в ContractorOffer, ни в ContractorOfferProduct, то это можно рассматривать, как махинация и подтасовка результатов под определенного поставщика.",
    "Поле Decision в таблице ProtocolDecisionAccounts имеет тип данных boolean"
]

DB_METADATA = {
    "Account": {
        "comment": "Пользователи системы."
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
    }
}
