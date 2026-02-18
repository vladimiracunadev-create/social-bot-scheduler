# 🐳 Análisis de Recursos Docker (Total vs. Actual)

Este documento detalla el consumo de recursos (Disco y RAM) del proyecto **Social Bot Scheduler**. Se ha ajustado para reflejar la diferencia entre el estado actual de tu entorno y el potencial total del repositorio para que reclutadores y novatos tomen decisiones informadas.

## 🏁 Estado del Entorno Docker

> [!WARNING]
> Tu entorno actual puede estar "incompleto" si solo has descargado algunos servicios. Para ejecutar el laboratorio completo, debes considerar el **Tamaño Real Total**.

| Escenario | Almacenamiento (Disco) | RAM Sugerida | Notas |
|-----------|------------------------|--------------|-------|
| **Estado Parcial** | Variable (~600 MB - 1 GB) | 4 GB | Solo servicios básicos o un caso individual. |
| **Repositorio Total** | **~8.0 GB** | **16 GB** | Los 18+ servicios, 8 bases de datos y herramientas de observabilidad. |

---

## 🏗️ Desglose Exhaustivo de Almacenamiento (Potential)

Si decides hacer un `docker-compose --profile full pull`, este es el impacto en disco:

### 🖼️ Imágenes (Total: ~6.8 GB)
| Categoría | Imágenes | Tamaño Est. |
|-----------|----------|-------------|
| **Orquestación** | n8n (v2.7.5) | 580 MB |
| **Bases de Datos Pesadas** | MSSQL (2022) + Cassandra (4.1) | 2.8 GB |
| **Bases de Datos Medias** | MySQL, MariaDB, MongoDB, Postgres | 2.0 GB |
| **Observabilidad** | Prometheus, Grafana, cAdvisor | 650 MB |
| **Microservicios (Destinos)** | PHP, Alpine, Node, Python, Ruby, Go | 800 MB |

### 💾 Volúmenes y Persistencia (Total: ~1.2 GB)
- **Caché de Construcción**: ~500 MB (Capas intermedias de Dockerfiles personalizados).
- **Datos de DBs**: ~500 MB (Espacio reservado para persistencia de los 8 motores).
- **Configuración**: ~200 MB (Logs, n8n workflows, grafana dashboards).

---

## 🚦 Decisión de Implementación: ¿Todo o Caso a Caso?

Para usuarios con recursos limitados, recomendamos la **Activación por Perfiles** (`profiles`):

1.  **Novato (Ligero)**: `docker-compose --profile case01 up -d`
    *   *Consumo*: ~1.2 GB Disco / 1.5 GB RAM Total.
2.  **Reclutador (Estándar)**: Casos 01 al 06.
    *   *Consumo*: ~4.0 GB Disco / 8 GB RAM.
3.  **Senior (Full Lab)**: Todos los casos + Infraestructura.
    *   *Consumo*: ~8.0 GB Disco / 16 GB RAM.

---

## 💡 Recomendaciones para Reclutadores
*   **Si solo quieres ver la lógica**: Evalúa el **Caso 01 (Python/PHP/MySQL)** o **Caso 04 (Node/FastAPI/SQLite)**. Son los más ligeros y rápidos de desplegar.
*   **Si quieres ver robustez**: Activa el **Caso 07 (Cassandra)** o **08 (MSSQL)** para observar cómo el sistema maneja bases de datos de alta demanda.
