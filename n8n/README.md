# 🔧 n8n Auto-Configuration

Esta carpeta contiene la configuración necesaria para que **n8n se auto-configure** al arrancar con Docker Compose.

## Contenido

### `workflows/`
Los 9 workflows de integraci?n pre-configurados, listos para importaci?n autom?tica:

| Archivo | Caso | Ruta Origen → Destino |
|---------|------|-----------------------|
| `case-01-python-to-php.json` | 01 | Python → n8n → PHP |
| `case-02-python-to-go.json` | 02 | Python → n8n → Go |
| `case-03-go-to-node.json` | 03 | Go → n8n → Node.js |
| `case-04-node-to-fastapi.json` | 04 | Node.js → n8n → FastAPI |
| `case-05-laravel-to-react.json` | 05 | Laravel → n8n → React |
| `case-06-go-to-symfony.json` | 06 | Go → n8n → Symfony |
| `case-07-rust-to-ruby.json` | 07 | Rust → n8n → Ruby |
| `case-08-csharp-to-flask.json` | 08 | C# → n8n → Flask |
| `case-09-python-to-gateway.json` | 09 | Python -> n8n -> FastAPI Gateway |

## ¿Cómo funciona?

Al ejecutar `docker-compose up -d`, el contenedor de n8n usa un entrypoint personalizado (`scripts/n8n_auto_setup.sh`) que:

1. **Arranca n8n** en segundo plano
2. **Espera** a que esté listo (health check)
3. **Crea** un usuario administrador automáticamente
4. **Importa** los 9 workflows desde esta carpeta
5. **Activa** todos los workflows
6. **Marca** la importación como completada (no se repite en reinicios)

### Credenciales por defecto (Laboratorio)

| Campo | Valor |
|-------|-------|
| Email | `admin@social-bot.local` |
| Password | `SocialBot2026!` |

> ⚠️ Estas son credenciales de laboratorio/demo. No usar en producción.

## ¿Necesito hacer algo manualmente?

**No.** Todo es automático. Solo necesitas:

```bash
docker-compose up -d
```

Y esperar ~30 segundos. Luego puedes verificar en [http://localhost:5678](http://localhost:5678).

## ¿Cómo agregar un nuevo workflow?

1. Crea el archivo JSON del workflow en `n8n/workflows/`
2. Reinicia n8n: `docker-compose restart n8n`
3. O bien, borra el marcador para forzar re-importación:
   ```bash
   docker-compose exec n8n rm /home/node/.n8n/.workflows_imported
   docker-compose restart n8n
   ```
