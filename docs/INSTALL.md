# 🚀 Guía de Instalación

Esta guía detalla los pasos para poner en marcha el **Social Bot Scheduler** en diferentes entornos.

## 1. Configuración de Variables de Entorno
Cualquiera sea el método de instalación, necesitas configurar el webhook:

1. Crea un archivo `.env` basado en `.env.example`.
2. Define `WEBHOOK_URL` con la dirección de tu webhook de n8n.

## 2. Instalación con Docker (Recomendado)
El uso de Docker garantiza que el bot funcione exactamente igual en cualquier máquina.

```bash
# Construir la imagen
make build

# Iniciar contenedor
make up

# Ver logs
make logs
```

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
