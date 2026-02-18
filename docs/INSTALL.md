# 🚀 Guía de Instalación

Esta guía detalla los pasos para poner en marcha el **Social Bot Scheduler** en diferentes entornos.

## 1. Configuración de Variables de Entorno
Cualquiera sea el método de instalación, necesitas configurar el webhook:

1. Crea un archivo `.env` basado en `.env.example`.
2. Define `WEBHOOK_URL` con la dirección de tu webhook de n8n.

## 2. Instalación con Docker (Recomendado)
El uso de Docker garantiza la portabilidad absoluta y la seguridad mediante el aislamiento. La imagen está configurada para correr como **usuario no-privilegiado**.

```bash
# Construir la imagen con hardening
docker build -t social-bot-scheduler .

# Iniciar contenedor (ejemplo con n8n)
docker-compose up -d n8n dest-php db-mysql
```

> **Ecosistema Multi-DB**: Al levantar un servicio de destino, asegúrate de levantar también su base de datos asociada (ej: `db-mysql`, `db-mongodb`, etc.) para habilitar la persistencia.

> [!IMPORTANT]
> Nuestra imagen Docker utiliza una estrategia de **Dual-Layer Patching**:
> 1. Aísla la aplicación en un entorno virtual (`venv`).
> 2. Parchea proactivamente las dependencias del sistema en la imagen base `slim-bookworm`.
> 3. Se ejecuta como usuario no-privilegiado `botuser`.

## 3. Despliegue en Kubernetes (K8s)
Si tienes un entorno de orquestación, puedes usar los manifiestos incluidos:

1. Configura el secreto con tu URL real:
   ```bash
   # Edita k8s/secret.example.yaml con tus datos y aplícalo
   kubectl apply -f k8s/secret.example.yaml
   ```
2. Despliega el resto de recursos:
   ```bash
   make deploy
   ```

## 4. Instalación Manual (Desarrollo)
Si prefieres ejecutarlo directamente en tu sistema:

```bash
# Crear entorno virtual (opcional)
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows

# Instalar dependencias
make install

# Ejecutar
python bot.py
```
