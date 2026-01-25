# 🔧 Guía de Solución de Problemas (Troubleshooting)

Si algo no funciona como esperas, consulta esta guía antes de abrir un issue.

## 🔴 Problemas Comunes

### 1. El contenedor de n8n no inicia o se reinicia constantemente
**Causa**: Falta de permisos en la carpeta de datos o conflicto de puertos.
**Solución**:
- Asegúrate de que el puerto `5678` esté libre.
- Reinicia los volúmenes:
  ```bash
  docker-compose down -v
  docker-compose up -d n8n
  ```

### 2. "Connection Refused" en el Dashboard (localhost:808X)
**Causa**: El contenedor destino no se ha levantado correctamente.
**Solución**:
- Verifica los logs:
  ```bash
  docker-compose logs dest-php  # o el servicio que estés usando
  ```
- Si usas C# (Caso 08) o Rust (Caso 07), asegúrate de haber reconstruido la imagen si cambiaste código:
  ```bash
  docker-compose build dest-flask
  docker-compose up -d dest-flask
  ```

### 3. El Emisor (Rust/Go/Python) da error de conexión al enviar
**Causa**: El webhook de n8n no está escuchando o la URL en `.env` es incorrecta.
**Solución**:
- Verifica que n8n esté activo en `http://localhost:5678`.
- Revisa el archivo `.env` en la carpeta `origin` de tu caso. Debe apuntar a `http://localhost:5678/webhook/...`.

### 4. Error al ejecutar `make` en Windows
**Causa**: Make no está instalado o no está en el PATH.
**Solución**:
- Instala Make via Chocolatey: `choco install make`.
- O usa los comandos de `docker-compose` directamente (mira el `Makefile` para ver qué hacen).

## 🧪 Cómo verificar el estado del sistema
Ejecuta este comando para ver todos los servicios activos:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```
Deberías ver `social-bot-n8n` y tu contenedor destino (ej. `social-bot-dest-ruby`) en estado "Up".
