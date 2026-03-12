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

## 🚦 Decisión de Implementación: ¿Todo o Caso a Caso?

Para usuarios con recursos limitados, recomendamos la **Activación por Perfiles** (`profiles`):

1.  **Novato (Ligero)**: `docker-compose --profile case01 up -d`
    *   *Consumo*: ~1.2 GB Disco / 1.5 GB RAM Total.
2.  **Reclutador (Estándar)**: Casos 01 al 06.
    *   *Consumo*: ~4.0 GB Disco / 8 GB RAM.
3.  **Senior (Full Lab)**: Todos los casos + Infraestructura.
    *   *Consumo*: ~8.0 GB Disco / 16 GB RAM.

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
