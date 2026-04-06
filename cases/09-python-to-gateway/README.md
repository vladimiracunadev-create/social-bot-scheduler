# 🧩 Caso 09: 🐍 Python -> 🌉 n8n -> ⚡ FastAPI Gateway

[![Language: Python](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Database: DuckDB](https://img.shields.io/badge/Database-DuckDB-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)

Este eje tecnológico representa la cúspide de la integración del laboratorio: un emisor en **Python** publica hacia **n8n**, el cual aplica guardrails avanzados y reenvía la solicitud a un **Integration Gateway** en **FastAPI** protegido por `X-API-Key`.

---

## 🏗️ Arquitectura del Flujo

1.  **📤 Origen**: `bot.py` (Python 3.11) - Emisor operativo.
2.  **🌉 Puente**: **n8n** (Webhook + Guardrails + Reenvío Autenticado)
3.  **📥 Destino**: **FastAPI Gateway** (Integration Hub)
4.  **📁 Persistencia**: **DuckDB** (OLAP In-Process Database)

---

## 🔒 Seguridad y Configuración

> [!IMPORTANT]
> El Gateway requiere autenticación obligatoria. Asegúrate de configurar tus secretos antes de iniciar.

- **`INTEGRATION_API_KEY`**: Clave obligatoria para el acceso al Gateway (no se aceptan valores demo embebidos).
- **`GITHUB_TOKEN`**: Opcional, habilita el modo de proveedor real para publicaciones.

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

- **🌐 Gateway Dashboard**: [http://localhost:8090](http://localhost:8090)
- **⚙️ API Docs (Swagger)**: `http://localhost:8090/docs`
- **🦆 Data Analysis**: DuckDB permite realizar consultas analíticas sobre el histórico de posts con latencia casi nula.

---

*Desarrollado como parte del Social Bot Scheduler v4.0*
