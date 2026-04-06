# 📥 Guía de Importación Manual (n8n v2.7+)

Debido a los recientes cambios en la API de **n8n**, la importación automática de flujos puede requerir una intervención manual de **2 minutos**. Esta guía es el "Fast Track" para dejar tu laboratorio operativo.

---

## 🚀 Solución Rápida

### 1️⃣ Acceso y Setup Inicial
Navega a `http://localhost:5678`. Si el orquestador solicita credenciales por primera vez, utiliza:
- **📧 Email**: `admin@social-bot.local`
- **👤 User**: `Admin SocialBot`
- **🔒 Pass**: `SocialBot2026!`

### 2️⃣ Procedimiento de Importación
Una vez dentro del editor de n8n:
1. Haz clic en el botón **"+" (Create Workflow)**.
2. Abre el menú de opciones (**⋮**) → **"Import from file"**.
3. Localiza la matriz de flujos en:
   `c:\dev\social-bot-scheduler\n8n\workflows\`
4. Selecciona el archivo (ej: `case-01-python-to-php.json`) e impórtalo.

> [!TIP]
> n8n requiere importar los flujos **uno por uno** para garantizar que los Webhooks se registren correctamente en el motor de red.

---

## ✅ Activación de Casos

Para cada flujo importado, es mandatorio:
1. **Abrir el editor** del workflow.
2. Hacer clic en el **toggle "Active"** (esquina superior derecha).
3. Verificar que el indicador cambie a **verde 🟢**.

---

## 🛠️ Resolución de Conflictos

- **¿Webhooks inactivos?**: Asegúrate de que el flujo esté guardado y en estado "Active". Reinicia el contenedor si es necesario: `make restart n8n`.
- **¿Error 404/500 en el Bot?**: Espera 10 segundos tras la activación para que el sistema propague la ruta del Webhook.
- **¿Setup bloqueado?**: Puedes hacer clic en **"Skip"** durante el onboarding inicial para acceder directamente a la interfaz de desarrollo.

---

## 📁 Directorio de Recursos

- **📦 Workflows JSON**: `n8n/workflows/`
- **🧩 Scripts de Origen**: `cases/*/origin/`
- **🧪 Test de Integración**: `scripts/test_shared_scripts.sh`

---
*Manual de recuperación v4.0 — Social Bot Scheduler*
