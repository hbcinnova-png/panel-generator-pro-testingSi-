from typing import List
from pydantic import BaseModel


class DiagnosticReport(BaseModel):
    status: str
    errores_detectados: List[str]
    archivos_sospechosos: List[str]
    rutas_rotas: List[str]
    causa_probable: str
    siguiente_accion: str


class FixProposal(BaseModel):
    archivos_a_modificar: List[str]
    descripcion_parche: str
    requiere_reinicio: bool


class RepairResult(BaseModel):
    status: str
    archivos_modificados: List[str]
    backup_creado: bool
    logs: List[str]


class AuditReport(BaseModel):
    status: str
    health_ok: bool
    rutas_validadas: List[str]
    observaciones: str
