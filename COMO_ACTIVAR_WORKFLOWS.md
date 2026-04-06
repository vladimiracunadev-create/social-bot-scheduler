# 🔧 Activación de Workflows en n8n — Guía Maestro

Esta guía detalla el proceso de activación manual de los flujos de orquestación en el núcleo de **n8n**. Sigue estos pasos para poner en marcha la inteligencia del laboratorio.

---

## 🚦 Paso 1: Acceso al Orquestador

Abre tu navegador preferido y navega a la URL local del servicio:
```text
http://localhost:5678
```

---

## 👤 Paso 2: Configuración Inicial (First Run)

Si es la primera vez que inicias el contenedor, n8n solicitará la creación de una cuenta de administrador. Utiliza estas credenciales estándar para el laboratorio:

- **📧 Email**: `admin@social-bot.local`
- **👤 Nombre**: `Admin SocialBot`
- **🔒 Password**: `SocialBot2026!`

---

## 📥 Paso 3: Importación de la Matriz

Para cada uno de los **9 casos de integración**, debes realizar el siguiente proceso:

1.  **Añadir Flujo**: Haz clic en el botón **"+" (Add workflow)**.
2.  **Importar**: En el menú superior derecho (**⋮**), selecciona **"Import from file"**.
3.  **Localizar Archivos**: Navega a la ruta del proyecto:
    `c:\dev\social-bot-scheduler\n8n\workflows\`
4.  **Seleccionar**: Elige el archivo `.json` correspondiente al caso (ej: `case-01-python-to-php.json`).

---

## ⭐ Paso 4: ACTIVACIÓN CRÍTICA

> [!IMPORTANT]
> Un workflow importado **no está operativo** hasta que se activa manualmente.

### 4.1 Switch de Activación
Busca el conmutador en la **esquina superior derecha** del editor:
- **Estado Inactivo (Gris)**: ⚪ `Inactive`
- **Estado Activo (Verde)**: 🟢 `Active`

### 4.2 Guardar Cambios
Asegúrate de hacer clic en **"Save"** para persistir la activación en la base de datos interna de n8n.

---

## 📋 Lista de Verificación (Checklist)

Asegúrate de que los siguientes flujos tengan el **punto verde 🟢** en la lista de workflows:

- [ ] `case-01-python-to-php.json`
- [ ] `case-02-python-to-go.json`
- [ ] `case-03-go-to-node.json`
- [ ] `case-04-node-to-fastapi.json`
- [ ] `case-05-laravel-to-react.json`
- [ ] `case-06-go-to-symfony.json`
- [ ] `case-07-rust-to-ruby.json`
- [ ] `case-08-csharp-to-flask.json`
- [ ] `case-09-python-to-gateway.json`

---

## 🧪 Validación del Sistema

Una vez activados, puedes lanzar una prueba real desde la consola:

```powershell
# Ejecutar bot de prueba del Caso 01
make demo
```

**Resultado esperado:**
- `[INFO] Payload enviado exitosamente` en la consola.
- El post aparece en el dashboard: `http://localhost:8081`.

---

## 🆘 Resolución de Problemas (FAQ)

> [!TIP]
> **¿No ves el botón de importación?**
> Busca el icono de tres puntos verticales (**⋮**) o el menú hamburguesa (**☰**) en la barra superior.

- **El toggle no cambia a verde**: Verifica que no haya nodos con errores de configuración (indicados con un punto rojo).
- **Activado pero no recibe datos**: Espera 10 segundos para que el Webhook se registre en el motor de red de n8n.
- **Error 404**: Verifica que los contenedores receptores estén corriendo con `make doctor`.

---
*Manual de operaciones v4.0 — Social Bot Scheduler*
