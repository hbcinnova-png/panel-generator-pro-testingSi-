from typing import Dict, List

import httpx

from .logs import log_action


class AuditAgent:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    async def run(self) -> Dict:
        log_action("AUDIT", "Inicio", "Validando post-reparación")

        rutas_validadas: List[str] = []
        observaciones: List[str] = []
        health_ok = False

        endpoints = [
            "/health",
            "/api/v1/repair/logs",
            "/api/v1/users",
            "/api/v1/panels",
        ]

        async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
            for endpoint in endpoints:
                try:
                    response = await client.get(endpoint)

                    if endpoint == "/health":
                        health_ok = response.status_code == 200

                    if response.status_code in [200, 401]:
                        rutas_validadas.append(endpoint)
                    elif response.status_code == 404:
                        observaciones.append(f"{endpoint} devuelve 404 Not Found")
                    elif response.status_code >= 500:
                        observaciones.append(f"{endpoint} devuelve error {response.status_code}")
                    else:
                        observaciones.append(f"{endpoint} devuelve estado {response.status_code}")

                except Exception as exc:
                    observaciones.append(
                        f"Fallo de conexión en {endpoint}: {type(exc).__name__}: {exc}"
                    )

        if health_ok and "/api/v1/repair/logs" in rutas_validadas:
            status = "APTO PARA TESTING"
        elif health_ok:
            status = "NO VALIDADO COMPLETO"
        else:
            status = "NO APTO"

        log_action("AUDIT", "Fin", f"Estado final: {status}")

        return {
            "status": status,
            "health_ok": health_ok,
            "rutas_validadas": rutas_validadas,
            "observaciones": (
                " | ".join(observaciones)
                if observaciones
                else "Sistema levantado y rutas principales verificadas."
            ),
        }
