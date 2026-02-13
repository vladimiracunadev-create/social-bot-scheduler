from social_bot.main import main

# ==================================================================================================
# PUNTO DE ENTRADA DEL BOT
# ==================================================================================================
# Script de ejecución directa.
# A diferencia del Caso 01, este script asume que el paquete `social_bot` ya es importable
# (probablemente instalado vía pip o poetry, o ejecutado con PYTHONPATH configurado).

if __name__ == "__main__":
    # Inicia la orquestación del bot
    main()
