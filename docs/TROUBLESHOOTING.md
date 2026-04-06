# 🔧 Guía de Solución de Problemas (Troubleshooting)

Si encuentras problemas al levantar los contenedores o ejecutar los bots, consulta esta guía revisada. Hemos incluido los problemas detectados durante las pruebas de integración reales.

---

## 🏗️ Problemas de Docker y Construcción

### ❌ Error: `npm error code EJSONPARSE` (Caso 03: Node.js)
**Síntoma**: Al hacer `docker-compose up --build`, el contenedor `dest-node` falla con un error de "Unexpected token" al parsear `package.json`.
**Causa**: El archivo `package.json` fue guardado con codificación UTF-16 (Unicode) en lugar de UTF-8, lo que rompe el motor de Node.js.
**Solución**:
1.  Asegúrate de que `package.json` esté en formato UTF-8 (sin BOM).
2.  Puedes usar el script `fix_json.py` incluido en la raíz si el error persiste.
3.  Borra el caché de docker y reconstruye:
    ```bash
    docker-compose build --no-cache dest-node
    ```

### ❌ Error: `extconf failed, exit code 1` (Caso 07: Ruby/Sinatra)
**Síntoma**: Fallo al instalar gemas como `puma` o `nio4r` dentro del contenedor Ruby.
**Causa**: La imagen base `ruby:alpine` es muy ligera y no incluye las herramientas de compilación (`make`, `gcc`) necesarias para algunas gemas.
**Solución**:
- Hemos actualizado el `Dockerfile` de `cases/07-rust-to-ruby/dest/` para incluir:
  ```dockerfile
  RUN apk add --no-cache build-base
  ```
- Si creas un nuevo caso basado en Ruby, recuerda incluir siempre `build-base`.

### ❌ Error: `403 Forbidden` (Caso 07: Ruby/Sinatra)
**Síntoma**: n8n falla con "Error in workflow" al intentar enviar datos al contenedor Ruby. Los logs de `social-bot-dest-ruby` muestran `attack prevented by Rack::Protection::HostAuthorization`.
**Causa**: Sinatra (Rack) bloquea peticiones cuyo encabezado `Host` no coincide con los permitidos (n8n usa el nombre de red interno).
**Solución**:
- Desactiva el HostAuthorization en `app.rb` para el entorno de simulación:
  ```ruby
  set :protection, :except => [:host_authorization, :json_csrf]
  set :host_authorization, { permitted_hosts: [] }
  ```
- Recuerda reconstruir la imagen: `docker-compose build dest-ruby`.

---

## 📈 Problemas de Observabilidad (v3.0)

### ❌ Error: Prometheus muestra n8n como `DOWN` o 404
**Síntoma**: En `http://localhost:9090` -> Status -> Targets, el job de n8n sale en rojo o con error 404.
**Causa**: La variable de entorno en `docker-compose.yml` está ausente o es incorrecta (ej: `N8N_METRICS` vs `N8N_METRICS_ENABLED`).
**Solución**:
- Verifica que `N8N_METRICS=true` esté en el servicio `n8n`.
- Reinicia el contenedor: `docker-compose up -d n8n`.

### ❌ Error: Grafana dice `Database is locked`
**Síntoma**: Errores en los logs de `social-bot-grafana`.
**Causa**: Problema común en Windows/Docker Desktop con el bloqueo de archivos SQLite en volúmenes montados.
**Solución**: Reinicia el stack completo: `docker-compose down && docker-compose up -d`.

---

## 🔗 Problemas de n8n y Flujos

### ❌ Síntoma: n8n arranca pero los workflows no se importaron

**Causa**: El script de auto-setup (`n8n_auto_setup.sh`) puede fallar si n8n tarda más de lo esperado en arrancar.
**Solución**:
1.  Fuerza la re-importación:
    ```bash
    make reset-n8n
    ```
2.  O manualmente:
    ```bash
    docker-compose exec n8n rm -f /home/node/.n8n/.workflows_imported
    docker-compose restart n8n
    ```
3.  Espera ~30 segundos y verifica en [http://localhost:5678](http://localhost:5678).

### ❌ Síntoma: n8n pide crear cuenta de owner

**Causa**: El auto-setup no pudo crear la cuenta en el primer arranque.
**Solución**:
-   Usa las credenciales declaradas en `N8N_OWNER_EMAIL` y `N8N_OWNER_PASSWORD` de tu `.env`.
-   Si no funcionan, crea una cuenta manualmente — los workflows ya estarán importados.
-   Si estás usando el perfil `edge`, verifica también `N8N_HOST`, `N8N_PORT`, `N8N_PROTOCOL`, `N8N_PROXY_HOPS`, `N8N_WEBHOOK_URL` y `N8N_EDITOR_BASE_URL`.

### ❌ Síntoma: El bot dice "Payload sent" pero el Dashboard está vacío

**Verificaciones**:
1.  **¿Workflow Activo?**: Abre n8n y verifica que el switch "Active" esté en verde.
2.  **Webhooks**: n8n por defecto usa URLs dinámicas. Asegúrate de que el path en el nodo Webhook coincida con lo que espera el bot (ej: `social-bot-scheduler-php`).
3.  **Logs de n8n**: Mira la pestaña "Executions" en n8n para ver si hay errores en el nodo HTTP Request.
4.  **Guardrails - Idempotencia**: Si el payload ha sido enviado antes, n8n lo ignorará silenciosamente. Verifica si estás enviando el mismo contenido exacto en poco tiempo.
5.  **Guardrails - Circuit Breaker**: Si el proveedor (X, Facebook, etc.) está caído, el mensaje se moverá al **DLQ**. Revisa los logs de errores.

### ❌ Síntoma: `edge-proxy` falla al arrancar

**Causa**: `EDGE_BASIC_AUTH_HASH` no está definido o no es un hash bcrypt válido.
**Solución**:
1.  Genera un hash:
    ```bash
    docker run --rm caddy:2.10.2-alpine caddy hash-password --plaintext 'TuPasswordFuerte'
    ```
2.  Copia el resultado en `EDGE_BASIC_AUTH_HASH`.
3.  Reinicia el perfil:
    ```bash
    make up-edge
    ```

---

## 🐍 Problemas de Python y Virtualenvs

### ❌ Error: `ModuleNotFoundError` al ejecutar `bot.py`
**Causa**: Estás ejecutando el bot con el Python global en lugar del entorno virtual configurado por `setup.py`.
**Solución**:
- Activa siempre el entorno virtual antes de correr el bot:
  - **Windows**: `..\..\..\venv\Scripts\activate`
  - **Linux/Mac**: `source ../../../venv/bin/activate`
- O usa la ruta directa: `..\..\..\venv\Scripts\python bot.py`.

---

## ⚡ Comandos de Rescate
Si todo falla, limpia el entorno y empieza de cero:
```bash
# Detener todo y borrar volúmenes (borra datos de n8n)
docker-compose down -v

# Borrar imágenes antiguas que puedan estar corruptas
docker system prune -a --volumes

# Reconstruir todo (n8n se auto-configura de nuevo)
docker-compose up -d --build
```

> **Tip**: Despu?s de `docker-compose down -v`, n8n re-importar? los 9 workflows autom?ticamente al arrancar.

## Black y Formato

### Error recurrente: `black --check .` falla aunque el archivo "se vea bien"
**Sintoma**: CI muestra mensajes como `would reformat cases/.../api.py` o `would reformat cases/.../use_cases.py`, pero a simple vista el archivo parece ya formateado.

**Causa**: Black aplica reglas sintacticas muy especificas sobre:
- concatenacion implicita de strings
- comprensiones o llamadas largas que Black decide colapsar en una sola linea
- bloques multilinea con parentesis donde Black prefiere una forma distinta
- lineas SQL, HTML o CSS embebidas que visualmente parecen correctas, pero no coinciden con el formato exacto de Black

**Diagnostico recomendado**:
```bash
black --diff --check <archivo>
```

Ejemplo real para este repo:
```bash
black --diff --check cases/09-python-to-gateway/dest/app/api.py cases/09-python-to-gateway/dest/app/infrastructure.py cases/09-python-to-gateway/dest/app/use_cases.py
```

**Por que usar `--diff --check` y no solo `--check`**:
- `--check` solo dice que reformataria el archivo
- `--diff --check` muestra exactamente el parche que Black espera
- eso evita adivinar cambios y reduce commits repetidos por formato

**Flujo recomendado antes de subir cambios**:
1. Ejecuta `black --check .`
2. Si falla, ejecuta `black --diff --check <archivo>` sobre los archivos reportados
3. Aplica exactamente ese diff
4. Repite hasta que Black no reporte mas diferencias
5. Recien despues haz commit y push

**Leccion aprendida**:
- En este repositorio ya ocurrio con el Caso 09 y puede repetirse en casos con FastAPI, SQL embebido, dashboards HTML inline o strings largas.
- Cuando haya duda, el output de Black es la fuente de verdad.
