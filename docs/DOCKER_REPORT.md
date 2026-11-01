# 📊 Reporte de Recursos Docker

> [!IMPORTANT]
> **Esto es una fotografía, no el estado actual.** Los números y los IDs de imagen de
> abajo se midieron durante la auditoría Docker de la v4.9.0. En la v4.11.0 se vació
> el entorno Docker por completo (8,34 GB liberados: 3 imágenes, 3 volúmenes y 112
> entradas de caché de build) y las versiones de imagen cambiaron en los 20 casos
> — ver [CVE_REMEDIATION_v4.11.0.md](CVE_REMEDIATION_v4.11.0.md). Las imágenes que
> aquí aparecen como `php:8.2-apache`, `node:20-alpine` o `alpine:3.20.6` ya no se
> usan. Para el estado real de tu máquina: `docker system df`.

Este documento detalla el uso de disco de los procesos, imágenes y volúmenes de Docker
en el entorno de desarrollo tal como estaba al cierre de la v4.9.0.

## 💾 Resumen de Uso del Sistema

| Tipo de Recurso | Total | Activos | Tamaño | Reclamable |
| :--- | :--- | :--- | :--- | :--- |
| **Imágenes** | 11 | 10 | 6.005 GB | 6.001 GB (99%) |
| **Contenedores** | 12 | 0 | 56.82 MB | 56.82 MB (100%) |
| **Volúmenes Locales** | 4 | 2 | 57.26 MB | 5.025 MB (8%) |
| **Caché de Build** | 61 | 0 | 1.718 GB | 803.2 MB |

> [!NOTE]
> Casi la totalidad del espacio ocupado por las imágenes (99%) es reclamable, lo que indica que existen múltiples versiones o imágenes sin uso activo por contenedores en ejecución.

## 🖼️ Imágenes Disponibles

| Imagen | ID | Uso de Disco | Tamaño Contenido |
| :--- | :--- | :--- | :--- |
| `n8nio/n8n:2.7.5` | `9220846479a4` | 1.73 GB | 248 MB |
| `grafana/grafana:11.2.0` | `9e1e77ade304` | 995 MB | 210 MB |
| `php:8.2-apache` | `46d9dd4b58c0` | 714 MB | 183 MB |
| `prom/prometheus:v2.54.1` | `1f0f50f06aca` | 503 MB | 134 MB |
| `node:20-alpine` | `09e2b3d97260` | 192 MB | 48.3 MB |
| `alpine:3.20.6` | `25109184c71b` | 13.1 MB | 3.95 MB |

### Casos de Integración (Destinos)

| Imagen | Uso de Disco |
| :--- | :--- |
| `social-bot-scheduler-dest-ruby` | 504 MB |
| `social-bot-scheduler-dest-fastapi` | 236 MB |
| `social-bot-scheduler-dest-node` | 207 MB |
| `social-bot-scheduler-dest-flask` | 200 MB |
| `social-bot-scheduler-dest-go` | 24.4 MB |

## 📦 Volúmenes Locales

| Nombre del Volumen | Driver |
| :--- | :--- |
| `social-bot-scheduler_grafana_data` | `local` |
| `social-bot-scheduler_n8n_data` | `local` |
| `b119daf7c4733a272...` | `local` |
| `d6eb6d645229e1868...` | `local` |

---
*Última actualización: 2026-02-15*
