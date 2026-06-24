# HBC3 repair_agents

Estado: APTO PARA TESTING / NO VALIDADO EN PRODUCCIÓN.

Módulo instalado en:

backend/repair_agents/

Endpoints previstos:

- POST /api/v1/repair/diagnose
- POST /api/v1/repair/propose-fix
- POST /api/v1/repair/apply-fix
- POST /api/v1/repair/audit
- GET /api/v1/repair/logs

Reglas:

- No producción sin aprobación.
- Backups obligatorios.
- Logs obligatorios.
- Escritura solo en staging autorizado.
- No mock.
- No demo.

Siguiente paso:

Conectar router en el archivo principal FastAPI y validar endpoints.
