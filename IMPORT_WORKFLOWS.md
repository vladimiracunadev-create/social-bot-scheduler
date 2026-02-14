# Guía de Importación Manual de Workflows en n8n

## Situación

N8n está corriendo pero los workflows no se importaron automáticamente debido a cambios en la API de n8n v2.7.5.

## Solución: Importar Manualmente (2 minutos)

### Paso 1: Acceder a n8n

1. Abre tu navegador
2. Ve a: `http://localhost:5678`

### Paso 2: Completar Setup Inicial

Si ves una pantalla de bienvenida/setup:

- **Email**: `admin@social-bot.local`
- **First Name**: `Admin`
- **Last Name**: `SocialBot`
- **Password**: `SocialBot2026!`

Click en "Get Started" o "Continue"

### Paso 3: Importar los 8 Workflows

Una vez dentro de n8n:

1. **Click en el botón "+" o "Create Workflow"**
2. **Click en "..."** (menú) → **"Import from file"**
3. **Navega a la carpeta:**
   ```
   c:\dev\social-bot-scheduler\n8n\workflows\
   ```
4. **Selecciona TODOS los archivos** (Ctrl+A):
   - case-01-python-to-php.json
   - case-02-python-to-go.json
   - case-03-go-to-node.json
   - case-04-node-to-fastapi.json
   - case-05-laravel-to-react.json
   - case-06-go-to-symfony.json
   - case-07-rust-to-ruby.json
   - case-08-csharp-to-flask.json

5. **Importar uno por uno** (n8n no soporta importación múltiple)

### Paso 4: Activar los Workflows

Para cada workflow importado:

1. Abre el workflow
2. Click en el **toggle "Active"** (arriba derecha)
3. Verifica que cambie a verde/activado
4. Guarda si es necesario

### Paso 5: Verificar que Funcionan

Una vez que los 8 workflows estén activos:

```bash
# Probar el Caso 01
cd cases/01-python-to-php/origin
python bot.py
```

**Resultado esperado:**
```
[INFO] Iniciando Social Bot Service...
[INFO] Procesando 1 posts...
[INFO] Payload enviado exitosamente
```

Luego verifica el dashboard:
```
http://localhost:8081
```

Deberías ver el post recibido.

## Troubleshooting

### Si n8n pide "Skip" en el setup
- Click en "Skip" y accederás directo a la interfaz
- Luego ve a Settings → Users para crear un usuario si es necesario

### Si los webhooks no se activan
- Asegúrate que el workflow esté marcado como "Active"
- Verifica que el puerto 5678 esté accesible
- Reinicia n8n: `docker-compose restart n8n`

### Si el bot da error 404/500
- Verifica que los workflows están activos (verde)
- Espera 10-15 segundos después de activar (webhooks se registran)
- Verifica el path del webhook en el workflow coincide con el bot

## Archivos de Referencia

- **Workflows**: `c:\dev\social-bot-scheduler\n8n\workflows\`
- **Generador**: `c:\dev\social-bot-scheduler\generate_workflows.py`
- **Bot de prueba**: `c:\dev\social-bot-scheduler\cases\01-python-to-php\origin\bot.py`

---

**Tiempo estimado**: 2-3 minutos para importar los 8 workflows manualmente.
