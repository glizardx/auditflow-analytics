import pandas as pd


def main():
    # 1. Carregar a base limpa que foi gerada pelo transform.py
    inspecoes = pd.read_csv("data/processed/inspecoes_limpas.csv")

    # 2. Criar uma coluna booleana: True quando tem erro, False quando nao tem
    inspecoes["TEM_ERRO"] = inspecoes["GRAVIDADE"] != "SEM_ERRO"

    # 3. Calcular indicadores gerais
    total_inspecoes = len(inspecoes)
    total_erros = inspecoes["TEM_ERRO"].sum()
    taxa_erro = total_erros / total_inspecoes * 100

    print("Resumo geral")
    print("-" * 40)
    print(f"Total de inspecoes: {total_inspecoes}")
    print(f"Total de erros: {total_erros}")
    print(f"Taxa de erro: {taxa_erro:.2f}%")
    print()

    # 4. Calcular metricas por tipo de autorizacao
    resumo_tipo = inspecoes.groupby("TIPO_DE_AUTORIZACAO").agg(
        total_inspecoes=("TEM_ERRO", "count"),
        total_erros=("TEM_ERRO", "sum"),
        taxa_erro=("TEM_ERRO", "mean"),
    )

    # 5. A media de True/False sai entre 0 e 1. Multiplicamos por 100 para virar percentual.
    resumo_tipo["taxa_erro"] = resumo_tipo["taxa_erro"] * 100

    # 6. Ordenar para ver primeiro os tipos com maior taxa de erro
    resumo_tipo = resumo_tipo.sort_values("taxa_erro", ascending=False)

    print("Resumo por tipo de autorizacao")
    print("-" * 40)
    print(resumo_tipo.round(2))

    # 7. Salvar o relatorio em CSV para usar depois no dashboard ou no README
    resumo_tipo.round(2).to_csv("outputs/diagnostics/resumo_tipo_autorizacao.csv")


if __name__ == "__main__":
    main()
