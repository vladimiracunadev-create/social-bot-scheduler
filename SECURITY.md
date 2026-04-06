# 🛡️ Security Policy — Social Bot Scheduler

Este repositorio es un **laboratorio de ingeniería** con múltiples servicios y componentes. El hardening de seguridad se enfoca en reducir el riesgo operativo sin sacrificar el valor didáctico del ecosistema.

---

## 🛡️ Postura de Seguridad

A partir de la versión `4.0.0`, el proyecto implementa un estándar de **Hardening por Defecto**.

### 🔒 Secure-Default
- **Red Privada**: Todos los puertos de red se bindean exclusivamente a `127.0.0.1`.
- **Gestión de Secretos**: Eliminación de contraseñas hardcodeadas; uso obligatorio de variables de entorno (`.env`).
- **Surface Reduction**: Los componentes de observabilidad (Prometheus/Grafana) son opt-in.
- **Bootstrap Seguro**: n8n se configura dinámicamente sin credenciales predecibles en el código fuente.

### 🧪 Demo-Local
El perfil `demo-local` (usando `.env.demo.example`) es para **workshops controlados**.
- ⚠️ **ADVERTENCIA**: No debe usarse en entornos de nube pública o Internet sin capas adicionales de seguridad.

---

## 🏗️ Matriz de Superficie de Ataque

| Componente | Nivel de Riesgo | Exposición Local | Recomendación |
| :--- | :--- | :--- | :--- |
| **n8n** | 🔴 ALTO | Puerto 5678 | Proteger con Basic Auth / MFA |
| **cAdvisor** | 🔴 CRÍTICO | Puerto 8089 | **Nunca exponer.** Tiene acceso al Socket Docker. |
| **Grafana** | 🟡 MEDIO | Puerto 3000 | Configurar admin/password robustos en `.env`. |
| **Dashboards** | 🟢 BAJO | Puertas 8080-8090 | Solo visualización de datos de prueba. |

---

## 🚫 Lo que NO debe exponerse a Internet

> [!CAUTION]
> No publiques directamente ninguno de los puertos del laboratorio (5678, 3000, 9090, 8089, 8080-8090).

Si es estrictamente necesario el acceso remoto, implementa:
1. **Reverse Proxy**: Caddy/Nginx con TLS forzado.
2. **Autenticación**: Basic Auth o Authelia.
3. **Firewall**: Filtrado por IP (Whitelist).
4. **Segmentación**: Aislamiento a nivel de red Docker.

---

## 📂 Gestión de Secretos

Contamos con dos plantillas de configuración:
- `[.env.example](.env.example)`: Estándar para desarrollo seguro.
- `[.env.demo.example](.env.demo.example)`: Configuración para demostraciones rápidas.

> [!IMPORTANT]
> Nunca incluyas el archivo `.env` en el control de versiones. Asegúrate de que esté listado en `.gitignore`.

---

## 🐛 Reporte de Vulnerabilidades

Si encuentras una falla de seguridad:
1. **No la divulgues públicamente** de inmediato.
2. Abre un **Security Advisory** en GitHub o contacta al mantenedor.
3. Proporciona:
   - Resumen del problema.
   - Pasos para reproducir.
   - Impacto potencial.

---

## ⚙️ Recomendaciones Operativas

| Acción | Comando Recomendado |
| :--- | :--- |
| Desarrollo Seguro | `make up-secure` |
| Monitoreo Local | `make up-observability` |
| Acceso Remoto Controlado | `make up-edge` |

---

*Seguridad gestionada proactivamente por Vladimir Acuña*
