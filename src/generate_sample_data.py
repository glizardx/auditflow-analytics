from __future__ import annotations

import random
from datetime import datetime, timedelta

import pandas as pd

from config import DATA_DIR


OUTPUT_DIR = DATA_DIR / "sample_raw"
RANDOM_SEED = 42

PROCESS_TYPES = [
    "PROCESSO_A",
    "PROCESSO_B",
    "PROCESSO_C",
    "PROCESSO_D",
    "PROCESSO_E",
    "PROCESSO_F",
    "PROCESSO_G",
]

PROCESS_WEIGHTS = [0.36, 0.19, 0.17, 0.13, 0.08, 0.04, 0.03]
ERROR_RATES = {
    "PROCESSO_A": 0.055,
    "PROCESSO_B": 0.030,
    "PROCESSO_C": 0.060,
    "PROCESSO_D": 0.075,
    "PROCESSO_E": 0.070,
    "PROCESSO_F": 0.280,
    "PROCESSO_G": 0.180,
}


def choose_process_type() -> str:
    return random.choices(PROCESS_TYPES, weights=PROCESS_WEIGHTS, k=1)[0]


def fake_document(index: int) -> str:
    return f"{index:011d}"


def build_flow_data(rows: int = 27_000) -> pd.DataFrame:
    start_date = datetime(2025, 9, 15, 8, 0, 0)
    records = []

    for index in range(rows):
        process_type = choose_process_type()
        start_at = start_date + timedelta(
            days=random.randint(0, 65),
            minutes=random.randint(0, 600),
        )
        duration = max(1, random.lognormvariate(4.2, 1.0))
        finished_at = start_at + timedelta(minutes=duration)
        status = random.choices(["Completo", "Iniciado"], weights=[0.94, 0.06], k=1)[0]

        records.append(
            {
                "IDPROCESSO": 900 + random.randint(1, 80),
                "NOMEPROCESSO": f"Fluxo Operacional {process_type}",
                "IDOCORRENCIAPROCESSO": 300_000_000 + index,
                "IDREGISTROCONTROLADO": process_type,
                "INSTITUICAOORIGEM": 1000 + random.randint(1, 20),
                "UNIDADEORIGEM": random.randint(0, 99),
                "INSTITUICADESTINO": 2000 + random.randint(1, 20),
                "UNIDADEDESTINO": random.randint(0, 99),
                "USUARIO": f"usuario_{random.randint(1, 180):03d}",
                "ATIVIDADE": random.choice(["VALIDA", "APROVACAO", "APROVACAO_GESTOR"]),
                "PROCEDIMENTO": random.choices(
                    ["APROVAR", "DEVOLVER PARA CORRECAO", "REPROVAR", "CANCELAR FLUXO"],
                    weights=[0.86, 0.10, 0.03, 0.01],
                    k=1,
                )[0],
                "SITUACAOFLUXO": status,
                "DATAHORAINICIOATIVIDADE": start_at.strftime("%d/%m/%Y %H:%M:%S"),
                "DATAHORAFIMATIVIDADE": finished_at.strftime("%d/%m/%Y %H:%M:%S"),
                "JUSTIFICATIVA": "Texto sintetico removido no pipeline"
                if random.random() < 0.12
                else None,
            }
        )

    return pd.DataFrame(records)


def build_inspection_data(rows: int = 6_600) -> pd.DataFrame:
    start_date = datetime(2025, 11, 1)
    records = []

    for index in range(rows):
        process_type = choose_process_type()
        has_error = random.random() < ERROR_RATES[process_type]
        severity = (
            random.choices(["Grave", "Gravissimo"], weights=[0.84, 0.16], k=1)[0]
            if has_error
            else "Sem Erro"
        )
        error_type = (
            random.choice(["Aprovacao Incorreta", "Reprovacao Incorreta", "Preenchimento Incorreto"])
            if has_error
            else "Sem Erro"
        )

        records.append(
            {
                "COORDENACAO": f"coordenacao_{random.randint(1, 4)}",
                "LIDERANCA": f"lideranca_{random.randint(1, 10)}",
                "DATA DA INSPECAO": start_date + timedelta(days=random.randint(0, 25)),
                "INSPETOR": f"inspetor_{random.randint(1, 9)}",
                "CPF/CNPJ": fake_document(index + 1),
                "COOP": f"unidade_{random.randint(1, 35)}",
                "TIPO": random.choice(["Cooperativa", "Autorizar", "Autoatendimento"]),
                "DATA DE EXECUCAO": start_date - timedelta(days=random.randint(0, 8)),
                "INTERNO OU EXTERNO": random.choices(
                    ["Interno", "Chamados", "Externo"],
                    weights=[0.88, 0.10, 0.02],
                    k=1,
                )[0],
                "TIPO DE AUTORIZACAO": process_type,
                "COLABORADOR": f"colaborador_{random.randint(1, 165):03d}",
                "TIPO DE ERRO": error_type,
                "DESCRICAO": "Descricao sintetica removida no pipeline" if has_error else None,
                "GRAVIDADE": severity,
                "DESVIO DE ATENCAO": "Sim" if has_error and random.random() < 0.75 else "Nao",
                "REVERSAO": "Nao",
                "QUAIS FLUXOS": None,
                "OBSERVACOES": None,
                "SOLICITANTE": None,
            }
        )

    return pd.DataFrame(records)


def main() -> None:
    random.seed(RANDOM_SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    flow = build_flow_data()
    inspections = build_inspection_data()

    flow.to_excel(OUTPUT_DIR / "volume_fluxos.xlsx", index=False)

    with pd.ExcelWriter(OUTPUT_DIR / "inspecoes_202511.xlsx") as writer:
        pd.DataFrame({"TIPOS DE AUTORIZAÇÃO": PROCESS_TYPES}).to_excel(
            writer,
            sheet_name="Listas",
            index=False,
        )
        pd.DataFrame(
            {
                "Novembro": pd.date_range("2025-11-01", periods=20),
                "Atividade": ["Inspecao"] * 20,
            }
        ).to_excel(writer, sheet_name="CRONOGRAMA", index=False)

        inspectors = sorted(inspections["INSPETOR"].unique())
        for inspector in inspectors:
            sheet = inspections[inspections["INSPETOR"] == inspector].drop(columns=["INSPETOR"])
            sheet.insert(3, "INSPETOR", inspector)
            sheet.to_excel(writer, sheet_name=inspector, index=False)

    print("Dados sinteticos gerados em:")
    print(OUTPUT_DIR)
    print()
    print("Arquivos:")
    print(OUTPUT_DIR / "volume_fluxos.xlsx")
    print(OUTPUT_DIR / "inspecoes_202511.xlsx")


if __name__ == "__main__":
    main()
