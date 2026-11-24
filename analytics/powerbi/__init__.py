"""Módulo de integración con Power BI.

Capa analítica de solo lectura sobre los casos del laboratorio. Nunca escribe
en la base de datos de un caso, nunca expone secretos y nunca altera el
comportamiento transaccional: cada adaptador emite únicamente consultas
``SELECT`` y cada columna exportada se valida contra una lista de denegación
antes de escribirse.

Punto de entrada: ``python -m analytics.powerbi.cli --help``.
"""

CONTRACT_VERSION = "1.0.0"

__all__ = ["CONTRACT_VERSION"]
