import duckdb


DATABASE_PATH = "data/database/auditflow.duckdb"
QUERY_PATH = "sql/resumo_tipo_autorizacao.sql"


def main():
    connection = duckdb.connect(DATABASE_PATH)

    with open(QUERY_PATH, "r", encoding="utf-8") as file:
        query = file.read()

    resultado = connection.execute(query).fetchdf()

    print("Resultado da query SQL")
    print("-" * 40)
    print(resultado)

    connection.close()


if __name__ == "__main__":
    main()
