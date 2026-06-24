from typing import Optional

from fastapi import APIRouter, HTTPException

from .audit_agent import AuditAgent
from .diagnostic_agent import DiagnosticAgent
from .logs import get_logs
from .repair_agent import RepairAgent
from .schemas import AuditReport, DiagnosticReport, FixProposal, RepairResult

router = APIRouter(tags=["Repair Agents"])


@router.post("/diagnose", response_model=DiagnosticReport)
async def diagnose_system():
    agente = DiagnosticAgent()
    return await agente.run()


@router.post("/propose-fix", response_model=FixProposal)
async def propose_fix():
    agente_diag = DiagnosticAgent()
    diagnostico = await agente_diag.run()

    agente_rep = RepairAgent()
    return agente_rep.propose_fix(diagnostico)


@router.post("/apply-fix", response_model=RepairResult)
async def apply_fix(propuesta: Optional[FixProposal] = None):
    """
    Seguridad:
    El servidor recalcula diagnóstico y propuesta.
    No confía en rutas arbitrarias enviadas desde frontend.
    """

    agente_diag = DiagnosticAgent()
    diagnostico = await agente_diag.run()

    agente_rep = RepairAgent()
    propuesta_servidor = agente_rep.propose_fix(diagnostico)

    if propuesta is not None:
        if hasattr(propuesta, "model_dump"):
            propuesta_cliente = propuesta.model_dump()
        else:
            propuesta_cliente = propuesta.dict()

        if propuesta_cliente != propuesta_servidor:
            return {
                "status": "BLOQUEO_REAL",
                "archivos_modificados": [],
                "backup_creado": False,
                "logs": [
                    "Payload de cliente rechazado. El servidor recalcula la propuesta "
                    "y no acepta rutas arbitrarias."
                ],
            }

    try:
        return agente_rep.apply_fix(propuesta_servidor)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/audit", response_model=AuditReport)
async def audit_system():
    agente = AuditAgent()
    return await agente.run()


@router.get("/logs")
async def fetch_logs():
    return {"logs": get_logs()}
