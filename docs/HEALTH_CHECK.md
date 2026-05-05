# 🏥 Diagnóstico del HUB (Comando Doctor)

La herramienta `hub.py` incluye un comando `doctor` diseñado para verificar la salud del sistema y asegurar que todos los componentes necesarios estén operativos.

## ¿Qué verifica el comando `doctor`?

El comando realiza las siguientes comprobaciones:

1.  **Docker**: Verifica si el motor de Docker está instalado y respondiendo.
2.  **Docker Compose**: Valida la presencia de la herramienta de orquestación.
3.  **Integridad de Manifiestos**: Confirma que el directorio `cases/` contiene archivos `app.manifest.yml` válidos para cada caso.
4.  **Log de Auditoría**: Comprueba el estado del archivo de auditoría `hub.audit.log`.

## 🎛️ Diagnóstico desde el Master Dashboard (v4.3.0)

Como complemento al `hub.py doctor`, el **Master Dashboard** (`http://localhost:8080`) realiza diagnóstico continuo:

- **Ping automático cada 20 s** al puerto del receptor de cada caso (`fetch` con `no-cors` y timeout 2.5 s).
- **Estado por tarjeta**: `READY` (verde) si el receptor responde, `OFFLINE` (rojo) si no.
- **Contadores en vivo** en la barra superior: `🟢 N/9 READY · 🔴 N/9 OFFLINE · 🚧 11 PLANNED`.
- **Última comprobación** con timestamp + botón **🔄 Re-comprobar** para forzar un ciclo.
- **Modal con comando** cuando un caso está OFFLINE: muestra `docker-compose --profile caseXX up -d` con botón copiar.
- **Toasts** notifican transiciones `ONLINE → OFFLINE` o viceversa entre comprobaciones.

> Esta funcionalidad es 100% client-side (no añade backend) — el navegador no ejecuta `docker`, solo te muestra el comando exacto que tú decides ejecutar.

## Cómo ejecutarlo

Desde la raíz del proyecto, ejecuta:

```bash
python hub.py doctor
```

## Registro de Auditoría (`hub.audit.log`)

Cada acción realizada a través del HUB (incluyendo diagnósticos, listados y ejecuciones de bots) se registra automáticamente en el archivo `hub.audit.log`.

**Campos del log:**
- `[TIMESTAMP]`: Fecha y hora de la acción.
- `USUARIO`: El usuario del sistema que ejecutó el comando.
- `CMD`: El comando específico ejecutado.
- `ESTADO`: Resultado de la operación (EXITO/FALLO).
- `DETALLES`: Información adicional o mensajes de error.

> [!TIP]
> Revisa este archivo periódicamente para auditar el uso del sistema y detectar posibles intentos de ejecución no autorizados.
