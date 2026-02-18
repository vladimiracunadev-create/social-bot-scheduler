# 📔 Índice de la Matriz Tecnológica

Descubre por qué hemos elegido estas combinaciones y qué beneficios aporta cada una a tu flujo de trabajo.

---

## 📊 Comparativa de Emisores (Origen)
| Tecnología | Caso | Ventaja | Uso Recomendado |
| :--- | :--- | :--- | :--- |
| **Python** | 01, 02 | Facilidad de scripting y librerías robustas (Pydantic). | Prototipado rápido y validación de tipos compleja. |
| **Go** | 03, 06 | Binario único, ultra-rápido y concurrente. | Sistemas embebidos o servidores de alta carga. |
| **Node.js** | 04 | Manejo asíncrono nativo excelente. | Integración con otros servicios JS existentes. |
| **Laravel** | 05 | Framework PHP ultra-productivo. | Aplicaciones SaaS empresariales. |
| **Rust** | 07 | Seguridad de memoria y rendimiento. | Sistemas críticos y de baja latencia. |
| **C# (.NET)** | 08 | Ecosistema empresarial maduro. | Integraciones corporativas y servicios Windows. |

---

## 🛠️ Comparativa de Receptores (Destino)
| Tecnología | Dashboard | Persistencia (DB) | Por qué elegirlo |
| :--- | :--- | :--- | :--- |
| **PHP (Vanilla)** | 8081 | **MySQL** | Universalidad y simplicidad máxima. |
| **Go** | 8082 | **MariaDB** | Eficiencia extrema y drivers nativos Go. |
| **Node.js** | 8083 | **PostgreSQL** | Flexibilidad y manejo de JSONB. |
| **FastAPI** | 8084 | **SQLite** | Velocidad Python con BD embebida. |
| **React (Express)** | 8085 | **MongoDB** | Ecosistema MERN (Mongo/Express/React/Node). |
| **Symfony** | 8086 | **Redis** | Alto rendimiento y estados en memoria. |
| **Ruby (Sinatra)** | 8087 | **Cassandra** | Escalabilidad lineal y alta disponibilidad. |
| **Flask** | 8088 | **SQL Server** | Integración Enterprise robusta. |

---

## 🗄️ Paradigmas de Almacenamiento
En esta v4.0, hemos implementado una **Persistencia Políglota**:
- **SQL (ACID)**: Usamos MySQL, MariaDB, Postgres y SQL Server para demostrar transaccionalidad.
- **NoSQL (Documental)**: MongoDB permite esquemas dinámicos para posts complejos.
- **NoSQL (Wide-Column)**: Cassandra demuestra almacenamiento distribuido masivo.
- **K/V (Cache)**: Redis se usa para estados ultra-rápidos.
- **Embedded**: SQLite para soluciones sin servidor de base de datos externo.

## 🔄 El Rol de n8n
En todos los casos, **n8n** actúa como la capa de abstracción. Esto significa que puedes cambiar el Emisor o el Receptor (y su base de datos) sin que tus flujos de publicación en Facebook, Twitter o Slack se rompan. Es el seguro de vida de tu automatización.
