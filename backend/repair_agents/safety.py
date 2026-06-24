import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from .logs import log_action


FORBIDDEN_PATH_PARTS = [
    ".env",
    "secrets",
    "credentials",
    "private_key",
    "id_rsa",
    "wp-config.php",
    "database.sql",
    "dump.sql",
]

FORBIDDEN_EXTENSIONS = [
    ".pem",
    ".key",
    ".crt",
]

ALLOWED_REPAIR_FILES = {
    "main.py",
    "backend/main.py",
    "backend/api.py",
    "app/main.py",
}


def normalize_relative_path(path: str) -> str:
    return Path(path).as_posix().lstrip("./")


def is_safe_relative_path(path: str) -> bool:
    if not path or not path.strip():
        return False

    normalized = Path(path)

    if normalized.is_absolute():
        return False

    if ".." in normalized.parts:
        return False

    lowered = path.lower()

    for forbidden in FORBIDDEN_PATH_PARTS:
        if forbidden.lower() in lowered:
            return False

    for extension in FORBIDDEN_EXTENSIONS:
        if lowered.endswith(extension):
            return False

    return True


def is_allowed_repair_target(path: str) -> bool:
    if not is_safe_relative_path(path):
        return False

    return normalize_relative_path(path) in ALLOWED_REPAIR_FILES


def filter_safe_files(paths: List[str]) -> List[str]:
    return [path for path in paths if is_safe_relative_path(path)]


class SafetyProtocol:
    @staticmethod
    def repairs_allowed() -> bool:
        """
        Fail-closed HBC3.

        Por defecto todo entorno se trata como producción.
        Solo permite escritura automática si:
        ENVIRONMENT=staging/development/dev/local/testing
        y HBC3_ALLOW_REPAIR_WRITES=true
        """
        env = os.getenv("ENVIRONMENT", "production").lower().strip()
        allow_writes = os.getenv("HBC3_ALLOW_REPAIR_WRITES", "false").lower().strip()
        safe_envs = {"staging", "development", "dev", "local", "testing"}

        return env in safe_envs and allow_writes == "true"

    @staticmethod
    def is_production() -> bool:
        return not SafetyProtocol.repairs_allowed()

    @staticmethod
    def create_backup(filepath: str) -> str:
        if not is_allowed_repair_target(filepath):
            raise ValueError(f"Ruta no permitida para backup/reparación: {filepath}")

        source = Path(filepath)
        if not source.exists():
            raise FileNotFoundError(f"Archivo no encontrado para backup: {filepath}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = normalize_relative_path(filepath).replace("/", "__")

        backup_dir = Path(".hbc3_backups")
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / f"{safe_name}.{timestamp}.bak"
        shutil.copy2(source, backup_path)

        log_action("SAFETY", "Backup creado", str(backup_path))
        return str(backup_path)
