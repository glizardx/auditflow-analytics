import duckdb


DATABASE_PATH = "data/database/auditflow.duckdb"
FLUXOS_CSV = "data/processed/fluxos_limpos.csv"
INSPECOES_CSV = "data/processed/inspecoes_limpas.csv"


def main():
    # DuckDB cria o arquivo do banco automaticamente se ele ainda nao existir.
    connection = duckdb.connect(DATABASE_PATH)

    # CREATE OR REPLACE recria a tabela sempre que rodamos o script.
    # Isso ajuda enquanto estamos aprendendo, porque podemos refazer a carga sem medo.
    connection.execute(
        f"""
        CREATE OR REPLACE TABLE fluxos AS
        SELECT *
        FROM read_csv_auto('{FLUXOS_CSV}');
        """
    )

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE inspecoes AS
        SELECT *
        FROM read_csv_auto('{INSPECOES_CSV}');
        """
    )

    total_fluxos = connection.execute("SELECT COUNT(*) FROM fluxos").fetchone()[0]
    total_inspecoes = connection.execute("SELECT COUNT(*) FROM inspecoes").fetchone()[0]

    print("Banco criado com sucesso.")
    print(f"Tabela fluxos: {total_fluxos} linhas")
    print(f"Tabela inspecoes: {total_inspecoes} linhas")

    connection.close()


if __name__ == "__main__":
    main()
