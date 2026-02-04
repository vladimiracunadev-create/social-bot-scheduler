# 🏥 HUB Health Check (Doctor Command)

La herramienta `hub.py` incluye ahora un comando `doctor` diseñado para verificar la salud del sistema y asegurar que todos los componentes necesarios estén operativos.

## ¿Qué verifica el comando `doctor`?

El comando realiza las siguientes comprobaciones:

1.  **Docker**: Verifica si el motor de Docker está instalado y respondiendo.
2.  **Docker Compose**: Valida la presencia de la herramienta de orquestación.
3.  **Integridad de Casos**: Confirma que el directorio `cases/` existe y contiene casos válidos.
4.  **Audit Log**: Comprueba el estado del archivo de auditoría `hub.audit.log`.

## Cómo ejecutarlo

Desde la raíz del proyecto, ejecuta:

```bash
python hub.py doctor
```

## Registro de Auditoría (`hub.audit.log`)

Cada acción realizada a través del HUB (incluyendo diagnósticos, listados y ejecuciones de bots) se registra automáticamente en el archivo `hub.audit.log`.

**Campos del log:**
- `[TIMESTAMP]`: Fecha y hora de la acción.
- `USER`: El usuario del sistema que ejecutó el comando.
- `CMD`: El comando específico ejecutado.
- `STATUS`: Resultado de la operación (SUCCESS/FAILED).
- `DETAILS`: Información adicional o mensajes de error.

> [!TIP]
> Revisa este archivo periódicamente para auditar el uso del sistema y detectar posibles intentos de ejecución no autorizados.
