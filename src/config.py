import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = Path(os.getenv("AUDITFLOW_RAW_DIR", DATA_DIR / "raw"))
PROCESSED_DIR = DATA_DIR / "processed"
DATABASE_DIR = DATA_DIR / "database"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

FLOW_FILE = RAW_DIR / "volume_fluxos.xlsx"
INSPECTIONS_FILE = RAW_DIR / "inspecoes_202511.xlsx"

DIAGNOSTICS_DIR = OUTPUTS_DIR / "diagnostics"
