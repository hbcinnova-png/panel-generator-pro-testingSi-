from datetime import datetime
from pathlib import Path
from typing import List

LOG_DIR = Path(".hbc3_logs")
LOG_FILE = LOG_DIR / "repair_audit.log"


def log_action(agente: str, accion: str, detalle: str) -> str:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    mensaje = f"[{timestamp}] [{agente}] {accion} - {detalle}\n"

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(mensaje)

    return mensaje


def get_logs() -> List[str]:
    if not LOG_FILE.exists():
        return ["No hay registros de reparación activos."]

    return LOG_FILE.read_text(encoding="utf-8").splitlines()
