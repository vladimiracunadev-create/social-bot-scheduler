# 🐳 Análisis de Recursos Docker (Total vs. Actual)

### ☢️ Comando de Liberación Total (Un solo paso)
Si deseas borrar **todo rastro** (imágenes base, volúmenes, contenedores y caché) y recuperar ~10GB de espacio:
```bash
make nuke
```
*(O directamente: `docker system prune -a -f --volumes`)*

Este documento detalla el consumo de recursos (Disco y RAM) del proyecto **Social Bot Scheduler**.
 Se ha ajustado para reflejar la diferencia entre el estado actual de tu entorno y el potencial total del repositorio para que reclutadores y novatos tomen decisiones informadas.

## 🏁 Estado del Entorno Docker

> [!WARNING]
> Tu entorno actual puede estar "incompleto" si solo has descargado algunos servicios. Para ejecutar el laboratorio completo, debes considerar el **Tamaño Real Total**.

### 🧹 Gestión de Recursos y Limpieza
Dada la alta demanda técnica de este repositorio (8 bases de datos simultáneas), es vital saber cómo liberar recursos:
- Consulta la [Guía de Recursos Docker](file:///c:/dev/social-bot-scheduler/docs/DOCKER_RESOURCES.md) para ver el reporte de estrés y límites.
- Usa `make clean` o `python hub.py clean` para una limpieza estándar.
- Usa `docker system prune -a -f --volumes` para una limpieza total (Deep Cleanup).

Este documento detalla el consumo de recursos (Disco y RAM) del proyecto **Social Bot Scheduler**. Se ha ajustado para reflejar la diferencia entre el estado actual de tu entorno y el potencial total del repositorio para que reclutadores y novatos tomen decisiones informadas.

## 🏁 Estado del Entorno Docker

> [!WARNING]
> Tu entorno actual puede estar "incompleto" si solo has descargado algunos servicios. Para ejecutar el laboratorio completo, debes considerar el **Tamaño Real Total**.

| Escenario | Almacenamiento (Disco) | RAM Sugerida | Notas |
|-----------|------------------------|--------------|-------|
| **Estado Parcial** | Variable (~600 MB - 1 GB) | 4 GB | Solo servicios básicos o un caso individual. |
| **Repositorio Total** | **~8.0 GB** | **16 GB** | Los 19+ servicios, 8 bases de datos externas, 1 gateway con DuckDB y herramientas de observabilidad. |

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
- **Datos de DBs**: ~550 MB (Espacio reservado para persistencia de los 8 motores externos y DuckDB embebida).
- **Configuración**: ~200 MB (Logs, n8n workflows, grafana dashboards).

---

## 📊 Consumo de RAM por Caso (Activación Selectiva)

> [!TIP]
> Cada caso se levanta con `docker-compose --profile caseXX up -d`. Las cifras incluyen el **núcleo siempre activo** (`n8n` 1 GB + `master-dashboard` 128 MB ≈ **1.13 GB**). Si ya tienes el núcleo arriba, súmale solo la columna *Δ Caso*.

| Caso | Receptor | Δ Receptor | Base de Datos | Δ DB | **Δ Caso** | **Total con núcleo** | Categoría |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **01** | PHP | 128 MB | MySQL | 512 MB | **640 MB** | ~1.75 GB | 🟢 Ligero |
| **02** | Go | 64 MB | MariaDB | 256 MB | **320 MB** | ~1.45 GB | 🟢 Ligero |
| **03** | Node.js | 128 MB | PostgreSQL | 256 MB | **384 MB** | ~1.5 GB | 🟢 Ligero |
| **04** | FastAPI | 128 MB | SQLite (embebida) | 0 MB | **128 MB** | ~1.25 GB | 🟢 Ligero |
| **05** | React + Node | 128 MB | MongoDB | 256 MB | **384 MB** | ~1.5 GB | 🟢 Ligero |
| **06** | Symfony | 128 MB | Redis | 64 MB | **192 MB** | ~1.3 GB | 🟢 Ligero |
| **07** | Ruby | 128 MB | Cassandra | **2 GB** | **2.13 GB** | ~3.25 GB | 🔴 Pesado |
| **08** | Flask | 128 MB | SQL Server | **2 GB** | **2.13 GB** | ~3.25 GB | 🔴 Pesado |
| **09** | FastAPI Gateway | 256 MB | DuckDB (embebida) | 0 MB | **256 MB** | ~1.4 GB | 🟢 Ligero |

> [!IMPORTANT]
> **Casos 07 y 08** son los únicos "pesados" del laboratorio: cada uno consume **~3.25 GB** por culpa de Cassandra/SQL Server. Si tu máquina tiene <8 GB de RAM disponibles, evita ejecutarlos en paralelo con otros casos.

### 🎯 Combinaciones recomendadas según RAM disponible

| RAM libre | Combinación sugerida | Total estimado |
| :---: | :--- | :---: |
| **2 GB** | Solo núcleo + 1 caso ligero (ej. case04) | ~1.25 GB |
| **4 GB** | Núcleo + 3-4 casos ligeros (01, 02, 04, 06) | ~2.5 GB |
| **8 GB** | Núcleo + todos los ligeros (01-06, 09) | ~4 GB |
| **16 GB** | `--profile full` (incluye 07/08 y observabilidad) | ~10 GB |

### 🚧 Estimaciones para casos planificados (10-20)

> [!WARNING]
> Cifras estimadas, sin medición real (los casos no están implementados todavía). Ver [PLANNED_CASES.md](PLANNED_CASES.md).

| Caso | Stack resumido | Δ Caso (est.) | Total con núcleo (est.) |
| :---: | :--- | :---: | :---: |
| **10** | Spring Boot + Ktor + PostgreSQL | ~1.0 GB | ~2.15 GB 🟡 |
| **11** | Phoenix + Cowboy + Mnesia | ~384 MB | ~1.5 GB 🟢 |
| **12** | LLM producer + FastAPI RAG + pgvector | ~1.5 GB | ~2.65 GB 🟡 |
| **13** | Node + Kafka + Go + ClickHouse | **~2.2 GB** | **~3.35 GB 🔴** |
| **14** | Next.js + Supabase local stack | **~2.25 GB** | **~3.4 GB 🔴** |
| **15** | Go gRPC + Python gRPC + CockroachDB | ~832 MB | ~2.0 GB 🟡 |
| **16** | Apollo + Hasura + TimescaleDB | ~768 MB | ~1.9 GB 🟢 |
| **17** | Rust MQTT + Node + Mosquitto + InfluxDB | ~736 MB | ~1.85 GB 🟢 |
| **18** | Zig + Crystal + Neo4j | ~608 MB | ~1.75 GB 🟢 |
| **19** | F# + Clojure + XTDB | ~1.5 GB | ~2.65 GB 🟡 |
| **20** | Swift Vapor + Dart Shelf + Firebase emulator | ~1.4 GB | ~2.55 GB 🟡 |

**Implementar los 11 simultáneamente** requeriría ~25 GB de RAM adicionales sobre el `--profile full` actual.

---

### ➕ Componentes opcionales

| Servicio | RAM | Cuándo se añade |
| :--- | :---: | :--- |
| Prometheus | 256 MB | `--profile observability` o `full` |
| Grafana | 512 MB | `--profile observability` o `full` |
| cAdvisor | 128 MB | `--profile observability` o `full` |
| Caddy edge proxy | ~80 MB | `--profile edge` |

> [!NOTE]
> Los [casos planificados 10–20](PLANNED_CASES.md) no se contabilizan aquí (no tienen perfiles aún). Estimación bruta si todos se implementaran: **+6 a +8 GB adicionales** por la incorporación de Kafka, ClickHouse, CockroachDB, Neo4j, XTDB y Firebase Emulator.

---

## 🚦 Decisión de Implementación: ¿Todo o Caso a Caso?

Para usuarios con recursos limitados, recomendamos la **Activación por Perfiles** (`profiles`):

1.  **Novato (Ligero)**: `docker-compose --profile case01 up -d`
    *   *Consumo*: ~1.2 GB Disco / 1.5 GB RAM Total.
    *   Si solo quieres el core del laboratorio, `make up-secure` deja fuera observabilidad y casos pesados.
2.  **Reclutador (Estándar)**: Casos 01 al 06.
    *   *Consumo*: ~4.0 GB Disco / 8 GB RAM.
3.  **Senior (Full Lab)**: Todos los casos + Infraestructura.
    *   *Consumo*: ~8.0 GB Disco / 16 GB RAM.
4.  **Edge Controlado**: `make up-edge` además del modo base.
    *   *Consumo*: añade ~50-100 MB de RAM para Caddy y no sustituye el hardening de producción.

---

## 🏁 Reporte de Prueba de Estrés (Stress Test - Feb 2026)

Se realizó una ejecución del stack completo (`--profile full`) en el hardware actual, resultando en los siguientes hallazgos críticos:

| Hallazgo | Impacto | Causa Raíz |
| :--- | :--- | :--- |
| **Estabilidad General** | **17/20 Servicios OK** | Los servicios clave (n8n, Dashboard, DBs ligeras) operan sin problemas. |
| **Falla en Cassandra** | **Cerrado Forzoso (OOM)** | Alcanzó el límite de 2GB de RAM configurado, provocando un exit (137). |
| **Falla en Case 07/08** | **Inestabilidad en Ruby/Flask** | Al caer Cassandra y subir el consumo general, los emisores/receptores dependientes fallaron. |
| **Consumo de Disco** | **~8.5 GB** | Incluye imágenes descargadas y capas de construcción de Dockerfiles. |

> [!IMPORTANT]
> **Conclusión**: El hardware actual es ideal para el **Perfil Óptimo** (Casos 01-06). Para el **Perfil Experto** (Todo el repo), se recomienda una máquina con al menos 16-24 GB de RAM (ej: Mac Mini con Silicon) para evitar la caída de servicios pesados como Cassandra.

---

## 🧹 Limpieza y Liberación de Recursos

Antes de apagar el sistema o migrar de máquina, es fundamental limpiar los recursos para devolver el disco y la memoria al sistema operativo.

### Opción 1: Vía Makefile (Recomendado)
```bash
make clean
```

### Opción 2: Vía HUB CLI
```bash
python hub.py clean
```

### Opción 3: Limpieza Total (Deep Cleanup)
Si deseas liberar **todo** el espacio (incluyendo imágenes base como MSSQL, Cassandra y PHP) para que la máquina quede como si nunca hubiera ejecutado el repo:

```bash
# ADVERTENCIA: Esto borrará todas las imágenes no usadas por otros contenedores activos
docker system prune -a -f --volumes
```

### ¿Qué hace este proceso?
1.  **Detiene y elimina** todos los contenedores del proyecto.
2.  **Elimina los volúmenes** (borrando todos los datos de las bases de datos).
3.  **Limpia imágenes huérfanas** y redes temporales.
4.  **Prune -a**: Elimina imágenes base, liberando hasta 10GB+ de espacio.
