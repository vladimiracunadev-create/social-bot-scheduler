# 👔 Guía para Reclutadores Técnicos

> **Propósito**: Este documento facilita la evaluación técnica del proyecto **Social Bot Scheduler** para procesos de selección. Traduce la complejidad técnica en valor empresarial y proporciona un tour guiado de las capacidades demostradas.

---

## 🎯 Resumen Ejecutivo

**Social Bot Scheduler** es un laboratorio de ingeniería de software que demuestra **interoperabilidad multi-lenguaje y políglota de datos a escala empresarial**. El proyecto implementa una matriz de 8 ejes de integración donde diferentes lenguajes de programación (Python, Go, Node.js, PHP, Rust, Ruby, C#) se comunican entre sí y persisten datos en 8 motores de bases de datos diferentes.

### Valor de Negocio
- **Reducción de silos tecnológicos**: Permite que equipos con diferentes stacks trabajen juntos sin fricciones
- **Escalabilidad horizontal**: Arquitectura modular que facilita agregar nuevos componentes sin afectar los existentes
- **Seguridad empresarial**: Implementa estándares de producción (CVE-free, Zero Trust, auditoría continua)
- **Portabilidad**: Despliegue consistente en Docker, Kubernetes y entornos locales

---

## 💼 Habilidades Técnicas Demostradas

### 🏗️ Arquitectura y Diseño
- **Arquitectura de Microservicios**: Diseño de sistemas distribuidos con comunicación asíncrona
- **Patrón Pub/Sub**: Implementación de bus de eventos mediante webhooks y n8n
- **Separación de Responsabilidades**: Arquitectura de 3 capas (Origen → Puente → Destino)
- **Persistencia Políglota**: Integración de 8 motores de base de datos (SQL, NoSQL, KV, Documental)
- **Diseño Modular**: 8 casos de integración independientes pero cohesivos

### 🔐 Seguridad y DevSecOps
- **Hardening de Contenedores**: Imágenes Docker sin vulnerabilidades (Trivy scan)
- **Principio de Mínimo Privilegio**: Ejecución como usuario no-root, filesystem read-only
- **Triple Capa de Auditoría**: Gitleaks + Trivy + pip-audit en CI/CD
- **Zero Trust Networking**: NetworkPolicies de Kubernetes con denegación por defecto
- **Validación de Entradas**: Protección contra Path Traversal y RCE en CLI
- **Resiliencia Industrial**: Implementación de Idempotencia y Circuit Breaker para tolerancia a fallos

### 🛠️ Stack Tecnológico Polivalente
| Categoría | Tecnologías |
|-----------|-------------|
| **Lenguajes** | Python, Go, Node.js, PHP, Rust, Ruby, C# |
| **Bases de Datos** | MySQL, MariaDB, PostgreSQL, SQLite, MongoDB, Redis, Cassandra, SQL Server |
| **Frameworks** | FastAPI, Express, Laravel, Symfony, Flask, Sinatra, .NET |
| **Orquestación** | n8n, Docker Compose, Kubernetes (Kustomize) |
| **CI/CD** | GitHub Actions, Pre-commit hooks, Automated testing |
| **Infraestructura** | Docker, Kubernetes, Makefile automation |

### 🚀 DevOps y Automatización
- **Containerización Multi-Stage**: Dockerfiles optimizados para producción
- **Orquestación Local y Cloud**: Docker Compose + Kubernetes manifests
- **Pipeline CI/CD Robusto**: Linting, testing, security scanning, build automation
- **CLI Personalizado**: Hub runner con comandos de diagnóstico y gestión

---

## 🔍 Tour Guiado: Casos de Evaluación Rápida

### 📌 Caso 01: Python → PHP (Integración Clásica)
**Ubicación**: [`cases/01-python-to-php/`](../cases/01-python-to-php)

**Qué evaluar**:
- **Emisor Python**: Uso de Pydantic para validación de datos, manejo de fechas, HTTP requests
- **Receptor PHP**: API REST vanilla, persistencia en **MySQL**, dashboard web
- **Integración**: Comunicación asíncrona mediante webhooks de n8n

**Comando de prueba rápida**:
```bash
.\hub.ps1 ejecutar-caso 01-python-to-php
```

### 📌 Caso 04: Node.js → FastAPI (Stack Moderno)
**Ubicación**: [`cases/04-node-to-fastapi/`](../cases/04-node-to-fastapi)

**Qué evaluar**:
- **Emisor Node.js**: Async/await, Axios, manejo de errores
- **Receptor FastAPI**: API con validación automática, persistencia en **SQLite**
- **Dashboard**: Visualización en tiempo real en `localhost:8084`

### 📌 Caso 07: Rust → Ruby (Lenguajes Especializados)
**Ubicación**: [`cases/07-rust-to-ruby/`](../cases/07-rust-to-ruby)

**Qué evaluar**:
- **Emisor Rust**: Manejo de memoria seguro, concurrencia, HTTP client
- **Receptor Ruby/Sinatra**: Framework minimalista, persistencia en **Cassandra**
- **Versatilidad**: Capacidad de trabajar con lenguajes de nicho

---

## 📊 Métricas y Logros Destacados

### ✅ Calidad de Código
- **CI/CD Verde**: Pipeline automatizado con 100% de tests pasando
- **Cobertura de Seguridad**: Sin vulnerabilidades CRITICAL/HIGH en build (verificado con Trivy)
- **Linting Automático**: Pre-commit hooks con Black, Flake8, isort
- **Documentación Completa**: 16 archivos de documentación técnica

### 🏆 Complejidad Técnica
- **8 Lenguajes de Programación**: Dominio de múltiples paradigmas y ecosistemas
- **8 Bases de Datos**: Integración de motores SQL, NoSQL y In-Memory
- **8 Casos de Integración**: Cada uno con su propio stack completo
- **Arquitectura Unificada**: Todos los casos comparten el mismo patrón de diseño
- **Zero-Touch Setup**: n8n se auto-configura con workflows pre-importados
- **Portabilidad Total**: Funciona en Windows, Linux y macOS

### 🔧 Operaciones y Mantenimiento
- **Makefile Centralizado**: 15+ comandos para desarrollo y deployment
- **Health Checks**: Sistema de diagnóstico automatizado (`hub.py doctor`)
- **Logs Estructurados**: Auditoría completa de operaciones
- **Rollback Seguro**: Versionado semántico y changelog detallado

---

## 🚦 Guía de Evaluación en 15 Minutos

### Paso 1: Revisión de Arquitectura (5 min)
1. Leer [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) para entender el patrón de 3 capas
2. Revisar diagrama Mermaid de flujo de datos
3. Examinar la matriz de casos implementados

### Paso 2: Inspección de Código (5 min)
1. **Seguridad**: Revisar [`SECURITY.md`](../SECURITY.md) y [`Dockerfile`](../Dockerfile)
2. **Calidad**: Examinar [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) y [`.github/workflows/ci-cd.yml`](../.github/workflows/ci-cd.yml)
3. **Código**: Revisar un caso completo (recomendado: Caso 01 o 04)

### Paso 3: Ejecución Práctica (5 min)
```bash
# Clonar repositorio
git clone https://github.com/vladimiracunadev-create/social-bot-scheduler.git
cd social-bot-scheduler

# Levantar todo (n8n se auto-configura con los 8 workflows)
docker-compose up -d

# Esperar ~30s y verificar
make smoke

# Ejecutar caso demo
make demo

# Verificar resultado en http://localhost:8081
```

> **Zero configuración manual**: No necesitas crear cuentas en n8n ni importar workflows.
> Credenciales de lab: `admin@social-bot.local` / `SocialBot2026!`

---

## 🎓 Contexto de Aprendizaje

Este proyecto fue desarrollado como un **laboratorio de experimentación técnica** para:
- Profundizar en arquitecturas distribuidas y microservicios
- Explorar la interoperabilidad entre lenguajes de programación
- Implementar prácticas de seguridad a nivel empresarial
- Dominar herramientas de DevOps y automatización

**No es un producto comercial**, sino una **demostración de capacidades técnicas** aplicables a entornos empresariales reales.

---

## 📞 Preguntas Frecuentes de Reclutadores

### ¿Por qué tantos lenguajes?
Demuestra versatilidad y capacidad de trabajar en equipos heterogéneos. En empresas grandes, es común que diferentes equipos usen diferentes stacks.

### ¿Es escalable a producción?
Sí. Incluye manifiestos de Kubernetes, health checks, logs estructurados, seguridad hardened y stack de observabilidad completo (Prometheus/Grafana).

### ¿Cuánto tiempo tomó desarrollar esto?
El proyecto evolucionó iterativamente. La **v4.0.0** representa un salto hacia la persistencia políglota, añadiendo 8 bases de datos en una sola fase de expansión.

### ¿Qué parte fue más desafiante?
La estandarización de seguridad en contenedores (eliminar CVEs) y la creación del HUB CLI con validación robusta de entradas.

---

## 🔗 Enlaces Rápidos

| Documento | Propósito |
|-----------|-----------|
| [`README.md`](../README.md) | Guía de inicio rápido |
| [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) | Diseño del sistema |
| [`SECURITY.md`](../SECURITY.md) | Estrategia de seguridad |
| [`docs/HUB.md`](HUB.md) | Documentación del CLI |
| [`CHANGELOG.md`](../CHANGELOG.md) | Historial de versiones |

---

**Última actualización**: Febrero 2026  
**Versión del proyecto**: v4.0.0  
**Repositorio**: [github.com/vladimiracunadev-create/social-bot-scheduler](https://github.com/vladimiracunadev-create/social-bot-scheduler)
