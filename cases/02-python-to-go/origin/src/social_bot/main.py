"""
==================================================================================================
BOOTSTRAP DE ALTA PERFORMANCE (Case 02: Python -> Go -> MariaDB)
==================================================================================================
A diferencia del Caso 01, este flujo está diseñado pensando en la escalabilidad vertical.
Go, como receptor, es capaz de procesar magnitudes de datos muy superiores, lo que convierte 
a este bot en un cliente ligero de un sistema de alto tráfico.
"""

from .service import BotService


def main():
    """
    Función de arranque.
    Inicializa el servicio y delega el control al orquestador de Python.
    """
    service = BotService()
    service.run()


if __name__ == "__main__":
    main()
