# 🔧 Guía de Solución de Problemas (Troubleshooting)

Si encuentras dificultades al orquestar los contenedores o ejecutar los bots políglotas, consulta esta guía técnica. Hemos consolidado las soluciones a los problemas más recurrentes detectados en el laboratorio.

---

## 🏗️ Docker e Infraestructura

### ❌ Error: `npm error code EJSONPARSE` (Caso 03)
**Síntoma**: El contenedor `dest-node` falla con un error de "Unexpected token" al parsear el `package.json`.
- **Causa**: Codificación de archivo incorrecta (UTF-16 en lugar de UTF-8).
- **Solución**: Asegúrate de que `package.json` esté en **UTF-8 (sin BOM)**. Usa el comando:
  ```bash
  docker-compose build --no-cache dest-node
  ```

### ❌ Error: `extconf failed` (Caso 07)
**Síntoma**: Fallo al instalar gemas nativas en el contenedor Ruby.
- **Causa**: La imagen `ruby:alpine` requiere herramientas de compilación adicionales.
- **Solución**: Verifica que el Dockerfile incluya `apk add --no-cache build-base`.

### ❌ Error: `403 Forbidden` en Sinatra
**Síntoma**: n8n recibe un error 403 al intentar conectar con el receptor Ruby.
- **Causa**: Protección de `HostAuthorization` de Rack activa por defecto.
- **Solución**: Desactiva la protección en `app.rb` para el entorno de simulación local.

---

## 🌉 n8n y Flujos de Orquestación

### ❌ Síntoma: Los flujos no aparecen importados
- **Solución**: Fuerza la re-importación manual:
  ```bash
  make reset-n8n
  # O vía comando directo:
  docker-compose restart n8n
  ```

### ❌ Síntoma: Fallo en el Webhook (404)
- **Verificación**: Asegúrate de que el workflow esté marcado como **Active 🟢** en la esquina superior derecha del editor de n8n.
- **Latencia**: Tras activar un flujo, espera **10-15 segundos** antes de disparar el bot de origen.

---

## 🛡️ Seguridad y Secretos (Trivy Aware)

### ❌ Error: Fallo en el Pipeline de CI/CD (Trivy)
**Síntoma**: El escaneo de seguridad falla o indica que la acción no puede resolverse.
- **Causa**: Uso de versiones comprometidas de `trivy-action`.
- **Solución**: Hemos migrado todos los flujos a la versión **`v0.35.0`**. No utilices etiquetas mutables como `@latest` en entornos críticos.

### ❌ Error: `edge-proxy` no arranca
- **Causa**: `EDGE_BASIC_AUTH_HASH` ausente o inválido.
- **Solución**: Genera un hash bcrypt válido:
  ```bash
  docker run --rm caddy:2.10.2-alpine caddy hash-password --plaintext 'TuPassword'
  ```

---

## 📊 Observabilidad y Métricas

### ❌ Síntoma: Grafana muestra "Database is locked"
- **Causa**: Conflicto de bloqueo de SQLite en volúmenes Docker (común en Windows).
- **Solución**: Reinicia el stack completo:
  ```bash
  make down && make up
  ```

---

## 🐍 Python y Style Guide (Black)

### ❌ Síntoma: `black --check .` falla en el CI
**Causa**: Black es extremadamente estricto con el espaciado y la concatenación de strings largas.
- **Diagnóstico**:
  ```bash
  black --diff --check <archivo_erroneo>
  ```
- **Acción**: Aplica el diff exacto sugerido por la herramienta. El estándar de Black es la "fuente de verdad" estética del proyecto.

---

## ⚡ Comandos de Rescate (Full Reset)

Si el entorno se encuentra en un estado inconsistente, ejecuta una purga total:
```bash
# Detener servicios y borrar volúmenes (limpia n8n y DBs)
docker-compose down -v

# Purga profunda de recursos huérfanos
docker system prune -a --volumes

# Reconstrucción total
make up
```

---
*Manual de resolución de incidentes v4.0 — Social Bot Scheduler*
