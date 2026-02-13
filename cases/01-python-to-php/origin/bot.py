import sys
import os

# ==================================================================================================
# PUNTO DE ENTRADA DEL BOT (WRAPPER)
# ==================================================================================================
# Este script actúa como un "shim" o adaptador para ejecutar el paquete `social_bot` como un script.
#
# Contexto:
#   En estructuras de proyectos Python modernas, el código fuente suele estar dentro de un directorio `src`.
#   Para ejecutarlo sin instalar el paquete (modo desarrollo/scripting), necesitamos manipular el `PYTHONPATH`.

# Agregamos el directorio 'src' al path de búsqueda de módulos de Python.
# Esto permite importar `social_bot` aunque no esté instalado en el site-packages del entorno virtual.
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from social_bot.main import main

if __name__ == "__main__":
    # Inicia la ejecución principal delegando al módulo `social_bot.main`
    main()
