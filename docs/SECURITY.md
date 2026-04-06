# Seguridad y buenas practicas

Resumen operativo para este laboratorio:

- usa `.env.example` para un arranque local mas seguro
- usa `.env.demo.example` solo para demos en localhost
- usa `make up-edge` solo cuando realmente necesites acceso remoto controlado y ya tengas `EDGE_BASIC_AUTH_HASH`
- no expongas n8n, Grafana, Prometheus, cAdvisor ni los dashboards de casos a Internet
- trata `cAdvisor` como perfil de alto privilegio por sus montajes del host
- no reutilices credenciales demo fuera de un entorno controlado

Para el detalle completo de la postura de runtime, secretos, edge profile y supply chain, consulta [SECURITY.md](../SECURITY.md) y [RUNTIME_SECURITY.md](RUNTIME_SECURITY.md).
