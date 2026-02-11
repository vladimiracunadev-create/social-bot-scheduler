# ⚖️ Cumplimiento y Ética

> **AVISO IMPORTANTE**: Este proyecto es un **laboratorio educativo de ingeniería de software**. No está diseñado ni destinado para la automatización masiva no solicitada (spam), eludir controles de seguridad o violar los Términos de Servicio (ToS) de ninguna plataforma.

---

## 1. Propósito Educativo
El objetivo de **Social Bot Scheduler** es demostrar patrones de arquitectura distribuidos, interoperabilidad entre lenguajes y prácticas de DevOps (CI/CD, Seguridad, Observabilidad).

## 2. Política de Uso Responsable
Cualquier despliegue o uso de este software debe adherirse a los siguientes principios:

- **APIs Oficiales**: Utilizar únicamente métodos de acceso públicos y documentados por las plataformas de destino.
- **Respeto a Límites (Rate Limiting)**: El sistema implementa "retrasos" y "circuit breakers" para evitar saturación, pero es responsabilidad del operador configurar estos límites según las reglas de cada plataforma.
- **Identidad**: Los bots deben ser claramente identificables y no suplantar identidad humana.
- **Consentimiento**: No interactuar con usuarios que no hayan dado su consentimiento explícito o implícito según el contexto.

## 3. Descargo de Responsabilidad (Disclaimer)
El autor y los contribuyentes de este repositorio **no se hacen responsables** del mal uso de este código. El usuario asume toda la responsabilidad por el cumplimiento de las leyes locales y los Términos de Servicio de terceros.

## 4. Diseño "Good Citizen"
Este software incluye mecanismos de seguridad por diseño para comportamiento ético:
- **Idempotencia**: Evita el envío accidental de mensajes duplicados.
- **Dead Letter Queue (DLQ)**: Detiene los reintentos infinitos ante errores.
- **Logs de Auditoría**: Registra todas las operaciones para trazabilidad.

---
*Ingeniería con Ética.*
