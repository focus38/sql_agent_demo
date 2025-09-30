import psycopg
import logging

from psycopg.rows import dict_row
from typing import List, Dict, Any


class SqlExecutor:
    def __init__(self, db_config):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)

    async def _execute_query(self, input_sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        try:
            async with await psycopg.AsyncConnection.connect(self.db_config) as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(input_sql, params)
                    result = await cur.fetchall()
                    return [dict(row) for row in result]

        except Exception as e:
            self.logger.error(f"Error while execute SQL query: {e}")
            raise

    async def execute_query(self, sql: str, params: tuple = None) -> Dict[str, Any]:
        try:
            result = await self._execute_query(sql, params)
            return {
                'success': True,
                'data': result,
                'row_count': len(result)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }