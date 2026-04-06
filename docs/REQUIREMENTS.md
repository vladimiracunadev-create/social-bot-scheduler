# 💻 Requisitos del Sistema — Social Bot Scheduler

Este documento detalla las especificaciones mínimas y recomendadas de hardware y software para garantizar la ejecución fluida del laboratorio políglota.

---

## 🏗️ Requisitos de Hardware

Ejecutar más de 20 contenedores simultáneamente (incluyendo 8 motores de bases de datos heterogéneos) es una tarea intensiva en recursos. El sistema permite **Carga Selectiva** mediante perfiles para ajustarse a máquinas con menos recursos.

| Componente | Perfil Mínimo (1 Caso) | Perfil Estándar (Demo) | Perfil Total (9 Casos + Obs) |
| :--- | :--- | :--- | :--- |
| **CPU** | 2 Cores | 4 Cores | 4-8 Cores |
| **RAM** | 4 GB | 8 GB | **16 GB** |
| **Disco** | 2 GB | 5 GB | **8-10 GB** |

---

## ⚡ Notas de Gestión de Recursos

> [!WARNING]
> **Consumo Crítico**: Los motores **MSSQL** y **Cassandra** son los mayores consumidores de memoria. En nuestra configuración optimizada, están limitados a 2GB de RAM cada uno mediante límites de Docker Compose.

- **Carga Selectiva**: Utiliza `make up-case-01` o `docker-compose --profile case01 up` para operar con el consumo mínimo de recursos (aprox. 4GB RAM).
- **Optimización**: Se recomienda cerrar aplicaciones pesadas (Chrome, IDEs, etc.) antes de lanzar el perfil `full` en máquinas de 8GB.

---

## 🛠️ Dependencias de Software

### Núcleo Obligatorio
- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**: v24.0 o superior (Recomendado).
- **[Python 3.10+](https://www.python.org/downloads/)**: Necesario para el HUB CLI y los emisores de origen.
- **[Git](https://git-scm.com/downloads)**: Para la gestión del repositorio y sincronización de cambios.

### Herramientas Opcionales
- **Make**: Para ejecutar los atajos del `Makefile` (`make up`, `make clean`, `make doctor`).
- **Navegador Web Moderno**: Chrome, Edge o Firefox para interactuar con los Dashboards.

---

## 🧹 Mantenimiento y Purga de Recursos

Para garantizar un rendimiento óptimo y liberar espacio en disco tras una sesión de evaluación masiva, utiliza los comandos de limpieza profunda:

```bash
# Limpiar contenedores y volúmenes (vía Makefile)
make clean

# Purga total de imágenes huérfanas (vía HUB CLI)
python hub.py clean
```

---
*Especificaciones técnicas v4.0 — Social Bot Scheduler*
