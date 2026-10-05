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