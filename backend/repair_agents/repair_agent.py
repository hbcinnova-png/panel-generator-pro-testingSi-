import os
from typing import Dict, List, Optional

from .logs import log_action
from .safety import SafetyProtocol, is_allowed_repair_target


class RepairAgent:
    """
    Agente reparador HBC3.

    Reglas:
    - No aplica parches falsos.
    - No toca producción.
    - Solo modifica archivos permitidos por whitelist.
    - Siempre crea backup antes de escribir.
    - Idempotente: no duplica imports ni include_router.
    """

    def propose_fix(self, diagnostico: Dict) -> Dict:
        log_action("REPAIR", "Propuesta", "Evaluando diagnóstico")

        errores = diagnostico.get("errores_detectados", [])
        rutas_rotas = diagnostico.get("rutas_rotas", [])

        archivos: List[str] = []
        descripcion = "No se requiere acción."
        requiere_reinicio = False

        main_file = self._find_main_file()

        if "/api/v1/repair/logs" in rutas_rotas:
            if main_file:
                archivos.append(main_file)
                descripcion = (
                    "Registrar router repair_agents en FastAPI usando include_router "
                    "con prefijo /api/v1/repair. Parche limitado a archivo principal permitido."
                )
                requiere_reinicio = True
            else:
                descripcion = (
                    "No se encontró archivo principal FastAPI permitido. "
                    "Buscar main.py, backend/main.py, backend/api.py o app/main.py."
                )
        elif rutas_rotas:
            descripcion = (
                "Hay rutas rotas que no pertenecen al módulo repair_agents. "
                "No aplicar parche automático. Revisar routers users/panels/auth."
            )
        elif errores:
            descripcion = (
                "Hay errores detectados, pero no hay una reparación automática segura. "
                "Revisar logs antes de tocar código."
            )

        return {
            "archivos_a_modificar": archivos,
            "descripcion_parche": descripcion,
            "requiere_reinicio": requiere_reinicio,
        }

    def apply_fix(self, propuesta: Dict) -> Dict:
        if SafetyProtocol.is_production():
            log_action("REPAIR", "Bloqueo", "Escritura automática bloqueada por entorno seguro")
            return {
                "status": "BLOQUEO_REAL",
                "archivos_modificados": [],
                "backup_creado": False,
                "logs": [
                    "Escritura bloqueada. Para staging real usa ENVIRONMENT=staging "
                    "y HBC3_ALLOW_REPAIR_WRITES=true."
                ],
            }

        descripcion = propuesta.get("descripcion_parche", "")
        archivos = propuesta.get("archivos_a_modificar", [])

        if not archivos:
            log_action("REPAIR", "Sin cambios", "No hay archivos propuestos")
            return {
                "status": "SIN_CAMBIOS",
                "archivos_modificados": [],
                "backup_creado": False,
                "logs": ["No hay archivos seguros para modificar."],
            }

        if "repair_agents" not in descripcion or "include_router" not in descripcion:
            log_action("REPAIR", "Bloqueo", "Descripción de parche no autorizada")
            return {
                "status": "BLOQUEO_REAL",
                "archivos_modificados": [],
                "backup_creado": False,
                "logs": [
                    "Parche bloqueado. Solo se permite registrar repair_agents con include_router."
                ],
            }

        archivos_modificados: List[str] = []
        backup_creado = False
        logs: List[str] = []

        for archivo in archivos:
            if not is_allowed_repair_target(archivo):
                logs.append(f"Ruta bloqueada por whitelist: {archivo}")
                log_action("REPAIR", "Ruta bloqueada", archivo)
                continue

            if not os.path.exists(archivo):
                logs.append(f"Archivo no encontrado: {archivo}")
                continue

            backup_path = SafetyProtocol.create_backup(archivo)
            backup_creado = True

            aplicado = self._ensure_repair_router_registered(archivo)

            if aplicado:
                archivos_modificados.append(archivo)
                logs.append(f"Router repair_agents registrado en {archivo}. Backup: {backup_path}")
                log_action("REPAIR", "Modificación", f"Router registrado en {archivo}")
            else:
                logs.append(
                    f"No se modificó {archivo}: router ya registrado o estructura no compatible."
                )

        status = "PARCHE_APLICADO" if archivos_modificados else "SIN_CAMBIOS"

        return {
            "status": status,
            "archivos_modificados": archivos_modificados,
            "backup_creado": backup_creado,
            "logs": logs,
        }

    def _find_main_file(self) -> Optional[str]:
        candidatos = ["main.py", "backend/main.py", "backend/api.py", "app/main.py"]

        for archivo in candidatos:
            if os.path.exists(archivo) and is_allowed_repair_target(archivo):
                return archivo

        return None

    def _ensure_repair_router_registered(self, filepath: str) -> bool:
        with open(filepath, "r", encoding="utf-8") as file:
            contenido = file.read()

        if "app.include_router(repair_router" in contenido:
            return False

        if "FastAPI(" not in contenido:
            return False

        import_line = "from backend.repair_agents.router import router as repair_router\n"
        include_line = (
            "\napp.include_router("
            "repair_router, "
            'prefix="/api/v1/repair", '
            'tags=["repair_agents"]'
            ")\n"
        )

        nuevo_contenido = contenido

        if import_line.strip() not in nuevo_contenido:
            nuevo_contenido = import_line + nuevo_contenido

        if "app.include_router(repair_router" not in nuevo_contenido:
            nuevo_contenido = nuevo_contenido.rstrip() + include_line

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(nuevo_contenido)

        return True
