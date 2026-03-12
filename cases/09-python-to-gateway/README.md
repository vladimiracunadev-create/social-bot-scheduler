# Case 09: Python -> n8n -> FastAPI Gateway

Caso de integracion donde un bot Python publica un payload operativo hacia n8n, n8n aplica guardrails y reenvia la solicitud a un Integration Gateway en FastAPI autenticado con `X-API-Key`.

## Flujo

`Python bot -> n8n webhook -> FastAPI gateway -> DuckDB -> dashboard`

## Credenciales de desarrollo

- `INTEGRATION_API_KEY=SocialBotLocalKey2026!`
- `GITHUB_TOKEN=` opcional para modo real

## Demo

```bash
make up
make demo09
```

Luego abre `http://localhost:8090`.
