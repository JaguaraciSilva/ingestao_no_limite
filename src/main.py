# src/main.py
import sys
import os
import time
from src.domain.models import EmpresaDomainModel
from src.infrastructure.repository import ParquetIngestionRepository

if __name__ == "__main__":
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-f") and not arg.endswith(".json")]

    csv_in = args[0] if len(args) > 0 else "data/empresas_dados_gov.csv"
    parquet_out = args[1] if len(args) > 1 else "data/saida_v9.parquet"

    print(f"🚀 Executando pipeline modular: '{csv_in}' -> '{parquet_out}'...", flush=True)

    start = time.perf_counter()
    
    # Injeta o domínio de Empresas no Repositório de Ingestão
    schema = EmpresaDomainModel.get_schema()
    repository = ParquetIngestionRepository(csv_in, parquet_out, schema)
    repository.ingest()
    
    elapsed = time.perf_counter() - start

    if os.path.exists(parquet_out):
        tamanho_mb = os.path.getsize(parquet_out) / (1024 * 1024)
        print("\n" + "=" * 50, flush=True)
        print("         BENCHMARK FINALIZADO COM SUCESSO", flush=True)
        print("=" * 50, flush=True)
        print(f"⏱  Tempo Decorrido:    {elapsed:.2f} s", flush=True)
        print(f"💾 Tamanho em Disco:   {tamanho_mb:.3f} MB", flush=True)
        print("=" * 50, flush=True)
    else:
        print("⚠️ O arquivo de saída não foi localizado.", flush=True)