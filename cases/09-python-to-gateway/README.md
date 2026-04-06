# Case 09: Python -> n8n -> FastAPI Gateway

Caso de integracion donde un bot Python publica un payload operativo hacia n8n, n8n aplica guardrails y reenvia la solicitud a un Integration Gateway en FastAPI autenticado con `X-API-Key`.

## Flujo

`Python bot -> n8n webhook -> FastAPI gateway -> DuckDB -> dashboard`

## Secretos y modo de ejecucion

- `INTEGRATION_API_KEY` es obligatorio. El gateway ya no acepta una clave demo embebida en el codigo.
- `GITHUB_TOKEN` es opcional y solo habilita el modo real del proveedor.
- Para laboratorio local puedes copiar `.env.demo.example` a `.env`.
- Para un arranque mas seguro usa `.env.example`, define tus propios valores y mantén los puertos en `127.0.0.1`.

## Demo

```bash
make up
make demo09
```

Luego abre `http://localhost:8090`.
