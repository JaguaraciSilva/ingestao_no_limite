import os
import sys
import time
import duckdb
import psutil

# Descobre a RAM total disponível no ambiente atual e define o max_memory do DuckDB com segurança
ram_total_mb = psutil.virtual_memory().total / (1024 * 1024)
max_mem = f"{int(ram_total_mb * 0.7)}MB" if ram_total_mb < 500 else "200MB"

def executar_ingestao(csv_path: str, output_parquet: str):
    # Pasta temporária para spill de RAM se necessário
    os.makedirs("/tmp/duckdb_temp", exist_ok=True)
    con = duckdb.connect(database=":memory:")

    # Define o limite de RAM de forma flexível (Docker vs Local)
    # Se estiver rodando no Docker, usa 28MB; no notebook local, usa 200MB para evitar OutOfMemory
    is_docker = os.environ.get("DOCKER_ENV", "false").lower() == "true"
    max_mem = "28MB" if is_docker else "200MB"

    print(f"🔧 Configurando DuckDB | Modo Docker: {is_docker} | max_memory: {max_mem}")

    con.execute("PRAGMA temp_directory='/tmp/duckdb_temp';")
    con.execute(f"SET max_memory = '{max_mem}';")
    con.execute("SET threads = 1;")
    con.execute("SET preserve_insertion_order = false;")

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
            CAST(opcao_pelo_mei AS VARCHAR) ASopcao_pelo_mei,
            TRY_CAST(data_opcao_mei AS DATE) AS data_opcao_mei,
            TRY_CAST(data_exclusao_mei AS DATE) AS data_exclusao_mei
        FROM read_csv(
            '{csv_path}',
            header = true,
            delim = ',',
            dateformat = '%Y-%m-%d',
            auto_detect = false,
            buffer_size = 524288,
            nullstr = ['', 'NULL', 'null', 'N/A'],
            columns = {{
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
            }}
        )
        ORDER BY cnpj_basico
    ) TO '{output_parquet}'
    (
        FORMAT PARQUET,
        COMPRESSION 'ZSTD',
        COMPRESSION_LEVEL 19,
        ROW_GROUP_SIZE 50000
    );
    """

    try:
        con.execute(query)
    finally:
        con.close()


if __name__ == "__main__":
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-f") and not arg.endswith(".json")]

    csv_in = args[0] if len(args) > 0 else "data/empresas_dados_gov.csv"
    parquet_out = args[1] if len(args) > 1 else "data/saida_v9.parquet"

    print(f"🚀 Executando pipeline: '{csv_in}' -> '{parquet_out}'...", flush=True)

    start = time.perf_counter()
    executar_ingestao(csv_in, parquet_out)
    elapsed = time.perf_counter() - start

    if os.path.exists(parquet_out):
        tamanho_mb = os.path.getsize(parquet_out) / (1024 * 1024)
        print("\n" + "=" * 50, flush=True)
        print("         BENCHMARK FINALIZADO", flush=True)
        print("=" * 50, flush=True)
        print(f"⏱️️  Tempo Decorrido:    {elapsed:.2f} s", flush=True)
        print(f"💾 Tamanho em Disco:   {tamanho_mb:.3f} MB", flush=True)
        print("=" * 50, flush=True)
    else:
        print("⚠️ O arquivo de saída não foi localizado.", flush=True)