# System Requirements

This document outlines the minimum and optimal hardware/software requirements for running the **Social Bot Scheduler** laboratory.

## 💻 Hardware Requirements

Running 20 containers simultaneously (including 8 different database engines) is a resource-intensive task.

| Component | Mínimo (Por caso) | Óptimo (Estándar) | Máximo (Todo el Repo) |
| :--- | :--- | :--- | :--- |
| **CPU** | 2 Cores | 4 Cores | 4-8 Cores |
| **RAM** | 4 GB | 8 GB | **16 GB** |
| **Disco** | 2 GB | 5 GB | **8-10 GB** |

> [!TIP]
> Para un desglose detallado de cada servicio, consulta el [Análisis de Recursos Docker](DOCKER_RESOURCES.md).

### ⚠️ Resource Management Notes
- **MSSQL & Cassandra**: These are the heaviest consumers. In our optimized `docker-compose.yml`, they are capped at 2GB each.
- **Selective Loading**: Use `docker-compose --profile case01 up` to run with only 4GB of RAM.
- **Background Tasks**: Close heavy applications (Chrome, IDs) before running the `full` profile on 8GB machines.

## 🛠️ Software Requirements

### Core Dependencies
- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**: Mandatory (v24.0+ recommended).
- **[Python 3.10+](https://www.python.org/downloads/)**: Required for the HUB CLI and Emisores.
- **[Git](https://git-scm.com/downloads)**: To clone and manage the repository.

### Optional Tools
- **Make**: To use the `Makefile` shortcuts (`make up`, `make clean`, `make doctor`).
- **Web Browser**: Chrome/Edge/Firefox for the Dashboard.

## 🧹 Maintenance & Optimization

To guarantee optimal performance, it is recommended to run the cleanup command periodically:

```bash
# Via Makefile
make clean

# Via HUB CLI
python hub.py clean
```

This will remove all containers, volumes, and images to reclaim disk space and ensure a fresh start.
