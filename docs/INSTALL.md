# 📦 Guía de Instalación — Social Bot Scheduler

Esta guía describe el despliegue del laboratorio en sus diferentes modalidades. El sistema está diseñado para ser **Local-First** y **Secure-by-Default**.

---

## 🏗️ 1. Selección del Perfil de Despliegue

### 🛡️ Opción A: Core Seguro (Mínimo)
Ideal para desarrollo de nuevos flujos sin sobrecargar el sistema.
```bash
cp .env.example .env
docker-compose up -d
```
**Servicios activos**: `n8n` y el `Master Dashboard`.

### 🚀 Opción B: Laboratorio Completo (Demo)
Activa la matriz completa de 9 casos y el stack de observabilidad.
```bash
cp .env.demo.example .env
make up
```
**Efecto**: Levanta 20+ contenedores con persistencia políglota y métricas en tiempo real.

---

## 🔐 2. Configuración de Seguridad (Variables de Entorno)

> [!IMPORTANT]
> Antes del primer arranque, personaliza las siguientes variables en tu archivo `.env`:

| Variable | Propósito | Requerido |
| :--- | :--- | :---: |
| `N8N_OWNER_EMAIL` | Acceso inicial al orquestador. | ✅ |
| `N8N_OWNER_PASSWORD`| Contraseña maestra de n8n. | ✅ |
| `INTEGRATION_API_KEY`| Token de autenticación del Gateway (Caso 09). | ✅ |
| `GRAFANA_ADMIN_PASSWORD`| Acceso al stack de observabilidad. | 🟡 |

---

## 🌐 3. Configuración de Acceso Remoto (Edge Profile)

Si necesitas exponer el laboratorio de forma controlada mediante un **Reverse Proxy (Caddy)**:

1. **Generar Credenciales**:
   ```bash
   docker run --rm caddy:2.10.2-alpine caddy hash-password --plaintext 'TuPasswordFuerte'
   ```
2. **Configurar Hash**: Pega el resultado en la variable `EDGE_BASIC_AUTH_HASH` del `.env`.
3. **Desplegar**:
   ```bash
   make up-edge
   ```

---

## 🔒 4. Nota para usuarios Windows

El repositorio incluye `.gitattributes` que fuerza LF en scripts shell, Python, Go y otros archivos de código. Git aplica esta conversión automáticamente al clonar. Sin embargo, si tu editor convierte archivos `.sh` a CRLF, los scripts fallarán dentro de los contenedores Linux con:

```
/bin/sh^M: bad interpreter: No such file or directory
```

**Solución**: configura tu editor para respetar `.gitattributes`, o comprueba los line endings antes de hacer push:
```bash
git diff --check
```

## 🐍 5. Instalación del Entorno de Scripting (Local)

Para ejecutar o depurar los bots (`origin`) fuera de Docker (recomendado para desarrollo rápido):

```bash
# Crear y activar entorno virtual
python -m venv venv
# Linux/macOS: source venv/bin/activate
# Windows: venv\Scripts\activate

# Instalar dependencias base
pip install -r requirements.txt
```

---

## 🚢 6. Consideraciones para Kubernetes

Aunque el laboratorio se valida principalmente en Docker, incluimos manifiestos en `k8s/` para entornos de orquestación.

- **Segmentación**: Aplica `NetworkPolicies` estrictas.
- **Secretos**: No utilices valores de la plantilla `demo` en clústeres compartidos.
- **Hardening**: Revisa las guías de [Seguridad Runtime](./RUNTIME_SECURITY.md) antes del despliegue.

---
*Manual de despliegue v4.0 — Social Bot Scheduler*
