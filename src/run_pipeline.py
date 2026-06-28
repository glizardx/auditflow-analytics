from transform import main as transform_data
from load_database import main as load_database


def main():
    print("Etapa 1/2: limpando e anonimizando dados")
    transform_data()
    print()

    print("Etapa 2/2: carregando dados no DuckDB")
    load_database()
    print()

    print("Pipeline finalizado.")


if __name__ == "__main__":
    main()
