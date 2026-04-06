# 🛡️ Security Policy — Social Bot Scheduler

Este repositorio es un **laboratorio de ingeniería** políglota. Nuestra postura de seguridad se enfoca en reducir el riesgo operativo mediante el **Hardening por Defecto** y el monitoreo constante de la cadena de suministro.

---

## 🛡️ Postura de Seguridad Industrial

A partir de la versión `4.0.0`, el proyecto implementa estándares de **Seguridad Runtime** agresivos:

### 🔒 Hardening por Defecto (Secure-by-Default)
- **Aislamiento de Red**: Todos los servicios se vinculan exclusivamente a `127.0.0.1` (localhost) para evitar exposición accidental.
- **Gestión de Secretos**: Uso mandatorio de variables de entorno via `.env`. No se permiten credenciales hardcodeadas.
- **Principio de Menor Privilegio**: Imágenes Docker optimizadas que ejecutan como usuarios no-root siempre que es posible.

---

## 🛑 Mitigación de Ataques de Cadena de Suministro (Trivy)

> [!CAUTION]
> **Aviso de Seguridad Crítica (Marzo 2026)**:
> Hemos detectado y mitigado proactivamente el compromiso de la acción `aquasecurity/trivy-action`. 
> 
> **Acciones tomadas por este sistema**:
> 1. **Upgrade Inmediato**: Hemos migrado de la versión comprometida (`0.33.1`) a la versión verificada y segura **`v0.35.0`**.
> 2. **Auditoría de CI/CD**: Se ha revisado el pipeline para asegurar que no existan más dependencias vulnerables a ataques de "tag-poisoning".
> 3. **Monitoreo Informado**: Este repositorio considera activamente las alertas de seguridad globales para proteger tu entorno de desarrollo.

---

## 🏗️ Matriz de Superficie de Ataque

| Componente | Riesgo | Puerto Local | Acción Recomendada |
| :--- | :--- | :--- | :--- |
| **n8n Orchestrator** | 🔴 ALTO | `5678` | Proteger con Basic Auth / MFA |
| **cAdvisor (Socket)** | 🔴 CRÍTICO | `8089` | **NUNCA EXPONER**. Acceso root a Docker. |
| **Prometheus/Grafana**| 🟡 MEDIO | `3000`/`9090` | Cambiar credenciales default en `.env`. |
| **Integration Hubs** | 🟢 BAJO | `8080-8090` | Visualización de casos de prueba. |

---

## 📂 Gestión de Secretos y Configuración

El proyecto provee plantillas de configuración para distintos escenarios:
- **[.env.example](.env.example)**: Configuración recomendada para desarrollo local seguro.
- **[.env.demo.example](.env.demo.example)**: Configuración rápida para workshops controlados.

> [!IMPORTANT]
> Nunca incluyas tu archivo `.env` real en el control de versiones. El sistema ignorará automáticamente estos archivos mediante el `.gitignore`.

---

## ⚙️ Recomendaciones Operativas

| Escenario | Comando | Nivel de Hardening |
| :--- | :--- | :--- |
| **Desarrollo Estándar** | `make up-secure` | 🛡️ Máximo |
| **Auditoría de Recursos** | `make up-observability` | 📊 Medio |
| **Acceso Remoto (Proxy)** | `make up-edge` | 🌐 Controlado |

---

## 🐛 Reporte de Vulnerabilidades

Si identificas un riesgo de seguridad en el laboratorio:
1. **Reporte Privado**: No abras un Issue público. Utiliza el sistema de **Security Advisories** de GitHub.
2. **Detalles**: Incluye pasos para reproducir y el impacto técnico estimado.

---
*Seguridad gestionada proactivamente por Vladimir Acuña — Software & Security Engineering*
