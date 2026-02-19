# 🎓 Manual Paso a Paso: Guía de Instalación y Ejecución

Este documento está diseñado para llevarte de **cero a operativo** en el universo de Social Bot Scheduler. No asume conocimientos previos.

---

## 🏗️ Fase 1: Lo que necesitas instalar (Prerrequisitos)

Antes de mover un dedo, asegúrate de tener estas tres herramientas en tu equipo. Son el martillo, el destornillador y la llave inglesa de este proyecto.

### 1. Sistema de Contenedores (Docker)
Docker permite crear "computadoras virtuales" (contenedores) para ejecutar tus servidores.
-   **Windows/Mac**: Descarga e instala [Docker Desktop](https://www.docker.com/products/docker-desktop/).
-   **Linux**: Sigue las guías oficiales para instalar Docker Engine y Docker Compose.
-   **Verificación**: Abre una terminal (CMD o PowerShell) y escribe `docker --version`. Debería salir algo como `Docker version 24.x.x`.

### 2. Lenguaje de Scripting (Python)
Usamos Python para nuestros asistentes automáticos.
-   **Descarga**: [Install Python 3.10+](https://www.python.org/downloads/).
-   **Importante**: Al instalar en Windows, marca la casilla **"Add Python to PATH"**.
-   **Verificación**: Escribe `python --version` en la terminal.

### 3. Editor de Código (Opcional pero recomendado)
-   **Visual Studio Code**: [Descargar aquí](https://code.visualstudio.com/).

---

## 🚀 Fase 2: Descargar y Preparar

1.  **Clonar el Proyecto**:
    Abre tu terminal donde quieras guardar el proyecto y ejecuta:
    ```bash
    git clone https://github.com/vladimiracunadev-create/social-bot-scheduler.git
    cd social-bot-scheduler
    ```

2.  **Ejecutar el Asistente de Configuración**:
    Hemos creado un script mágico que prepara todo por ti.
    ```bash
    python setup.py
    ```
    -   Verás un menú con las 8 opciones.
    -   Escribe `1` y presiona Enter para elegir el **Caso 01 (Python -> PHP)**.
    -   El script creará archivos ocultos (`.env`) y carpetas necesarias.

---

## ⚙️ Fase 3: Levantar la Infraestructura

Ahora vamos a encender los servidores. El asistente te dio un comando al final, pero aquí te lo explicamos.

En tu terminal (dentro de la carpeta del proyecto):
docker-compose up -d n8n dest-php
```
-   `up -d`: Significa "levántate en segundo plano" (detached).
-   `n8n`: Es el servicio "puente".
-   `dest-php`: Es el servidor destino.
-   **Nota**: Docker también descargará automáticamente el motor de base de datos necesario (ej: MySQL para el Caso 01).

**¿Cómo sé que funcionó?**
Ejecuta:
```bash
docker ps
```
Deberías ver una lista con `social-bot-n8n` y `social-bot-dest-php` en estado **Up**.

---

## 🧠 Fase 4: El Cerebro ya está listo (n8n - Automático)

A diferencia de antes, **ya no necesitas configurar n8n manualmente**. El sistema se auto-configura al arrancar:

-   ✅ Los 8 workflows se importan automáticamente
-   ✅ Se activan solos (webhooks listos para recibir)
-   ✅ Se crea un usuario admin automáticamente

**Solo verifica** que n8n arrancó bien:

1.  Abre tu navegador en: [http://localhost:5678](http://localhost:5678)
2.  Deberías ver la interfaz de n8n con los workflows ya importados.
3.  Si te pide login, usa: `admin@social-bot.local` / `SocialBot2026!`

> **Nota**: Si es la primera vez que arrancas n8n, espera unos 30 segundos para que termine la auto-configuración.

---

## 🎮 Fase 5: ¡A Jugar! (Ejecución)

Todo está listo. Es hora de enviar un mensaje.

1.  Vuelve a tu terminal.
2.  Entra a la carpeta del bot emisor:
    ```bash
    cd cases/01-python-to-php/origin
    ```
3.  Ejecuta el bot:
    ```bash
    # Si estás en Windows y setup.py creó el entorno virtual:
    ..\..\..\venv\Scripts\python bot.py
    
    # O si tienes Python global:
    python bot.py
    ```
    *Nota: Si te da error de librerías, ejecuta `pip install -r requirements.txt` primero.*

4.  Verás en la consola: `Payload sent to http://localhost:5678/...`

---

## ✅ Fase 6: Verificación Final

¿Llegó el mensaje?
Abre el destino en tu navegador: [http://localhost:8081](http://localhost:8081)

¡Deberías ver una tarjeta con el post que acabas de enviar! Has comunicado Python con PHP a través de Docker y n8n.

---

## 🛡️ Fase 7: ¿Qué pasa si algo falla? (Resiliencia)

Este sistema es "inteligente". Si intentas enviar el mismo mensaje dos veces, o si el servidor destino se cae, el sistema te protegerá:

1.  **Anti-Duplicados (Idempotencia)**: Si envías el mismo ID de post dos veces, el sistema dirá "OK" pero no lo procesará de nuevo.
2.  **Protección de Caídas (Circuit Breaker)**: Si el destino falla 5 veces seguidas, el sistema dejará de intentarlo por 5 minutos para "dejarlo descansar".
3.  **Buzón de Errores (DLQ)**: Si un mensaje falla definitivamente, se guarda en un log especial (`errors.log`) para que no se pierda.

Puedes probar esto apagando el contenedor destino (`docker stop social-bot-dest-php`) y viendo cómo n8n maneja el error.

> 💡 **¿Quieres profundizar?** Este sistema implementa **11 patrones arquitectónicos** (Microservices, Event-Driven, Circuit Breaker, IaC, y más). Consulta [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) para un catálogo completo con diagramas y explicaciones.

---

## 🗄️ Fase 8: Persistencia Real (Bases de Datos)
En esta v4.0, tus mensajes no solo se "muestran" en pantalla, sino que se guardan para siempre en una base de datos. Cada lenguaje usa una distinta:
- Si usas el **Caso 01**, revisa el motor **MySQL**.
- Si usas el **Caso 05**, tus posts viven en **MongoDB**.
- Si usas el **Caso 08**, se guardan en **SQL Server**.

Puedes ver el estado de estas bases de datos y los registros guardados directamente en el **Dashboard Maestro**: [http://localhost:8080](http://localhost:8080).

## 🔄 ¿Cómo pruebo otros casos?
Repite el proceso:
1.  Vuelve a la raíz: `cd ../../..`
2.  Corre `python setup.py` y elige otro número (ej. 7 para Ruby).
3.  Levanta el nuevo contenedor: `docker-compose up -d dest-ruby`. Docker levantará también la base de datos (Cassandra en este caso).
4.  Entra en la carpeta `origin` del nuevo caso y ejecuta el bot.
