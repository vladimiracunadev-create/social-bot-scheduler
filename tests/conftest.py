"""Configuración compartida de las pruebas del repositorio.

Inserta la raíz del repositorio en ``sys.path`` para que ``import analytics``
funcione igual se lance pytest desde la raíz o desde ``tests/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
