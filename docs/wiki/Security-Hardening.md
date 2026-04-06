# 🛡️ Hardening de Seguridad — Social Bot Scheduler

Esta guía documenta los estándares de endurecimiento (**Hardening**) aplicados al laboratorio para garantizar un entorno de ejecución industrial, resiliente y libre de vulnerabilidades críticas.

---

## 🛡️ ¿Qué significa "Security: Hardened"?

En el contexto de este repositorio, el término **Hardened** (Endurecido) implica una postura de seguridad proactiva dividida en cuatro dimensiones críticas:

1.  **Aislamiento (Isolation)**: Los servicios operan exclusivamente en `127.0.0.1`, eliminando vectores de ataque externos por defecto.
2.  **Minimización (Surface Reduction)**: Uso de imágenes base `Alpine` y eliminación de binarios innecesarios en producción.
3.  **Privilegio Mínimo (Least Privilege)**: Ejecución mandatoria como usuario no-root (`botuser`) y sistemas de archivos de solo lectura siempre que es posible.
4.  **Auditoría Continua (Supply Chain)**: Escaneos automáticos de CVEs en cada cambio del código.

---

## 🛑 Mitigación de Ataques de Cadena de Suministro

> [!CAUTION]
> **Vulnerabilidad Trivy Detectada y Mitigada (Marzo 2026)**
> El sistema ha sido actualizado para neutralizar el compromiso global de `aquasecurity/trivy-action`. 
> - **Acción**: Migración mandatoria a la versión verificada **`v0.35.0`**.
> - **Impacto**: Protección total contra ataques de inyección de código vía "Tag Poisoning".

---

## 🏗️ Estrategia de Triple Capa de Seguridad

El hardening se aplica de forma granular en tres niveles del stack tecnológico:

### 1. Inmunidad a CVEs (Patching Permanente)
Nuestras imágenes Docker se limpian en dos niveles:
-   **📦 App Layer**: Uso de Entornos Virtuales (`venv`) con dependencias estrictas y cifradas.
-   **⚙️ System Layer**: Actualización activa de librerías críticas (`pip`, `setuptools`, `wheel`) en la etapa final de construcción.

### 2. Escaneo Proactivo (Triple Scan CI/CD)
El flujo de entrega continua realiza tres auditorías automáticas:
- **🛡️ Trivy**: Diagnóstico de vulnerabilidades en el SO y librerías de sistema.
- **🐍 pip-audit**: Auditoría profunda de vulnerabilidades en el ecosistema Python.
- **🔑 Gitleaks**: Escaneo preventivo para evitar la fuga accidental de secretos o llaves API.

### 3. Redes de Confianza Cero (Zero Trust)
- **NetworkPolicies**: Los manifiestos de Kubernetes implementan una denegación selectiva de tráfico persistente.
- **Proxy de Borde**: El perfil `edge` utiliza Caddy con TLS forzado y autenticación básica Bcrypt para accesos remotos controlados.

---

## 🛡️ Resiliencia y Defensa en Profundidad

La seguridad no es solo evitar ataques, sino garantizar que el sistema se recupere. El laboratorio integra **Guardrails** avanzados:
- **✅ Idempotencia**: Evita el procesamiento duplicado de eventos.
- **⚡ Circuit Breaker**: Protege el sistema contra cascadas de fallos en servicios externos.
- **📥 DLQ (Dead Letter Queue)**: Captura fallos irrecuperables para auditoría posterior.

---
*Manual de seguridad industrial v4.0 — Social Bot Scheduler*
