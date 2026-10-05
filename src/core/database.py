# src/core/database.py
import os
import duckdb
from src.core.environment import EnvironmentFactory

class DuckDBEngine:
    """Gerenciador centralizado do motor analítico (Engine Pattern)."""
    @staticmethod
    def get_connection() -> duckdb.DuckDBPyConnection:
        os.makedirs("/tmp/duckdb_temp", exist_ok=True)
        env_strategy = EnvironmentFactory.get_strategy()
        max_mem = env_strategy.get_max_memory()

        con = duckdb.connect(database=":memory:")
        con.execute("PRAGMA temp_directory='/tmp/duckdb_temp';")
        con.execute(f"SET max_memory = '{max_mem}';")
        con.execute("SET threads = 1;")
        con.execute("SET preserve_insertion_order = false;")
        return con