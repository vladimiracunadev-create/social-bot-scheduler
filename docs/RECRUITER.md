# 👔 Guía para Reclutadores Técnicos — Perfil de Ingeniería

> [!NOTE]
> **Propósito**: Este documento facilita la evaluación técnica del proyecto **Social Bot Scheduler**. Traduce la complejidad de un ecosistema políglota en valor empresarial tangible y proporciona un tour guiado de las capacidades demostradas.

---

## 🎯 Resumen Ejecutivo: El Lab de Interoperabilidad

**Social Bot Scheduler** es un laboratorio de ingeniería de software que demuestra **interoperabilidad multi-lenguaje y persistencia políglota a escala industrial**. 

### 💎 Diferenciadores de Valor
- **Agnoticismo Tecnológico**: Integración fluida de 8 lenguajes (Python, Go, Node, Rust, etc.) y 8 motores de bases de datos.
- **Resiliencia Enterprise**: Implementación nativa de patrones de tolerancia a fallos (Circuit Breakers, Idempotencia).
- **Seguridad Proactiva**: Mitigación en tiempo real de ataques de cadena de suministro (vulnerabilidad Trivy mitigada).
- **Kubernetes Ready**: Manifiestos de despliegue y hardening para clústeres de orquestación modernos.

---

## 💼 Matriz de Capacidades Técnicas

### 🏗️ Arquitectura y Patrones (CNCF Aligned)
El proyecto implementa **11 patrones arquitectónicos** críticos, documentados en [`docs/ARCHITECTURE.md`](ARCHITECTURE.md):

| Patrón | Implementación Técnica | Impacto |
| :--- | :--- | :--- |
| **Mediator** | n8n como orquestador central desacoplado. | Facilidad de mantenimiento. |
| **Polyglot Persistence**| MySQL, PostgreSQL, MongoDB, Redis, Cassandra. | Optimización por caso de uso. |
| **Resilience** | Circuit Breaker + Dead Letter Queues (DLQ). | Alta disponibilidad (HA). |
| **Observability** | Prometheus + Grafana + cAdvisor. | Monitoreo en tiempo real. |
| **DevSecOps** | Análisis estático, escaneo de imagen y linting. | Calidad de entrega continua. |

### 🔐 Seguridad y DevSecOps (Hardening)
- **Mitigación Supply Chain**: Resolución proactiva del compromiso de `aquasecurity/trivy-action` mediante upgrade a `v0.35.0` y auditoría de tags.
- **Zero Trust**: Bindeo exclusivo a `localhost` y segmentación de red Docker.
- **Surface Reduction**: Uso de imágenes base `Alpine` y ejecución como usuario no-root.

---

## 🛠️ Stack Tecnológico Polivalente

| Capa | Tecnologías Clave |
| :--- | :--- |
| **Lenguajes** | 🐍 Python, 🐹 Go, 🟢 Node.js, 🐘 PHP, 🦀 Rust, 💎 Ruby, 🟦 C# |
| **Databases** | 🐬 MySQL, 🍃 MongoDB, 🏎️ Redis, 🐘 Postgres, 👁️ Cassandra, 🏢 SQL Server |
| **Orchestration** | 🐳 Docker Compose, ☸️ Kubernetes (Kustomize), 🤖 n8n |
| **Monitoring** | 🔥 Prometheus, 📊 Grafana, 👁️ cAdvisor |

---

## 🔍 Tour de Código para Ingenieros de Staff

### 📁 [Caso 04: Node.js → FastAPI](https://github.com/vladimiracunadev-create/social-bot-scheduler/tree/main/cases/04-node-to-fastapi)
**Foco**: Integración de stacks modernos con validación de tipos asíncrona y persistencia relacional ligera.

### 📁 [Caso 07: Rust → Ruby Sinatra](https://github.com/vladimiracunadev-create/social-bot-scheduler/tree/main/cases/07-rust-to-ruby)
**Foco**: Seguridad de memoria en el origen (Rust) y flexibilidad de micro-frameworks en el destino (Ruby), con persistencia en NoSQL (Cassandra).

---

## 🧪 Evaluación Práctica en 5 Minutos

Para una validación E2E sin configuración previa:

```bash
# 1. Preparar Entorno
cp .env.demo.example .env

# 2. Desplegar Matriz Completa
docker-compose up -d

# 3. Validar Salud del Hub
make doctor

# 4. Ejecutar Smoke Test
make demo
```

> [!TIP]
> El sistema incluye un **Zero-Touch Setup**: n8n se configura automáticamente con los 9 flujos operativos al primer arranque.

---

## 📞 FAQ para Talent Acquisition

**¿Por qué elegir n8n como mediador?**
Permite orquestar sistemas políglotas visualmente, reduciendo la fricción entre equipos de diferentes stacks y facilitando el mantenimiento de la lógica de negocio.

**¿Cómo gestionas la seguridad en local?**
Mediante el script `check_runtime_security.py` que audita puertos, tags Docker y secretos antes de permitir cualquier ejecución en el laboratorio.

---
*Perfil técnico v4.1 — Social Bot Scheduler*
