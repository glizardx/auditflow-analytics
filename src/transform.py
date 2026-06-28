from __future__ import annotations

import hashlib
import re
import unicodedata
import warnings

import pandas as pd

from config import FLOW_FILE, INSPECTIONS_FILE, PROCESSED_DIR
from inspect_excel import SKIP_INSPECTION_SHEETS, require_file


SENSITIVE_COLUMNS = {
    "USUARIO": "usuario",
    "COLABORADOR": "colaborador",
    "INSPETOR": "inspetor",
    "CPF/CNPJ": "documento",
}


def normalize_text(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    text = " ".join(text.split())
    return text


def normalize_category(value: object) -> object:
    text = normalize_text(value)
    if pd.isna(text):
        return pd.NA

    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]+", "_", text)
    text = text.strip("_")
    return text


def anonymize_value(value: object, prefix: str) -> object:
    if pd.isna(value):
        return pd.NA

    normalized = normalize_text(value)
    digest = hashlib.sha256(str(normalized).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{digest}"


def generalize_process_category(value: object) -> object:
    category = normalize_category(value)
    if pd.isna(category):
        return pd.NA

    return anonymize_value(category, "processo")


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [
        normalize_category(column)
        for column in cleaned.columns
    ]
    return cleaned


def load_flow_data() -> pd.DataFrame:
    require_file(FLOW_FILE)

    flow = pd.read_excel(FLOW_FILE)
    flow = clean_column_names(flow)

    flow["DATAHORAINICIOATIVIDADE"] = pd.to_datetime(
        flow["DATAHORAINICIOATIVIDADE"],
        dayfirst=True,
        errors="coerce",
    )
    flow["DATAHORAFIMATIVIDADE"] = pd.to_datetime(
        flow["DATAHORAFIMATIVIDADE"],
        dayfirst=True,
        errors="coerce",
    )
    flow["DURACAO_MINUTOS"] = (
        flow["DATAHORAFIMATIVIDADE"] - flow["DATAHORAINICIOATIVIDADE"]
    ).dt.total_seconds() / 60

    category_columns = [
        "ATIVIDADE",
        "PROCEDIMENTO",
        "SITUACAOFLUXO",
    ]
    for column in category_columns:
        flow[column] = flow[column].map(normalize_category)

    flow["NOMEPROCESSO"] = flow["NOMEPROCESSO"].map(
        lambda value: anonymize_value(value, "nome_processo")
    )
    flow["IDREGISTROCONTROLADO"] = flow["IDREGISTROCONTROLADO"].map(generalize_process_category)
    flow["USUARIO"] = flow["USUARIO"].map(lambda value: anonymize_value(value, "usuario"))
    flow["JUSTIFICATIVA"] = flow["JUSTIFICATIVA"].notna()
    flow = flow.rename(columns={"JUSTIFICATIVA": "TEM_JUSTIFICATIVA"})

    return flow


def load_inspections_data() -> pd.DataFrame:
    require_file(INSPECTIONS_FILE)

    workbook = pd.ExcelFile(INSPECTIONS_FILE)
    frames = []

    for sheet_name in workbook.sheet_names:
        if sheet_name in SKIP_INSPECTION_SHEETS:
            continue

        sheet = pd.read_excel(INSPECTIONS_FILE, sheet_name=sheet_name)
        sheet["ABA_ORIGEM"] = sheet_name
        frames.append(sheet)

    inspections = pd.concat(frames, ignore_index=True)
    inspections = clean_column_names(inspections)

    date_columns = ["DATA_DA_INSPECAO", "DATA_DE_EXECUCAO"]
    for column in date_columns:
        inspections[column] = pd.to_datetime(
            inspections[column],
            dayfirst=True,
            errors="coerce",
        )

    category_columns = [
        "TIPO",
        "INTERNO_OU_EXTERNO",
        "TIPO_DE_ERRO",
        "GRAVIDADE",
        "DESVIO_DE_ATENCAO",
        "REVERSAO",
        "ABA_ORIGEM",
    ]
    for column in category_columns:
        inspections[column] = inspections[column].map(normalize_category)

    inspections["TIPO_DE_AUTORIZACAO"] = inspections["TIPO_DE_AUTORIZACAO"].map(
        generalize_process_category
    )
    inspections["CPF_CNPJ"] = inspections["CPF_CNPJ"].map(
        lambda value: anonymize_value(value, "documento")
    )
    inspections["COLABORADOR"] = inspections["COLABORADOR"].map(
        lambda value: anonymize_value(value, "colaborador")
    )
    inspections["INSPETOR"] = inspections["INSPETOR"].map(
        lambda value: anonymize_value(value, "inspetor")
    )
    inspections["COORDENACAO"] = inspections["COORDENACAO"].map(
        lambda value: anonymize_value(value, "coordenacao")
    )
    inspections["LIDERANCA"] = inspections["LIDERANCA"].map(
        lambda value: anonymize_value(value, "lideranca")
    )
    inspections["COOP"] = inspections["COOP"].map(
        lambda value: anonymize_value(value, "coop")
    )
    inspections["TEM_DESCRICAO"] = inspections["DESCRICAO"].notna()
    inspections = inspections.drop(columns=["DESCRICAO"])

    return inspections


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    flow = load_flow_data()
    inspections = load_inspections_data()

    flow_output = PROCESSED_DIR / "fluxos_limpos.csv"
    inspections_output = PROCESSED_DIR / "inspecoes_limpas.csv"

    flow.to_csv(flow_output, index=False)
    inspections.to_csv(inspections_output, index=False)

    print("Arquivos tratados gerados:")
    print(flow_output)
    print(inspections_output)
    print()
    print("Resumo:")
    print(f"fluxos: {len(flow)} linhas")
    print(f"inspecoes: {len(inspections)} linhas")
    print(f"erros em inspecoes: {(inspections['GRAVIDADE'] != 'SEM_ERRO').sum()}")


if __name__ == "__main__":
    main()
