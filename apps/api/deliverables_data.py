"""Live deliverables catalog for sonata-001.

Three zones on one page (File 18, 2026-08-30):
  present  — working files for the in-progress period (xlsx dashboard, register, JE pack)
  scenarios — saved models. Empty until Phase 2. Never mock cifras.
  past     — official close packages. Empty until a period is posted.

Files live under DATA_DIR/deliverables/. Download is FileResponse, not R2.
"""
from pathlib import Path
from typing import Optional

CATALOG = [
    {
        "id": "dash-es-2026",
        "zone": "present",
        "period": "2026-07",
        "period_label": "Julio 2026 · EN CURSO",
        "name": "SonataMas_Dashboard_2026_ES.xlsx",
        "filename": "SonataMas_Dashboard_2026_ES.xlsx",
        "type": "xlsx",
        "note": "Tablero de cierre (Español). Ene–Jul REAL. No es un paquete de cierre firmado.",
        "stamp": None,
        "ready": True,
    },
    {
        "id": "dash-en-2026",
        "zone": "present",
        "period": "2026-07",
        "period_label": "July 2026 · IN PROGRESS",
        "name": "SonataMas_Dashboard_2026_EN.xlsx",
        "filename": "SonataMas_Dashboard_2026_EN.xlsx",
        "type": "xlsx",
        "note": "Same workbook, English labels. Not a signed close package.",
        "stamp": None,
        "ready": True,
    },
    {
        "id": "exc-jul-2026",
        "zone": "present",
        "period": "2026-07",
        "period_label": "Julio 2026 · EN CURSO",
        "name": "exception_register_2026-07.csv",
        "filename": "exception_register_2026-07.csv",
        "type": "csv",
        "note": "Cola RFR julio. EX-J07-11 y EX-J07-14 cerradas; el resto abierto.",
        "stamp": None,
        "ready": True,
    },
    {
        "id": "je-jul-2026",
        "zone": "present",
        "period": "2026-07",
        "period_label": "Julio 2026 · EN CURSO",
        "name": "July-2026-JE-Package-v2.md",
        "filename": "July-2026-JE-Package-v2.md",
        "type": "md",
        "note": "R-11-JUL, R-11-CATCHUP, R-14-JUL, AJ-J07-01, AJ-J06-REVERSE. Propuestos, no causados.",
        "stamp": None,
        "ready": True,
    },
]


def list_deliverables(data_dir: Path) -> list[dict]:
    out = []
    for item in CATALOG:
        path = data_dir / "deliverables" / item["filename"]
        rec = dict(item)
        rec["bytes"] = path.stat().st_size if path.exists() else 0
        rec["ready"] = bool(item["ready"] and path.exists())
        rec["size_label"] = _size_label(rec["bytes"]) if rec["ready"] else "—"
        out.append(rec)
    return out


def get_file(data_dir: Path, file_id: str) -> Optional[dict]:
    for rec in list_deliverables(data_dir):
        if rec["id"] == file_id:
            path = data_dir / "deliverables" / rec["filename"]
            rec["stored_path"] = str(path)
            rec["exists"] = path.exists()
            return rec
    return None


def zones_meta() -> dict:
    return {
        "present": {
            "id": "present",
            "title_es": "Actual",
            "title_en": "Current",
            "copy_es": "Tablero y cola del período en curso. Julio no está cerrado.",
            "copy_en": "Working dashboard and queue for the live period. July is not closed.",
        },
        "scenarios": {
            "id": "scenarios",
            "title_es": "Sus modelos",
            "title_en": "Your scenarios",
            "copy_es": "Ningún modelo guardado. El motor de escenarios (Phase 2) no está conectado. No se muestran cifras de demostración.",
            "copy_en": "No saved scenarios. The modeling engine (Phase 2) is not connected. No demo figures.",
        },
        "past": {
            "id": "past",
            "title_es": "Paquetes de cierre",
            "title_en": "Close packages",
            "copy_es": "No hay paquete de cierre oficial publicado. Saldo inicial bloqueado al 30-jun-2026. Julio EN CURSO — nada se ha causado a Alegra desde el portal.",
            "copy_en": "No official close package published. Opening balance locked 30 Jun 2026. July IN PROGRESS — nothing posted to Alegra from the portal.",
        },
    }


def _size_label(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"
