# Desafio: Ingestão de Alta Performance (`ingestao_no_limite`)

Manual Técnico & Resolução do Desafio para Engenheiros de Dados Júnior.

## 1. Contexto do Desafio e Metas
O desafio `ingestao_no_limite` exige processar um volume massivo de dados (3 milhões de registros, 13 colunas do cadastro CNPJ do dados.gov.br) sob restrições extremas de hardware em contêiner Docker[cite: 1]:
- **Memória RAM Máxima:** < 37.0 MB (Pico estrito)[cite: 1]
- **Armazenamento Parquet Final:** < 6.825 MB[cite: 1]
- **Tempo Limite:** < 420.0 segundos (7 minutos)[cite: 1]

**Desafio Arquitetural:** A ordenação global de dados é essencial para que os algoritmos de compressão Parquet (*Dictionary Encoding, RLE, Delta Encoding*) atinjam tamanhos reduzidos[cite: 1]. No entanto, ordenar 3 milhões de linhas na memória estoura facilmente a RAM de 37 MB[cite: 1]. A solução reside em motores com execução *Out-of-Core* (spill para disco) e ajuste fino dos buffers de leitura e escrita[cite: 1].

---

## 2. Arquitetura Modular e Design Patterns (DDD)
Para garantir alta coesão e reutilização para novos domínios de dados, o projeto adota **Domain-Driven Design (DDD)** e **Data Engineering Design Patterns** (Strategy e Repository):
- **Motor (Core):** Gerenciamento centralizado de conexões DuckDB e estratégia dinâmica de memória baseada no ambiente (`Docker` vs `Local`).
- **Domínio (Domain):** Definição de contratos de schemas e regras de mapeamento de colunas isoladas por domínio.
- **Repositório (Infrastructure):** Abstração da persistência em colunas (*Out-of-Core Read/Write* em Parquet).

---

## 3. Estrutura do Repositório
```text
ingestao_no_limite/
├── .gitignore
├── README.md
├── Dockerfile
├── requirements.txt
├── data/
│   └── empresas_dados_gov.csv
└── src/
    ├── __init__.py
    ├── main.py
    ├── core/
    │   ├── __init__.py
    │   ├── database.py
    │   └── environment.py
    ├── domain/
    │   ├── __init__.py
    │   └── models.py
    └── infrastructure/
        ├── __init__.py
        └── repository.py

```
---

## 4. Instruções de Execução no Ambiente (Linux / Debian / WSL2)

1. Permitir execução no diretório do projeto 

```text
sudo usermod -aG docker $USER
newgrp docker
```

2. Build da Imagem Docker

Na raiz do projeto (ingestao_no_limite), execute:

```text
docker run --rm --memory="200m" --memory-swap="200" -v $(pwd)/data:/data ingestao-no-limite:v9 /data/empresas_dados_gov.csv /data/saida.parquet
```

3. Para evitar o versionamento de arquivos temporários e pesados:

Arquivo .gitignore Recomendado

```text
.venv/
*.csv
*.parquet
data/
/tmp/
```

## 5. Guia de Extensibilidade: Como Adicionar um Novo Domínio (Ex: Funcionários)

Graças ao desacoplamento da arquitetura DDD, para processar um novo conjunto de dados (como dados de funcionários associados às empresas) não é necessário alterar nenhuma linha da infraestrutura ou do motor DuckDB.

Basta seguir 2 passos:

### Passo A: Criar o Modelo do Domínio (src/domain/funcionarios_model.py)

```text
from dataclasses import dataclass
from typing import Dict

@dataclass
class DatasetSchema:
    columns_mapping: Dict[str, str]
    order_by_column: str
    row_group_size: int = 50000
    compression: str = "ZSTD"
    compression_level: int = 19

class FuncionarioDomainModel:
    @staticmethod
    def get_schema() -> DatasetSchema:
        columns = {
            'cnpj_basico': 'VARCHAR',
            'cpf_funcionario': 'VARCHAR',
            'nome_funcionario': 'VARCHAR',
            'cargo': 'VARCHAR',
            'data_admissao': 'VARCHAR'
        }
        return DatasetSchema(
            columns_mapping=columns,
            order_by_column="cnpj_basico" # Ordena por CNPJ para agrupar
        )
```

### Passo B: Consumir no Pipeline Reutilizando o Repositório

```text
Basta injetar o novo schema no ParquetIngestionRepository já existente, mantendo todo o padrão de alta performance e consumo restrito de RAM.

from src.domain.funcionarios_model import FuncionarioDomainModel
from src.infrastructure.repository import ParquetIngestionRepository

# 1. Pega o schema do novo domínio (Funcionários)
schema = FuncionarioDomainModel.get_schema()

# 2. Injeta o schema diretamente no repositório de infraestrutura já existente
repository = ParquetIngestionRepository(
    csv_path="data/funcionarios.csv", 
    output_parquet="data/funcionarios_saida.parquet", 
    schema=schema
)

# 3. Executa a ingestão reutilizando 100% da engine DuckDB,
# mantendo o Out-of-Core, o spill para disco e o consumo restrito de RAM!
repository.ingest()

```

### Comandos Git para criar a nova branch e enviar as atualizações:

Execute os comandos abaixo no seu terminal para registrar tudo na nova branch:

```bash
git checkout -b feature/ddd-architecture
git add .
git commit -m "feat: adiciona arquitetura DDD, design patterns e guia de novos dominios no README"
git push -u origin feature/ddd-architecture