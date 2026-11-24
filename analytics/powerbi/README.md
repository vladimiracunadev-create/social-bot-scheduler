# `analytics/powerbi` — capa analítica para Power BI

Módulo independiente y **opcional** que exporta a CSV, en solo lectura, los
datos reales de los casos del laboratorio, para consumirlos desde Power BI
Desktop sin cuenta ni servicios en la nube.

No vive en `cases/` porque no es un caso de integración: es una superficie
analítica que se apoya en los que ya existen. No entra en el perfil Docker
`full`.

> **Documentación completa, con el paso a paso y las capturas de Power BI:**
> [`docs/POWER_BI_INTEGRATION.md`](../../docs/POWER_BI_INTEGRATION.md)

---

## Uso rápido

```powershell
python -m analytics.powerbi.cli list
```

```powershell
python -m analytics.powerbi.cli sample --out analytics/powerbi/samples
```

```powershell
python -m analytics.powerbi.cli export --case 09 --out analytics/powerbi/exports/case09
```

```powershell
python -m analytics.powerbi.cli merge --dir analytics/powerbi/exports/case09 --dir analytics/powerbi/exports/case13 --out analytics/powerbi/exports/all
```

```powershell
python -m analytics.powerbi.cli validate --dir analytics/powerbi/exports/all
```

`export` necesita el caso levantado. `sample`, `merge` y `validate` no
necesitan Docker.

---

## Estructura

| Fichero | Responsabilidad |
| :--- | :--- |
| `contracts.py` | contratos de dataset: nombre, columnas, tipos, grano |
| `redaction.py` | lista de denegación de columnas y truncado de texto libre |
| `transport.py` | guardia de solo lectura y transporte `docker exec` |
| `sources/case09.py` | DuckDB (fichero local con fallback al contenedor) |
| `sources/case13.py` | ClickHouse (`clickhouse-client`, o HTTP con `readonly=1`) |
| `sources/case16.py` | TimescaleDB (`psql --csv`, sesión en solo lectura) |
| `normalize.py` | esquema en estrella conformado a partir de los crudos |
| `writer.py` | CSV UTF-8 con BOM, `manifest.json` con SHA-256, validación |
| `sample_data.py` | datos sintéticos deterministas |
| `cli.py` | interfaz de línea de comandos |
| `dax/measures.dax` | medidas DAX del modelo |
| `model/DATA_MODEL.md` | relaciones, tipos, granos y claves |
| `reports/` | un `.pbix` por caso, listo para abrir |
| `samples/` | exportación sintética versionada |
| `exports/` | exportaciones reales (ignoradas por git) |

---

## Añadir un caso nuevo

Dos piezas, el resto es común:

1. un `DatasetContract` en `contracts.py`, añadido a `RAW_DATASETS`;
2. una clase en `sources/` que herede de `CaseSource` e implemente
   `available()`, `describe()` y `fetch_page()`, registrada en
   `sources/__init__.py`.

Si el caso aporta un tipo de evento nuevo, se mapea en
`normalize.build_fact_events()`. Las pruebas de `tests/powerbi/` recorren
todos los contratos declarados, así que un contrato nuevo queda cubierto por
las comprobaciones de redacción sin escribir nada más.

---

## Garantías

- **Solo lectura.** Toda sentencia pasa por `assert_read_only()`, y además cada
  motor se abre en modo lectura (`read_only=True`, `readonly=1`,
  `default_transaction_read_only=on`).
- **Sin credenciales en la exportación.** La lista de denegación se aplica al
  contrato y a cada fila; `api_key_prefix` y `api_key_hash` del caso 09 nunca
  salen.
- **Sin secretos en `argv`.** Las contraseñas viajan por el entorno del proceso
  cliente (`docker exec -e NOMBRE`, sin valor).
- **Volumen acotado.** Paginación obligatoria y techo de filas.
- **Reproducible.** El `manifest.json` registra filas y SHA-256 de cada CSV.

```powershell
python -m pytest tests/powerbi -q
```
