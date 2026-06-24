import asyncio
import os
from typing import Dict, List
from urllib.parse import urlparse

import httpx

from .logs import log_action


class DiagnosticAgent:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(5.0, connect=2.0)

    async def run(self) -> Dict:
        log_action("DIAGNOSTIC", "Inicio", "Comprobando endpoints internos")

        errores: List[str] = []
        rutas_rotas: List[str] = []
        archivos_sospechosos: List[str] = []

        endpoints = [
            "/health",
            "/api/v1/users",
            "/api/v1/panels",
            "/api/v1/repair/logs",
        ]

        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            for endpoint in endpoints:
                resultado = await self._check_endpoint_with_retries(client, endpoint)
                status_code = resultado.get("status_code")
                error = resultado.get("error")

                if error:
                    errores.append(error)
                    continue

                if status_code == 404:
                    rutas_rotas.append(endpoint)
                    errores.append(f"404 Not Found en {endpoint}")
                elif status_code == 401:
                    errores.append(f"401 Unauthorized en {endpoint}")
                elif status_code and status_code >= 500:
                    errores.append(f"Error {status_code} en {endpoint}")

        errores.extend(await self._check_database_config_safe())

        candidatos_main = [
            "main.py",
            "backend/main.py",
            "backend/api.py",
            "app/main.py",
        ]

        for archivo in candidatos_main:
            if os.path.exists(archivo):
                archivos_sospechosos.append(archivo)

        if not archivos_sospechosos:
            archivos_sospechosos = candidatos_main

        status = "OK" if not errores else "REQUIERE_REPARACION"

        if rutas_rotas:
            causa = "Rutas no registradas, router no incluido o endpoints inexistentes."
            siguiente = "Llamar a /api/v1/repair/propose-fix"
        elif errores:
            causa = "Revisar autenticación, base de datos, servidor o logs backend."
            siguiente = "Revisar logs antes de aplicar reparación."
        else:
            causa = "No se detectan errores críticos."
            siguiente = "Ninguna."

        log_action("DIAGNOSTIC", "Fin", f"Estado: {status}, errores: {len(errores)}")

        return {
            "status": status,
            "errores_detectados": errores,
            "archivos_sospechosos": archivos_sospechosos,
            "rutas_rotas": rutas_rotas,
            "causa_probable": causa,
            "siguiente_accion": siguiente,
        }

    async def _check_endpoint_with_retries(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        retries: int = 2,
    ) -> Dict:
        last_error = None

        for attempt in range(retries + 1):
            try:
                response = await client.get(endpoint)
                return {"status_code": response.status_code, "error": None}
            except Exception as exc:
                last_error = f"Fallo de conexión en {endpoint}: {type(exc).__name__}: {exc}"
                if attempt < retries:
                    await asyncio.sleep(0.25)

        return {"status_code": None, "error": last_error}

    async def _check_database_config_safe(self) -> List[str]:
        """
        Chequeo DB seguro y no bloqueante.
        No abre conexiones pesadas ni cuelga FastAPI.
        """
        errores: List[str] = []

        database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
        db_host = os.getenv("DB_HOST")
        db_port = int(os.getenv("DB_PORT", "5432"))

        if not database_url and not db_host:
            errores.append(
                "DB_CONFIG_NO_DETECTADA: No se detecta DATABASE_URL, POSTGRES_URL ni DB_HOST."
            )
            return errores

        host = db_host
        port = db_port

        if database_url:
            parsed = urlparse(database_url)
            host = parsed.hostname or host
            port = parsed.port or port

        if not host:
            errores.append("DB_HOST_NO_DETECTADO: No se pudo determinar host de base de datos.")
            return errores

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=1.5,
            )
            writer.close()
            await writer.wait_closed()
        except Exception as exc:
            errores.append(f"DB_CONEXION_FALLIDA: {type(exc).__name__}: {exc}")

        return errores
