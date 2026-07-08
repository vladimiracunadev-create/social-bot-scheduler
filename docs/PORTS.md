# 🔌 Asignación de Puertos — Regla Canónica

Este documento es el **single source of truth** de los puertos del laboratorio. La regla es una fórmula determinista + un validador en CI que hace **imposible** que dos casos colisionen o que un caso se desvíe.

---

## 📐 La fórmula

```
puerto_host(caso) = 8080 + número_de_caso
```

| Caso | Puerto | | Caso | Puerto |
| :---: | :---: | :---: | :---: | :---: |
| 01 | 8081 | | 11 | 8091 |
| 02 | 8082 | | 12 | 8092 |
| 03 | 8083 | | 13 | 8093 |
| 04 | 8084 | | 14 | 8094 |
| 05 | 8085 | | 15 | 8095 |
| 06 | 8086 | | 16 | 8096 |
| 07 | 8087 | | 17 | 8097 |
| 08 | 8088 | | 18 | 8098 |
| 09 | 8089 | | 19 | 8099 |
| 10 | 8090 | | 20 | 8100 |

- **El número de caso se lee en el puerto** (caso 16 → 80**96**, caso 27 → 81**27**).
- Cada caso publica **un único** puerto host (el dashboard/receiver). Las bases de datos, brokers y motores (Hasura, Mosquitto, InfluxDB, TimescaleDB…) son **internos a la red Docker** y nunca se publican, así que no consumen puertos ni pueden colisionar.

---

## 🧱 Puertos de infraestructura (fuera de la banda de casos)

| Servicio | Puerto | Perfil |
| :--- | :---: | :--- |
| n8n | 5678 | core |
| Master Dashboard | 8080 | core |
| Grafana | 3000 | observability |
| Prometheus | 9090 | observability |
| **cAdvisor** | **9091** | observability |

> La banda de casos (8081+) no cruza ningún puerto de infraestructura hasta el **caso 1009** (donde tocaría Prometheus `9090`). En la práctica el esquema es ilimitado.

---

## 🚦 ¿Qué pasa al llegar al caso 20, 30 o más?

Nada se rompe, **por construcción**:

- **Caso 20** → `8100`, **caso 30** → `8110`, **caso 99** → `8179`. La fórmula sigue dando puertos únicos y consecutivos.
- Un caso nuevo **no necesita elegir** puerto: se deriva de su número. No hay decisiones manuales que puedan chocar.
- Antes de cada `push`, el CI ejecuta [`scripts/validate_ports.py`](../scripts/validate_ports.py), que **falla el build** si:
  1. El `port` de un `app.manifest.yml` no cumple `8080 + id`.
  2. Dos servicios publican el mismo puerto host (misma pareja puerto/protocolo).
  3. Un caso implementado no está cableado a su puerto de fórmula en `docker-compose.yml`.
  4. Un puerto de infraestructura cae sobre la banda de un caso.

Es decir: **cualquier colisión o desvío se detecta antes de levantar nada**.

---

## ✅ Al implementar un caso nuevo

1. En `app.manifest.yml`: `destination.port: <8080 + id>` y `url: http://localhost:<puerto>`.
2. En `docker-compose.yml`: `- "${HOST_BIND_IP:-127.0.0.1}:<puerto>:<puerto_interno>"`.
3. En `index.html` (objeto `CASES`): `port: <puerto>`.
4. Correr `python scripts/validate_ports.py` → debe salir `OK`.

Si el validador pasa, el caso encaja en el esquema sin posibilidad de romper a otro.

---

*Parte de **Social Bot Scheduler**. Regla introducida en `v4.5.1`.*
