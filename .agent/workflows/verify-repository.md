---
description: How to verify the functional and structural health of the repository
---

To verify that the repository is working correctly, follow these steps:

1. **Check System Health & Resources**
// turbo
```bash
make doctor
```
Verifies Docker versions, case manifests, and host resources (RAM/Disk).

2. **Verify Resource Check Logic**
// turbo
```bash
python check_resources.py
```
Ensures the local resources JSON is generated correctly for the dashboard.

3. **Validate Code Style and Security**
// turbo
```bash
black --check .
```
// turbo
```bash
pip-audit --ignore-vuln CVE-2026-1703
```

4. **Start Infrastructure (Optional but recommended for Full Test)**
// turbo
```bash
make up
```

5. **Test Integration**
Use the CLI to test a sample case:
// turbo
```bash
python hub.py ejecutar 01-python-to-php
```

6. **Check Terminal Logs**
// turbo
```bash
docker-compose logs --tail=20
```
