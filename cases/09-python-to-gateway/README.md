# 🧩 Caso 09: 🐍 Python -> 🌉 n8n -> ⚡ FastAPI Gateway

[![Language: Python](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Database: DuckDB](https://img.shields.io/badge/Database-DuckDB-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)

Este eje tecnológico representa la cúspide de la integración del laboratorio: un emisor en **Python** publica hacia **n8n**, el cual aplica guardrails avanzados y reenvía la solicitud a un **Integration Gateway** en **FastAPI** protegido por `X-API-Key`.

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen**: `bot.py` (Python 3.11) - Emisor operativo.
2. **🌉 Puente**: **n8n** (Webhook + Guardrails + Reenvío Autenticado)
3. **📥 Destino**: **FastAPI Gateway** (Integration Hub)
4. **📁 Persistencia**: **DuckDB** (OLAP In-Process Database)

---

## 🔒 Seguridad y Configuración

> [!IMPORTANT]
> El Gateway requiere autenticación obligatoria. Asegúrate de configurar tus secretos antes de iniciar.

- **`INTEGRATION_API_KEY`**: Clave obligatoria para el acceso al Gateway (no se aceptan valores demo embebidos).
- **`GITHUB_TOKEN`**: Opcional, habilita el modo de proveedor real para publicaciones.
- **`GATEWAY_WEBHOOK_RATE_LIMIT`** *(default `30/minute`)*: throttling por IP en `POST /webhook` (P-02).
- **`GATEWAY_ERRORS_RATE_LIMIT`** *(default `60/minute`)*: throttling por IP en `POST /errors` (P-02).

### 🛡️ Controles de seguridad (v4.4.0)

- **Rate limiting (`slowapi`)**: cada endpoint está protegido por límite de peticiones por IP; el excedente devuelve **HTTP 429**. Contiene el agotamiento de la cuota de la GitHub API y el abuso de una `X-API-Key` filtrada.
- **Whitelist de `owner`**: el campo `owner` de `RequestParamsDTO` se valida contra el patrón de usuario de GitHub (`^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$`) en el borde (pydantic → **422**), como defensa en profundidad sobre el value object `Owner` del dominio. Rechaza barras, `@` y encodings que pudieran redirigir la llamada saliente.
- **Dependencias con hash SHA**: `requirements.txt` se genera desde `requirements.in` con `pip-compile --generate-hashes` (P-01).

---

## 🚀 Ejecución en Laboratorio

Para un arranque rápido y seguro del Caso 09:

```bash
# 1. Preparar entorno
cp .env.demo.example .env

# 2. Levantar servicios
make up

# 3. Ejecutar demo de integración
make demo09
```

---

## 🚦 Verificación y Dashboards

- **🌐 Gateway Dashboard**: [http://localhost:8089](http://localhost:8089)
- **⚙️ API Docs (Swagger)**: `http://localhost:8089/docs`
- **🦆 Data Analysis**: DuckDB permite realizar consultas analíticas sobre el histórico de posts con latencia casi nula.

---

*Desarrollado como parte del Social Bot Scheduler — controles de seguridad al día en v4.4.0*
