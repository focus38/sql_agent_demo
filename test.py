import asyncio
import config

from database.db_schema_service import DbSchemaService

db_schema_service = DbSchemaService(config.DB_CONNECTION_STRING, config.SCHEMA_NAME, config.SYSTEM_TABLE_NAMES, config.DB_METADATA)

loop = asyncio.new_event_loop()
result = asyncio.run(db_schema_service.get_schema())
print(result)