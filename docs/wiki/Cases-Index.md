# 🧩 Índice de la Matriz Tecnológica

Bienvenidos a la cartografía del **Social Bot Scheduler**. Este laboratorio se compone de 9 ejes de integración que demuestran la ductilidad de la orquestación moderna.

---

## 🏗️ Matriz de Integración (E2E)

| ID | Flujo (Origen -> Puente -> Destino) | Puerto | Persistencia | Nivel de Complejidad |
| :--- | :--- | :--- | :--- | :--- |
| **01** | Python -> **n8n** -> PHP | `8081` | 🐬 **MySQL** | 🟢 Inicial |
| **02** | Python -> **n8n** -> Go | `8082` | 🍃 **MariaDB** | 🟢 Inicial |
| **03** | Go -> **n8n** -> Node.js | `8083` | 🐘 **Postgres** | 🟡 Intermedio |
| **04** | Node.js -> **n8n** -> FastAPI | `8084` | 📂 **SQLite** | 🟡 Intermedio |
| **05** | Laravel -> **n8n** -> React | `8085` | 🍃 **MongoDB** | 🟡 Intermedio |
| **06** | Go -> **n8n** -> Symfony | `8086` | 🏎️ **Redis** | 🟡 Intermedio |
| **07** | Rust -> **n8n** -> Ruby | `8087` | 👁️ **Cassandra**| 🔴 Avanzado |
| **08** | C# (.NET) -> **n8n** -> Flask | `8088` | 🏢 **SQL Server**| 🔴 Avanzado |
| **09** | Python -> **n8n** -> FastAPI Gateway| `8090` | 🦆 **DuckDB** | 🔴 Avanzado |

---

## 🔬 Caso de Estudio: Integración Gateway (Caso 09)

El **Caso 09** es el pináculo arquitectónico del laboratorio, demostrando:
- **🔐 Seguridad de Bordes**: Verificación de `X-API-Key` y tokens en el gateway.
- **🛡️ Guardrails Totales**: Implementación de circuit breaker, idempotencia y DLQ en un solo flujo.
- **🏗️ Patrón DDD**: Gateway diseñado bajo los principios de *Domain-Driven Design*.
- **📊 Persistencia Analítica**: Uso de **DuckDB** para almacenamiento OLAP ligero.

---

## 🚦 Guía de Exploración

1.  **Añade flujos**: Sigue el [Manual de Activación](../../COMO_ACTIVAR_WORKFLOWS.md).
2.  **Lanza bots**: Utiliza el comando `python hub.py ejecutar <id>`.
3.  **Audita estados**: Verifica la persistencia en los dashboards correspondientes (`:8081-8090`).

---
*Catálogo técnico v4.1 — Social Bot Scheduler*
