from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

from config import DIAGNOSTICS_DIR, FLOW_FILE, INSPECTIONS_FILE


SKIP_INSPECTION_SHEETS = {"Listas", "CRONOGRAMA"}


def ensure_output_dirs() -> None:
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {path}\n"
            "Copie o arquivo original para data/raw/ usando o nome esperado no README."
        )


def normalize_column_name(column: object) -> str:
    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


def inspect_workbook(path: Path) -> pd.DataFrame:
    workbook = pd.ExcelFile(path)
    rows = []

    for sheet_name in workbook.sheet_names:
        sample = pd.read_excel(path, sheet_name=sheet_name, nrows=20)
        rows.append(
            {
                "file": path.name,
                "sheet": sheet_name,
                "sample_rows": len(sample),
                "columns_count": len(sample.columns),
                "columns": ", ".join(map(str, sample.columns)),
            }
        )

    return pd.DataFrame(rows)


def summarize_flow_file(path: Path) -> dict[str, object]:
    df = pd.read_excel(path)

    started_at = pd.to_datetime(
        df["DATAHORAINICIOATIVIDADE"],
        dayfirst=True,
        errors="coerce",
    )
    finished_at = pd.to_datetime(
        df["DATAHORAFIMATIVIDADE"],
        dayfirst=True,
        errors="coerce",
    )
    duration_minutes = (finished_at - started_at).dt.total_seconds() / 60

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "min_started_at": started_at.min(),
        "max_started_at": started_at.max(),
        "unique_users": df["USUARIO"].nunique(dropna=True),
        "unique_process_types": df["IDREGISTROCONTROLADO"].nunique(dropna=True),
        "median_duration_minutes": duration_minutes.median(),
        "mean_duration_minutes": duration_minutes.mean(),
    }


def load_inspection_sheets(path: Path) -> pd.DataFrame:
    workbook = pd.ExcelFile(path)
    frames = []

    for sheet_name in workbook.sheet_names:
        if sheet_name in SKIP_INSPECTION_SHEETS:
            continue

        sheet = pd.read_excel(path, sheet_name=sheet_name)
        sheet["ABA_ORIGEM"] = sheet_name
        frames.append(sheet)

    return pd.concat(frames, ignore_index=True)


def summarize_categorical_values(df: pd.DataFrame, columns: list[str], output_prefix: str) -> None:
    for column in columns:
        if column not in df.columns:
            continue

        counts = df[column].value_counts(dropna=False).reset_index()
        counts.columns = [column, "rows"]
        counts.to_csv(DIAGNOSTICS_DIR / f"{output_prefix}_{normalize_column_name(column)}.csv", index=False)


def summarize_inspections_file(path: Path) -> dict[str, object]:
    inspections = load_inspection_sheets(path)

    missing_percent = (
        inspections.isna()
        .mean()
        .mul(100)
        .round(1)
        .sort_values(ascending=False)
        .reset_index()
    )
    missing_percent.columns = ["column", "missing_percent"]
    missing_percent.to_csv(DIAGNOSTICS_DIR / "inspections_missing_percent.csv", index=False)

    summarize_categorical_values(
        inspections,
        columns=[
            "INSPETOR",
            "COLABORADOR",
            "TIPO DE ERRO",
            "GRAVIDADE",
            "TIPO DE AUTORIZACAO",
            "INTERNO OU EXTERNO",
            "COORDENACAO",
            "LIDERANCA",
        ],
        output_prefix="inspections_values",
    )

    return {
        "rows": len(inspections),
        "columns": len(inspections.columns),
        "inspection_sheets": inspections["ABA_ORIGEM"].nunique(dropna=True),
        "unique_inspectors": inspections["INSPETOR"].nunique(dropna=True),
        "unique_collaborators": inspections["COLABORADOR"].nunique(dropna=True),
        "error_rows": int((inspections["GRAVIDADE"].astype(str).str.lower() != "sem erro").sum()),
    }


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    ensure_output_dirs()
    require_file(FLOW_FILE)
    require_file(INSPECTIONS_FILE)

    print_section("1. Estrutura dos arquivos")
    workbook_summary = pd.concat(
        [
            inspect_workbook(FLOW_FILE),
            inspect_workbook(INSPECTIONS_FILE),
        ],
        ignore_index=True,
    )
    workbook_summary.to_csv(DIAGNOSTICS_DIR / "workbook_sheets.csv", index=False)
    print(workbook_summary[["file", "sheet", "sample_rows", "columns_count"]].to_string(index=False))

    print_section("2. Resumo do arquivo de fluxos")
    flow_summary = summarize_flow_file(FLOW_FILE)
    for key, value in flow_summary.items():
        print(f"{key}: {value}")

    print_section("3. Resumo do arquivo de inspecoes")
    inspections_summary = summarize_inspections_file(INSPECTIONS_FILE)
    for key, value in inspections_summary.items():
        print(f"{key}: {value}")

    print_section("4. Arquivos gerados")
    for path in sorted(DIAGNOSTICS_DIR.glob("*.csv")):
        print(path.relative_to(DIAGNOSTICS_DIR.parents[1]))


if __name__ == "__main__":
    main()
