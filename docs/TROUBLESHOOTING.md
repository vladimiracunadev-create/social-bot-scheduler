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

---

## 🔗 Problemas de n8n y Flujos

### ❌ Síntoma: El bot dice "Payload sent" pero el Dashboard está vacío
**Verificaciones**:
1.  **¿Workflow Activo?**: Abre n8n y verifica que el switch "Active" esté en verde.
2.  **Webhooks**: n8n por defecto usa URLs dinámicas. Asegúrate de que el path en el nodo Webhook coincida con lo que espera el bot (ej: `social-bot-scheduler-php`).
3.  **Logs de n8n**: Mira la pestaña "Executions" en n8n para ver si hay errores en el nodo HTTP Request.
4.  **Guardrails - Idempotencia**: Si el payload ha sido enviado antes, n8n lo ignorará silenciosamente. Verifica si estás enviando el mismo contenido exacto en poco tiempo.
5.  **Guardrails - Circuit Breaker**: Si el proveedor (X, Facebook, etc.) está caído, el mensaje se moverá al **DLQ**. Revisa los logs de errores.

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

# Reconstruir todo
docker-compose up -d --build
```
