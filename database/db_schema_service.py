import logging
import psycopg

from psycopg.rows import tuple_row
from typing import Any, Dict, List, LiteralString
from database.m_schema import MSchema

class DbSchemaService:
    def __init__(self, connection_string: str, schema_name: str, excluded_table_names: List[str], metadata: Dict[str, Dict[str, str]] = None):
        self.metadata = metadata
        self.m_schema = MSchema("PurchaseService", schema=schema_name)
        self.schema_name = schema_name
        self.connection_string = connection_string
        self.excluded_table_names = excluded_table_names
        self.logger = logging.getLogger(__name__)
        self.exclude_fields = ["EntityStatus"]

    async def get_schema(self) -> str:
        tables = await self.get_tables()
        foreign_keys = await self.get_foreign_keys()
        for table_name in tables:
            comment = ""
            if self.metadata is not None and table_name in self.metadata:
                comment = self.metadata[table_name]["comment"]
            self.m_schema.add_table(table_name, {}, comment)

            for item in tables[table_name]:
                column_name = item["column_name"]
                if column_name in self.exclude_fields:
                    continue
                data_type = item["data_type"]
                is_pk = True if item["pk_name"] is not None else False
                is_nullable = True if item["is_nullable"] is not None and item["is_nullable"] == "YES" else False
                default_value = item["column_default"] if item["column_default"] is not None else None
                self.m_schema.add_field(table_name, column_name, data_type, is_pk, is_nullable, default_value, False, "")

            table_foreign_keys = foreign_keys[table_name] if table_name in foreign_keys else []
            for fk in table_foreign_keys:
                self.m_schema.add_foreign_key(table_name, fk["column_name"], fk["f_schema"], fk["f_table"], fk["f_column"])

        return self.m_schema.to_mschema()

    async def get_tables(self) -> Dict[str, List[Any]]:
        schema = {}
        try:
            async with await psycopg.AsyncConnection.connect(self.connection_string) as con:
                async with con.cursor(row_factory=tuple_row) as cur:
                    query: LiteralString = """SELECT t.table_name, c.column_name, c.data_type,
                    c.column_default, c.is_nullable, cc.constraint_name as pk_name
                    FROM information_schema.\"tables\" t
                    JOIN information_schema.columns c ON t.table_name = c.table_name
                        AND t.table_schema = c.table_schema AND t.table_catalog = c.table_catalog
                    LEFT JOIN information_schema.table_constraints tc ON tc.table_schema=t.table_schema
                        AND tc.table_name=t.table_name AND tc.constraint_type='PRIMARY KEY'
                    LEFT JOIN information_schema.constraint_column_usage cc ON tc.table_schema=cc.table_schema
                        AND tc.table_name=cc.table_name AND tc.constraint_name=cc.constraint_name AND c.column_name=cc.column_name
                    WHERE t.table_schema = %s AND NOT t.table_name = ANY (%s) ORDER BY t.table_name, c.ordinal_position;"""
                    await cur.execute(query, (self.schema_name, self.excluded_table_names))
                    records = await cur.fetchall()
                    for record in records:
                        table_name, column_name, data_type, column_default, is_nullable, pk_name = record
                        if table_name not in schema:
                            schema[table_name] = []
                        schema[table_name].append({
                            "column_name": column_name,
                            "data_type": data_type,
                            "column_default": column_default,
                            "is_nullable": is_nullable,
                            "pk_name": pk_name
                        })
            return schema
        except Exception as ex:
            self.logger.error(f"Error while fetching database schema: {ex}")
            raise

    async def get_foreign_keys(self) -> Dict[str, List[Any]]:
        result = {}
        try:
            async with await psycopg.AsyncConnection.connect(self.connection_string) as con:
                async with con.cursor(row_factory=tuple_row) as cur:
                    query: LiteralString = """SELECT tc.table_name, kcu.column_name, 
                    ccu.table_schema AS f_schema, ccu.table_name AS f_table, ccu.column_name AS f_column
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = %s;"""
                    await cur.execute(query, (self.schema_name,))
                    records = await cur.fetchall()
                    for record in records:
                        table_name, column_name, f_schema, f_table, f_column = record
                        if table_name not in result:
                            result[table_name] = []
                        result[table_name].append({
                            "column_name": column_name,
                            "f_schema": f_schema,
                            "f_table": f_table,
                            "f_column": f_column
                        })
            return result
        except Exception as ex:
            self.logger.error(f"Error while fetching foreign keys: {ex}")
            raise

    async def get_table_info(self, table_name) -> Dict[str, str]:
        try:
            async with await psycopg.AsyncConnection.connect(self.connection_string) as con:
                async with con.cursor(row_factory=tuple_row) as cur:
                    query: LiteralString = """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position;"""

                    await cur.execute(query, (self.schema_name, table_name,))

                    table_info = {}
                    records = await cur.fetchall()
                    for record in records:
                        column_name, data_type, is_nullable, column_default = record
                        table_info[column_name] = {
                            'data_type': data_type,
                            'is_nullable': is_nullable,
                            'default': column_default
                        }

                    return table_info

        except Exception as e:
            self.logger.error(f"Error while fetching table info for {table_name}: {e}")
            raise