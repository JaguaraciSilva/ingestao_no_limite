# Desafio: Ingestão de Alta Performance (`ingestao_no_limite`)

Manual Técnico & Resolução do Desafio para Engenheiros de Dados Júnior.

## 1. Contexto do Desafio e Metas
O desafio `ingestao_no_limite` exige processar um volume massivo de dados (3 milhões de registros, 13 colunas do cadastro CNPJ do dados.gov.br) sob restrições extremas de hardware em contêiner Docker[cite: 1]:
* **Memória RAM Máxima:** < 37.0 MB (Pico estrito)[cite: 1]
* **Armazenamento Parquet Final:** < 6.825 MB[cite: 1]
* **Tempo Limite:** < 420.0 segundos (7 minutos)[cite: 1]

**Desafio Arquitetural:** A ordenação global de dados é essencial para que os algoritmos de compressão Parquet (*Dictionary Encoding, RLE, Delta Encoding*) atinjam tamanhos reduzidos[cite: 1]. No entanto, ordenar 3 milhões de linhas na memória estoura facilmente a RAM de 37 MB[cite: 1]. A solução reside em motores com execução *Out-of-Core* (spill para disco) e ajuste fino dos buffers de leitura e escrita[cite: 1].

---

## 2. Comparativo de Versões e Aprendizados Técnicos
Após a evolução do pipeline por 9 versões, a **V9** foi consagrada como campeã[cite: 1]:
* **Motor:** DuckDB com Out-of-Core, compressão `ZSTD` (nível 19) e *Row Group Size* de 50.000[cite: 1].
* **Estratégia de Streaming & Spill:** A configuração `SET max_memory = '28MB';` e o uso de diretório temporário forçam o spill para disco, mantendo o pico de RAM estritamente abaixo do teto[cite: 1, 4].
* **Delta Encoding no CNPJ:** Ordenar por `cnpj_basico` faz com que o Parquet aplique *DELTA BINARY_PACKED*, reduzindo drasticamente o tamanho da coluna[cite: 2].

---

## 3. Estrutura do Repositório
ingestao_no_limite/
├── .gitignore
├── README.md
├── data/
│   └── empresas_dados_gov.csv
└── src/
    ├── Dockerfile
    └── main.py

---

## 4. Instruções de Execução no Ambiente (Linux / Debian / WSL2)

1. Permitir execução no diretório do projeto 

sudo usermod -aG docker $USER
newgrp docker

2. Build da Imagem Docker

Na raiz do projeto (ingestao_no_limite), execute:

docker run --rm --memory="37m" --memory-swap="37m" -v $(pwd)/data:/data ingestao-no-limite:v9 /data/empresas_dados_gov.csv /data/saida.parquet

3. Para evitar o versionamento de arquivos temporários e pesados:

Arquivo .gitignore Recomendado

.venv/
*.csv
*.parquet
data/
/tmp/