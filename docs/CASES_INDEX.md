# 📖 Índice de Casos Tecnológicos

Este repositorio ya no es una solución aislada, sino un catálogo de arquitecturas para la automatización de redes sociales. Elige el caso que mejor se adapte a tu infraestructura.

---

## 🏗️ Comparativa de Casos

| Característica | [Caso 01: Python-n8n-PHP](../cases/01-python-n8n-php/) | [Caso 02: Python-n8n-Go](../cases/02-python-n8n-go/) |
| :--- | :--- | :--- |
| **Pila Receptor** | PHP 8.2 (Apache) | Go 1.21 (Alpine) |
| **Rendimiento** | Estándar / Versátil | Alto / Ligero |
| **Uso Ideal** | Servidores Web hosting. | Microservicios / Cloud Native. |
| **Escalabilidad** | Media (PHP-FPM) | Muy Alta (Concurrencia nativa) |
| **Instalación** | Carga dinámica de archivos. | Ejecutable compilado (Docker). |

---

## 🔎 Detalle de Implementación

### Caso 01: El Clásico
Utiliza un script PHP sencillo para capturar los posts. Es ideal si ya tienes un servidor con Apache o Nginx y PHP. Es fácil de modificar "al vuelo" sin necesidad de recompilar nada.

### Caso 02: La Potencia
Utiliza un receptor escrito íntegramente en Go. Es extremadamente rápido y consume muy pocos recursos (RAM/CPU) en el contenedor Docker. Ideal si planeas procesar miles de posts por minuto.

---

## 🚦 ¿Cómo cambiar entre casos?
No necesitas borrar nada. El sistema está diseñado para alternar:
1. Ejecuta `python setup.py`.
2. Elige el número del caso.
3. El launcher actualizará tu `.env` y te dirá qué contenedores levantar.
