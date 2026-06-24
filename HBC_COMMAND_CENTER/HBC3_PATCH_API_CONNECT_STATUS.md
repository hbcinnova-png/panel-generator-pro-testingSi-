# HBC3 PATCH API CONNECT

Estado: CONECTADO

Archivo: `backend/api.py`

Router añadido:

```python
app.include_router(
    repair_router,
    prefix="/api/v1/repair",
    tags=["repair_agents"],
)
```

Estado: APTO PARA TESTING / NO VALIDADO EN PRODUCCIÓN.
