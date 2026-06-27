# Pagina ABB

Aplicación limpia FastAPI + página web para crear paneles animados.

## Ejecutar local

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Endpoints

- `/` página web
- `/health` estado
- `/docs` documentación
- `/api/themes` temas
- `/api/panels` CRUD de paneles
- `/api/stats` estadísticas

## Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```
