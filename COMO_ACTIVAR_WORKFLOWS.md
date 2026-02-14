# 🔧 Cómo Activar Workflows en n8n - Guía Visual

## Paso 1: Acceder a n8n

Abre tu navegador y ve a:
```
http://localhost:5678
```

## Paso 2: Completar Setup (Primera Vez)

Si es la primera vez que accedes, verás una pantalla de bienvenida.

**Completa el formulario:**
- **Email**: `admin@social-bot.local`
- **First Name**: `Admin`  
- **Last Name**: `SocialBot`
- **Password**: `SocialBot2026!`
- **Confirmar Password**: `SocialBot2026!`

Click en **"Next"** o **"Continue"**

## Paso 3: Importar el Primer Workflow

### 3.1 Click en "Add Workflow" o el botón "+"
Busca el botón que dice "+ Add workflow" o simplemente "+"

### 3.2 Importar desde archivo
1. Click en los **3 puntos** (⋮) o menú hamburguesa (☰) en la esquina superior derecha
2. Selecciona **"Import from file"** o **"Import workflow"**
3. Se abrirá un explorador de archivos

### 3.3 Seleccionar el archivo workflow
Navega a:
```
c:\dev\social-bot-scheduler\n8n\workflows\
```

Selecciona el primer archivo:
```
case-01-python-to-php.json
```

Click **"Abrir"** o **"Open"**

## Paso 4: ACTIVAR el Workflow ⭐ IMPORTANTE

Después de importar, verás el workflow en el editor.

### 4.1 Buscar el toggle "Active"
En la **esquina superior derecha**, verás un switch/toggle que dice **"Inactive"** o **"Active"**

### 4.2 Click en el toggle
- **ANTES**: ⚪ Inactive (gris)
- **DESPUÉS**: 🟢 Active (verde)

### 4.3 Guardar (opcional)
Si hay un botón "Save", haz click para confirmar.

## Paso 5: Repetir para los otros 7 workflows

Repite los pasos 3 y 4 para cada archivo:

✅ `case-01-python-to-php.json` → ACTIVAR  
⬜ `case-02-python-to-go.json` → ACTIVAR  
⬜ `case-03-go-to-node.json` → ACTIVAR  
⬜ `case-04-node-to-fastapi.json` → ACTIVAR  
⬜ `case-05-laravel-to-react.json` → ACTIVAR  
⬜ `case-06-go-to-symfony.json` → ACTIVAR  
⬜ `case-07-rust-to-ruby.json` → ACTIVAR  
⬜ `case-08-csharp-to-flask.json` → ACTIVAR  

## Paso 6: Verificar que Están Activos

### Opción A: Desde la lista de workflows
1. Click en **"Workflows"** en el menú lateral izquierdo
2. Verás una lista de todos los workflows
3. Los activos tienen un **punto verde** 🟢 o badge que dice "Active"

### Opción B: Desde cada workflow
Abre cada workflow y verifica que el toggle esté en verde.

## Paso 7: Probar el Sistema

Una vez que los 8 workflows estén activos (verde):

```powershell
# Abrir PowerShell y ejecutar:
cd c:\dev\social-bot-scheduler\cases\01-python-to-php\origin
python bot.py
```

**Resultado esperado:**
```
[INFO] Iniciando Social Bot Service...
[INFO] Procesando 1 posts...
[INFO] Payload enviado exitosamente
```

Luego verifica el dashboard PHP:
```
http://localhost:8081
```

Deberías ver el mensaje recibido.

---

## 🆘 Problemas Comunes

### "No encuentro el botón Import"
- Busca el menú **⋮** (3 puntos verticales)
- O el menú **☰** (hamburguesa)
- Está generalmente en la esquina superior derecha

### "El workflow se importó pero no veo el toggle Active"
- Después de importar, n8n te lleva al editor del workflow
- El toggle está **arriba a la derecha**, cerca del nombre del workflow
- Puede decir "Inactive" en gris o tener un icono de switch ⚪

### "El toggle está en gris y no puedo clickearlo"
- Asegúrate de haber guardado el workflow primero
- Click en "Save" si está disponible
- Luego intenta activar

### "Activé pero sigue sin funcionar"
- Espera 10-15 segundos después de activar
- Los webhooks tardan en registrarse
- Verifica los logs: `docker-compose logs n8n`

---

## ✅ Checklist Final

Antes de probar el bot, verifica:

- [ ] Los 8 workflows están importados
- [ ] Los 8 workflows tienen toggle verde (Active)
- [ ] N8n está corriendo (`docker-compose ps`)
- [ ] El servicio destino PHP está corriendo (puerto 8081)

**Listo para probar!** 🚀
