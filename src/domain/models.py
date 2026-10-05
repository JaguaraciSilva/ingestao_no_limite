# src/domain/models.py
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class DatasetSchema:
    """Contrato de Domínio para metadados e tipos de colunas."""
    columns_mapping: Dict[str, str]
    order_by_column: str
    row_group_size: int = 50000
    compression: str = "ZSTD"
    compression_level: int = 19

class EmpresaDomainModel:
    """Regras de mapeamento específicas para o domínio de Empresas CNPJ."""
    @staticmethod
    def get_schema() -> DatasetSchema:
        columns = {
            'cnpj_basico': 'VARCHAR',
            'razao_social': 'VARCHAR',
            'natureza_juridica': 'VARCHAR',
            'qualificacao_responsavel': 'VARCHAR',
            'capital_social': 'VARCHAR',
            'porte_empresa': 'VARCHAR',
            'ente_federativo_responsavel': 'VARCHAR',
            'opcao_pelo_simples': 'VARCHAR',
            'data_opcao_simples': 'VARCHAR',
            'data_exclusao_simples': 'VARCHAR',
            'opcao_pelo_mei': 'VARCHAR',
            'data_opcao_mei': 'VARCHAR',
            'data_exclusao_mei': 'VARCHAR'
        }
        return DatasetSchema(
            columns_mapping=columns,
            order_by_column="cnpj_basico"
        )