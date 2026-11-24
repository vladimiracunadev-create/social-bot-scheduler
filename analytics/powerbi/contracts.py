"""Contratos de datos de la capa Power BI.

Un contrato es el acuerdo entre la base de datos de un caso y el modelo de
Power BI: un nombre de dataset estable, un orden fijo de columnas, un tipo
declarado por columna y el grano de una fila. Los adaptadores pueden cambiar
cómo alcanzan el motor; el contrato es a lo que se ata el ``.pbix``.

Aquí viven dos familias:

* **datasets crudos** (``case09_*``, ``case13_*``, ``case16_*``) — una
  proyección fiel y redactada de una tabla de un caso, usada para el detalle
  (drill-through); y
* **datasets conformados** (``dim_case``, ``dim_channel``, ``dim_date``,
  ``fact_events``) — el esquema en estrella contra el que se escriben las
  medidas, construido por :mod:`analytics.powerbi.normalize` a partir de los
  datasets crudos.

Los nombres de dataset y de columna se mantienen en inglés a propósito: son el
contrato que consume el ``.pbix`` y coinciden con las columnas reales de cada
motor. Traducirlos rompería tanto los informes como las medidas DAX.
"""

from __future__ import annotations

from dataclasses import dataclass

from analytics.powerbi.redaction import assert_contract_is_safe

# Correspondencia entre el tipo del contrato y el tipo de datos de Power BI /
# Power Query que debe ver el usuario en el modelo. Queda documentado para poder
# reconstruir el .pbix a mano.
POWER_BI_TYPES: dict[str, str] = {
    "text": "Text",
    "integer": "Whole Number",
    "decimal": "Decimal Number",
    "timestamp": "Date/Time",
    "date": "Date",
    "boolean": "True/False",
}


@dataclass(frozen=True)
class Column:
    """Una columna de un contrato de dataset."""

    name: str
    dtype: str
    description: str

    def __post_init__(self) -> None:
        if self.dtype not in POWER_BI_TYPES:
            raise ValueError(f"tipo de contrato desconocido: {self.dtype!r}")

    @property
    def power_bi_type(self) -> str:
        return POWER_BI_TYPES[self.dtype]


@dataclass(frozen=True)
class DatasetContract:
    """Un dataset con nombre, tipado y ordenado, exportado para Power BI."""

    name: str
    case_id: str
    engine: str
    grain: str
    description: str
    columns: tuple[Column, ...]

    def __post_init__(self) -> None:
        assert_contract_is_safe(self.name, self.column_names)
        if len(set(self.column_names)) != len(self.columns):
            raise ValueError(f"el dataset {self.name!r} declara columnas duplicadas")

    @property
    def column_names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.columns)

    @property
    def filename(self) -> str:
        return f"{self.name}.csv"

    def column(self, name: str) -> Column:
        for column in self.columns:
            if column.name == name:
                return column
        raise KeyError(name)


# ---------------------------------------------------------------------------
# Caso 09 — gateway FastAPI sobre DuckDB embebida
# ---------------------------------------------------------------------------
# api_key_prefix y api_key_hash existen en la tabla de origen y están ausentes
# aquí a propósito: redaction.assert_contract_is_safe rechazaría el contrato si
# alguien las volviera a añadir.

CASE09_REQUESTS = DatasetContract(
    name="case09_requests",
    case_id="09",
    engine="duckdb",
    grain="una petición de integración aceptada por el gateway",
    description="Peticiones recibidas en /webhook, con su estado final.",
    columns=(
        Column(
            "request_id", "text", "Identificador de la petición emitido por el bot."
        ),
        Column("channel", "text", "Canal lógico declarado por quien llama."),
        Column("action", "text", "Acción solicitada al gateway."),
        Column("owner", "text", "Propietario de GitHub al que apunta la petición."),
        Column("request_limit", "integer", "Límite de resultados solicitado."),
        Column("status", "text", "ACCEPTED, SUCCEEDED o FAILED."),
        Column("created_at", "timestamp", "Momento en que el gateway la almacenó."),
    ),
)

CASE09_PROVIDER_CALLS = DatasetContract(
    name="case09_provider_calls",
    case_id="09",
    engine="duckdb",
    grain="una llamada saliente a un proveedor externo",
    description="Llamadas al proveedor hechas al servir una petición, con latencia.",
    columns=(
        Column("call_id", "text", "Identificador de la llamada al proveedor."),
        Column("request_id", "text", "Petición que originó la llamada."),
        Column("provider", "text", "Nombre del proveedor externo."),
        Column("mode", "text", "Modo de proveedor usado (public o real)."),
        Column("endpoint", "text", "Endpoint invocado en el proveedor."),
        Column("http_status", "integer", "Código HTTP devuelto por el proveedor."),
        Column("latency_ms", "integer", "Latencia de ida y vuelta en milisegundos."),
        Column(
            "error_code", "text", "Código de error normalizado, vacío si hubo éxito."
        ),
        Column("error_message", "text", "Mensaje de error del proveedor, truncado."),
        Column("created_at", "timestamp", "Momento en que se registró la llamada."),
    ),
)

CASE09_REPO_SNAPSHOTS = DatasetContract(
    name="case09_repo_snapshots",
    case_id="09",
    engine="duckdb",
    grain="un repositorio observado en una petición",
    description="Repositorios devueltos por el proveedor para una petición.",
    columns=(
        Column("request_id", "text", "Petición a la que pertenece la observación."),
        Column("repo", "text", "Nombre completo del repositorio."),
        Column("stars", "integer", "Estrellas reportadas en el momento de observar."),
        Column("language", "text", "Lenguaje principal reportado."),
        Column("url", "text", "URL pública del repositorio."),
    ),
)

# ---------------------------------------------------------------------------
# Caso 13 — consumidor Go que proyecta eventos de Kafka en ClickHouse
# ---------------------------------------------------------------------------

CASE13_POSTS = DatasetContract(
    name="case13_posts",
    case_id="13",
    engine="clickhouse",
    grain="un post proyectado en el almacén columnar",
    description="Posts consumidos de Kafka y proyectados en ClickHouse.",
    columns=(
        Column("id", "text", "Identificador del post (clave del ReplacingMergeTree)."),
        Column("channel", "text", "Canal en el que se publicó el post."),
        Column("text", "text", "Cuerpo del post, truncado para analítica."),
        Column("created_at", "timestamp", "Momento de la proyección en ClickHouse."),
    ),
)

# ---------------------------------------------------------------------------
# Caso 16 — Hasura sobre una hypertable de TimescaleDB
# ---------------------------------------------------------------------------

CASE16_POSTS = DatasetContract(
    name="case16_posts",
    case_id="16",
    engine="timescaledb",
    grain="un post persistido en la hypertable",
    description="Posts escritos a través de Hasura en la hypertable social_posts.",
    columns=(
        Column("id", "text", "Identificador del post."),
        Column("channel", "text", "Canal en el que se publicó el post."),
        Column("text", "text", "Cuerpo del post, truncado para analítica."),
        Column("scheduled_at", "timestamp", "Publicación programada, si la hubo."),
        Column("created_at", "timestamp", "Marca de particionado de la hypertable."),
    ),
)

# ---------------------------------------------------------------------------
# Esquema en estrella conformado
# ---------------------------------------------------------------------------

DIM_CASE = DatasetContract(
    name="dim_case",
    case_id="*",
    engine="static",
    grain="un caso del laboratorio expuesto a Power BI",
    description="Dimensión de casos: stacks y motor analítico de cada uno.",
    columns=(
        Column("case_id", "text", "Número de caso a dos dígitos."),
        Column("case_name", "text", "Nombre de la carpeta del caso."),
        Column("origin_stack", "text", "Tecnología del bot emisor."),
        Column("dest_stack", "text", "Tecnología del servicio receptor."),
        Column("engine", "text", "Motor analítico del que se leyeron los datos."),
    ),
)

DIM_CHANNEL = DatasetContract(
    name="dim_channel",
    case_id="*",
    engine="derived",
    grain="un canal distinto observado en los casos",
    description="Dimensión de canales derivada de los hechos exportados.",
    columns=(
        Column("channel", "text", "Valor del canal tal como lo guarda el caso."),
        Column("channel_label", "text", "Etiqueta de presentación para informes."),
    ),
)

DIM_DATE = DatasetContract(
    name="dim_date",
    case_id="*",
    engine="derived",
    grain="un día del calendario cubierto por los hechos",
    description="Dimensión de fechas que cubre el rango exportado, sin huecos.",
    columns=(
        Column("date_key", "date", "Día del calendario (aaaa-mm-dd)."),
        Column("year", "integer", "Año del calendario."),
        Column("month", "integer", "Número de mes."),
        Column("day", "integer", "Día del mes."),
        Column("iso_week", "integer", "Número de semana ISO."),
        Column("weekday", "integer", "Día de la semana ISO, 1 = lunes."),
    ),
)

FACT_EVENTS = DatasetContract(
    name="fact_events",
    case_id="*",
    engine="derived",
    grain="un evento observable de un caso",
    description="Tabla de hechos conformada que une los eventos de cada caso.",
    columns=(
        Column("event_id", "text", "Identificador estable del evento."),
        Column("case_id", "text", "Caso al que pertenece el evento (a dim_case)."),
        Column("event_type", "text", "integration_request, provider_call o post."),
        Column("channel", "text", "Canal del evento (a dim_channel)."),
        Column("status", "text", "SUCCEEDED, FAILED o ACCEPTED."),
        Column("subject", "text", "Entidad sobre la que trata el evento."),
        Column(
            "occurred_at", "timestamp", "Marca temporal del evento, tal como se guardó."
        ),
        Column("date_key", "date", "Día del evento (a dim_date)."),
        Column("latency_ms", "integer", "Latencia, cuando el evento mide alguna."),
        Column("http_status", "integer", "Código HTTP, cuando el evento tiene uno."),
    ),
)

# Datasets crudos agrupados por caso, en orden de exportación.
RAW_DATASETS: dict[str, tuple[DatasetContract, ...]] = {
    "09": (CASE09_REQUESTS, CASE09_PROVIDER_CALLS, CASE09_REPO_SNAPSHOTS),
    "13": (CASE13_POSTS,),
    "16": (CASE16_POSTS,),
}

# Datasets conformados, en orden de exportación (dimensiones antes del hecho).
CONFORMED_DATASETS: tuple[DatasetContract, ...] = (
    DIM_CASE,
    DIM_CHANNEL,
    DIM_DATE,
    FACT_EVENTS,
)

# Todos los datasets indexados por nombre.
DATASETS: dict[str, DatasetContract] = {
    contract.name: contract
    for contract in (
        *(c for group in RAW_DATASETS.values() for c in group),
        *CONFORMED_DATASETS,
    )
}

# Casos con adaptador de Power BI.
SUPPORTED_CASES: tuple[str, ...] = tuple(sorted(RAW_DATASETS))

# Contenido estático de dim_case.
CASE_DIMENSION_ROWS: tuple[dict[str, str], ...] = (
    {
        "case_id": "09",
        "case_name": "09-python-to-gateway",
        "origin_stack": "Python",
        "dest_stack": "FastAPI",
        "engine": "duckdb",
    },
    {
        "case_id": "13",
        "case_name": "13-node-to-go-kafka",
        "origin_stack": "Node.js + Kafka",
        "dest_stack": "Go consumer",
        "engine": "clickhouse",
    },
    {
        "case_id": "16",
        "case_name": "16-graphql-to-hasura",
        "origin_stack": "Apollo GraphQL",
        "dest_stack": "Hasura",
        "engine": "timescaledb",
    },
)


def datasets_for_case(case_id: str) -> tuple[DatasetContract, ...]:
    """Devuelve los contratos crudos de ``case_id``."""
    try:
        return RAW_DATASETS[case_id]
    except KeyError as exc:
        raise KeyError(
            f"el caso {case_id!r} no tiene adaptador de Power BI; "
            f"soportados: {', '.join(SUPPORTED_CASES)}"
        ) from exc
