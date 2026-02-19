"""
==================================================================================================
PUNTO DE ENTRADA ARQUITECTÓNICO (Case 01: Python -> n8n -> PHP)
==================================================================================================
Este servicio actúa como el "Emisor Políglota" inicial del ecosistema.
Representa una aplicación moderna en Python que necesita delegar su salida a un
sistema legado en PHP a través de un bus de eventos (n8n).

Diseño:
- Separación de preocupaciones: main.py solo se encarga del Bootstrap.
- Inyección de dependencias implícita a través de BotService.
- Soporte para ejecución en contenedores Docker mediante manipulación de PYTHONPATH.
"""

from .service import BotService


def main():
    """
    Función principal de arranque.
    Inicializa el ciclo de vida del bot y delega la orquestación al BotService.
    """
    service = BotService()
    service.run()


if __name__ == "__main__":
    main()
