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
```bash
docker-compose up -d n8n dest-php
```
-   `up -d`: Significa "levántate en segundo plano" (detached).
-   `n8n`: Es el servicio "puente".
-   `dest-php`: Es el servidor destino donde veremos los resultados.

**¿Cómo sé que funcionó?**
Ejecuta:
```bash
docker ps
```
Deberías ver una lista con `social-bot-n8n` y `social-bot-dest-php` en estado **Up**.

---

## 🧠 Fase 4: Conectar el Cerebro (n8n)

Esta es la única parte manual. n8n necesita saber qué hacer con los mensajes.

1.  Abre tu navegador en: [http://localhost:5678](http://localhost:5678)
2.  Configura tu cuenta de admin (solo te lo pide la primera vez).
3.  Busca el botón **Menu** > **Workflows** > **Import from File**.
4.  Navega a la carpeta de tu caso:
    `social-bot-scheduler\cases\01-python-to-php\n8n\workflow.json`
    (Selecciona ese archivo json).
5.  **CRUCIAL**: Una vez importado, verás un botón **Inactive** (rojo) arriba a la derecha. **Cámbialo a Active (verde)**.

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

## 🔄 ¿Cómo pruebo otros casos?

Repite el proceso:
1.  Vuelve a la raíz: `cd ../../..`
2.  Corre `python setup.py` y elige otro número (ej. 7 para Ruby).
3.  Levanta el nuevo contenedor: `docker-compose up -d dest-ruby`.
4.  Importa el nuevo workflow en n8n y actívalo.
5.  Corre el nuevo bot desde su carpeta `origin`.
