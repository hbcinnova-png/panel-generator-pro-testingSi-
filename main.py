from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr, Field, field_validator

app = FastAPI(title="Pagina ABB", description="Página web y API para crear paneles animados", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

THEMES: Dict[str, Dict[str, Any]] = {
    "doctor-piscinas": {"name": "Doctor Piscinas", "colors": ["#ff006e", "#00d9ff"]},
    "tech-future": {"name": "Tech Future", "colors": ["#00d9ff", "#9d00ff"]},
    "luxury-gold": {"name": "Luxury Gold", "colors": ["#1a1a1a", "#d4af37"]},
    "nature-green": {"name": "Nature Green", "colors": ["#2d5016", "#52b788"]},
    "gaming-neon": {"name": "Gaming Neon", "colors": ["#0a0e27", "#00ff88"]},
}
PANELS: Dict[str, Dict[str, Any]] = {}

class PanelCreate(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1, max_length=500)
    phone: str = Field(..., min_length=3, max_length=40)
    email: EmailStr
    website: Optional[str] = None
    theme: str = "doctor-piscinas"
    panel_title: Optional[str] = None
    enable_animations: bool = True

    @field_validator("business_name", "description", "phone")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Campo obligatorio vacío")
        return value

    @field_validator("theme")
    @classmethod
    def valid_theme(cls, value: str) -> str:
        if value not in THEMES:
            raise ValueError("Tema inválido")
        return value

class Panel(PanelCreate):
    id: str
    created_at: str
    status: str

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail, "status_code": exc.status_code, "timestamp": datetime.utcnow().isoformat()})

@app.get("/", response_class=HTMLResponse)
async def home() -> str:
    opts = "".join(f'<option value="{k}">{v["name"]}</option>' for k, v in THEMES.items())
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pagina ABB</title><style>*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui;background:linear-gradient(135deg,#090b12,#24114d);color:white}}main{{max-width:920px;margin:auto;padding:22px}}section{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);border-radius:22px;padding:20px;margin:15px 0}}h1{{font-size:54px;margin:0;background:linear-gradient(90deg,#00d9ff,#ff006e,#d4af37);-webkit-background-clip:text;color:transparent}}input,select,textarea{{width:100%;padding:13px;border-radius:13px;border:1px solid #333;background:#0d1120;color:white}}label{{display:block;margin-top:10px;font-weight:800}}button,a{{display:inline-block;margin-top:14px;border:0;border-radius:13px;padding:13px 16px;background:#00d9ff;color:#06111d;font-weight:900;text-decoration:none}}pre{{white-space:pre-wrap;background:#0d1120;padding:12px;border-radius:13px}}</style></head><body><main><section><h1>Pagina ABB</h1><p>Aplicación limpia para crear paneles animados. Preparada para Render.</p><a href="/docs">Ver API</a></section><section><h2>Crear panel</h2><form id="f"><label>Negocio</label><input name="business_name" value="ABB Demo"><label>Descripción</label><textarea name="description">Panel generado desde Pagina ABB.</textarea><label>Teléfono</label><input name="phone" value="+34 600 000 000"><label>Email</label><input name="email" value="demo@abb.es"><label>Web</label><input name="website" value="https://example.com"><label>Tema</label><select name="theme">{opts}</select><label>Título</label><input name="panel_title" value="Panel ABB"><button>Generar panel</button></form></section><section><h2>Resultado</h2><pre id="r">Pendiente.</pre></section></main><script>f.onsubmit=async e=>{{e.preventDefault();let d=Object.fromEntries(new FormData(f).entries());d.enable_animations=true;let x=await fetch('/api/panels',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}});r.textContent=JSON.stringify(await x.json(),null,2)}}</script></body></html>'''

@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "Pagina ABB", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/themes")
async def list_themes() -> List[Dict[str, Any]]:
    return [{"id": key, **value} for key, value in THEMES.items()]

@app.post("/api/panels", response_model=Panel)
async def create_panel(payload: PanelCreate) -> Dict[str, Any]:
    panel_id = str(uuid4())
    panel = {**payload.model_dump(), "id": panel_id, "panel_title": payload.panel_title or payload.business_name, "created_at": datetime.utcnow().isoformat(), "status": "published"}
    PANELS[panel_id] = panel
    return panel

@app.get("/api/panels", response_model=List[Panel])
async def list_panels(skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
    return list(PANELS.values())[skip: skip + limit]

@app.get("/api/panels/{panel_id}", response_model=Panel)
async def get_panel(panel_id: str) -> Dict[str, Any]:
    if panel_id not in PANELS:
        raise HTTPException(status_code=404, detail="Panel no encontrado")
    return PANELS[panel_id]

@app.put("/api/panels/{panel_id}", response_model=Panel)
async def update_panel(panel_id: str, payload: PanelCreate) -> Dict[str, Any]:
    if panel_id not in PANELS:
        raise HTTPException(status_code=404, detail="Panel no encontrado")
    PANELS[panel_id].update(payload.model_dump())
    PANELS[panel_id]["panel_title"] = payload.panel_title or payload.business_name
    return PANELS[panel_id]

@app.delete("/api/panels/{panel_id}")
async def delete_panel(panel_id: str) -> Dict[str, str]:
    if panel_id not in PANELS:
        raise HTTPException(status_code=404, detail="Panel no encontrado")
    del PANELS[panel_id]
    return {"message": "Panel eliminado"}

@app.get("/api/stats")
async def stats() -> Dict[str, Any]:
    return {"total_panels": len(PANELS), "total_themes": len(THEMES), "api_version": "1.0.0", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import os
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
