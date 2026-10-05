# src/infrastructure/repository.py
from src.core.database import DuckDBEngine
from src.domain.models import DatasetSchema

class ParquetIngestionRepository:
    """Repository Pattern para persistência em formato columnar (Parquet)."""
    
    def __init__(self, csv_path: str, output_parquet: str, schema: DatasetSchema):
        self.csv_path = csv_path
        self.output_parquet = output_parquet
        self.schema = schema

    def _build_column_definitions(self) -> str:
        return ",\n".join([f"'{col}': '{dtype}'" for col, dtype in self.schema.columns_mapping.items()])

    def ingest(self):
        con = DuckDBEngine.get_connection()
        columns_def = self._build_column_definitions()
        
        query = f"""
        COPY (
            SELECT
                TRY_CAST(cnpj_basico AS UINTEGER) AS cnpj_basico,
                CAST(razao_social AS VARCHAR) AS razao_social,
                TRY_CAST(natureza_juridica AS USMALLINT) AS natureza_juridica,
                TRY_CAST(qualificacao_responsavel AS UTINYINT) AS qualificacao_responsavel,
                TRY_CAST(capital_social AS FLOAT) AS capital_social,
                CAST(porte_empresa AS VARCHAR) AS porte_empresa,
                CAST(ente_federativo_responsavel AS VARCHAR) AS ente_federativo_responsavel,
                CAST(opcao_pelo_simples AS VARCHAR) AS opcao_pelo_simples,
                TRY_CAST(data_opcao_simples AS DATE) AS data_opcao_simples,
                TRY_CAST(data_exclusao_simples AS DATE) AS data_exclusao_simples,
                CAST(opcao_pelo_mei AS VARCHAR) AS opcao_pelo_mei,
                TRY_CAST(data_opcao_mei AS DATE) AS data_opcao_mei,
                TRY_CAST(data_exclusao_mei AS DATE) AS data_exclusao_mei
            FROM read_csv(
                '{self.csv_path}',
                header = true,
                delim = ',',
                dateformat = '%Y-%m-%d',
                auto_detect = false,
                buffer_size = 524288,
                nullstr = ['', 'NULL', 'null', 'N/A'],
                columns = {{{columns_def}}}
            )
            ORDER BY {self.schema.order_by_column}
        ) TO '{self.output_parquet}'
        (
            FORMAT PARQUET,
            COMPRESSION '{self.schema.compression}',
            COMPRESSION_LEVEL {self.schema.compression_level},
            ROW_GROUP_SIZE {self.schema.row_group_size}
        );
        """
        try:
            con.execute(query)
        finally:
            con.close()