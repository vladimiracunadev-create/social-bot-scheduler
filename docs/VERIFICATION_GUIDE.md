# 🚦 Guía de Verificación — Social Bot Scheduler

Esta guía detalla los procedimientos para validar la integridad, seguridad y funcionalidad del laboratorio tras cualquier cambio en el entorno de runtime.

---

## 🛡️ 1. Auditoría de Seguridad y Cadena de Suministro

> [!IMPORTANT]
> **Mitigación Trivy**: Asegúrate de que el flujo de CI/CD esté utilizando la versión **`v0.35.0`** o superior para evitar vulnerabilidades de "tag-poisoning".

### 1a. Diagnóstico de Hardening (compose/Dockerfiles)
Valida que la configuración de Docker y los secretos sigan los estándares del proyecto:
```bash
python scripts/check_runtime_security.py
```

### 1b. Detección de Unicode bidi y ofuscación (supply chain)
Escanea el código fuente en busca de caracteres de control bidireccionales (CVE-2021-42574) y patrones de ofuscación `eval+base64`:
```bash
# El CI ejecuta esto automáticamente en el job supply-chain-checks.
# Para ejecutarlo localmente:
python - <<'PYEOF'
import sys, pathlib, re
BIDI = re.compile(r'[\u202a-\u202e\u2066-\u2069\u200f\u061c]')
EXTS = {'.py', '.js', '.go', '.rb', '.rs', '.sh', '.php'}
hits = [f'{p}:{n}' for p in pathlib.Path('.').rglob('*')
        if p.suffix in EXTS and p.is_file()
        for n, l in enumerate(p.read_text(errors='replace').splitlines(), 1)
        if BIDI.search(l)]
print('FAIL:', hits) if hits else print('OK: no bidi chars')
PYEOF
```

### 1c. Verificar security headers en producción local
Con el stack levantado, confirma que los headers estén activos:
```bash
curl -sI http://localhost:8080 | grep -E "X-Frame|X-Content|Content-Security|Permissions|Referrer"
```

---

## 🏗️ 2. Validación de Configuración (Docker)

Verifica que los perfiles y archivos compose se rendericen correctamente sin errores de sintaxis:

```bash
# Validar core y perfiles extendidos
docker-compose config
docker-compose --profile observability config
docker-compose --profile edge config
```

---

## 🌉 3. Validación del Orquestador (n8n)

Asegúrate de que n8n esté respondiendo y tenga los flujos importados correctamente:

```bash
python verify_n8n.py
```
**Puntos de control**:
- [ ] Salud del endpoint `/healthz`.
- [ ] Estado de los 9 flujos de la matriz (Active/Inactive).
- [ ] Conectividad con la base de datos interna.

---

## 🧩 4. Validación Funcional (E2E)

### Nivel 1: Smoke Test (Caso 01)
```bash
make up-secure
make demo
```

### Nivel 2: Integración Completa (Caso 09)
```bash
make demo09
```

### Nivel 3: Matriz Total
```bash
# Requiere perfil 'full' activo
python verify_all_cases.py
```

---

## 📊 5. Validación de Observabilidad

Si el stack de monitoreo está activo (`make up-observability`):

- **Prometheus**: `http://localhost:9090` (Check targets: `UP`).
- **Grafana**: `http://localhost:3000` (Verificar dashboards de contenedores).
- **cAdvisor**: `http://localhost:8089` (Métricas de runtime Docker).

---

## 🌐 6. Validación del Perfil Edge (Proxy)

Si el Caddy Reverse Proxy está en uso (`make up-edge`):

- **n8n**: `https://n8n.localhost`
- **Dashboard**: `https://grafana.localhost`
- **Gateway**: `https://gateway.localhost`

---

## 📝 Notas de Operación

- **Persistencia**: Si el login de n8n falla inexplicablemente, recrea el volumen: `docker volume rm social-bot-scheduler_n8n_data`.
- **Latencia**: Tras activar un workflow en n8n, espera ~10 segundos antes de disparar el bot de origen.
- **Entorno**: Si no tienes Docker disponible, limita las pruebas a `python -m py_compile` y validación estática de scripts.

---
*Manual de verificación v4.0 — Social Bot Scheduler*
