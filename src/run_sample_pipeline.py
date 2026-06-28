import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ["AUDITFLOW_RAW_DIR"] = str(PROJECT_ROOT / "data" / "sample_raw")


def main():
    from generate_sample_data import main as generate_sample_data
    from load_database import main as load_database
    from transform import main as transform_data

    print("Etapa 1/3: gerando dados sinteticos")
    generate_sample_data()
    print()

    print("Etapa 2/3: limpando e anonimizando dados sinteticos")
    transform_data()
    print()

    print("Etapa 3/3: carregando dados no DuckDB")
    load_database()
    print()

    print("Pipeline de portfolio finalizado.")


if __name__ == "__main__":
    main()
