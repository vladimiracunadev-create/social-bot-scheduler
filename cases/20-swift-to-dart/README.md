# 🧩 Caso 20: 🍎 Swift → 🌉 n8n → 🎯 Dart (Shelf) + 🔥 Firestore emulator

[![Status: Ready](https://img.shields.io/badge/Status-Ready-brightgreen.svg)]()
[![Language: Swift](https://img.shields.io/badge/Language-Swift-FA7343?logo=swift&logoColor=white)](https://www.swift.org/)
[![Language: Dart](https://img.shields.io/badge/Language-Dart-0175C2?logo=dart&logoColor=white)](https://dart.dev/)
[![Database: Firestore](https://img.shields.io/badge/Database-Firestore%20(emulator)-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/docs/emulator-suite)

Stack **mobile-backend** con lenguajes server-side: emisor **Swift** (en Linux) y receptor **Dart** con **Shelf**, persistiendo en el **emulador de Firestore** de la Firebase Emulator Suite (local, sin cloud).

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/Sources/Publisher/main.swift`: emisor Swift que reenvía los posts vencidos al webhook de n8n con `URLSession`.
2. **🌉 Puente** — **n8n**: guardrails canónicos (fingerprint → circuit breaker → idempotencia → HTTP con reintentos → DLQ).
3. **📥 Destino** — `dest/bin/server.dart`: receptor **Dart/Shelf** (compilado AOT a binario nativo) que cumple el contrato REST.
4. **📁 Persistencia** — **Firestore emulator**: el receptor hace `PATCH`/`GET` a la API REST v1 del emulador (colección `social_posts`, documentos con `fields` tipados).

> [!NOTE]
> El emulador de Firestore (Firebase Emulator Suite) corre local, sin proyecto real ni credenciales cloud. La imagen pre-descarga el JAR del emulador en el build para arrancar sin red.

---

## 🚀 Cómo levantarlo

```bash
docker-compose --profile case20 up -d      # emulador Firestore + receptor Dart
```

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `firebase-emu-20` | Emulador de Firestore | interno (`:8200`) |
| `dest-dart-20` | Dart/Shelf + dashboard | **8100** |

- **Dashboard del caso**: <http://localhost:8100>
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-20**.

---

## 🎯 Objetivos didácticos

- **Swift y Dart server-side**: dos lenguajes "mobile-first" usados como backend compilado.
- **Firebase Emulator Suite**: desarrollo local contra Firestore sin tocar la nube.
- **API REST de Firestore**: documentos con `fields` tipados (`stringValue`, `integerValue`).

---

## ⚠️ Consideraciones (modelo del laboratorio)

- Puerto `8100` = `8080 + 20` (regla canónica, ver [docs/PORTS.md](../../docs/PORTS.md)).
- Bind a `127.0.0.1`; el receptor valida `id`/`text` (→ HTTP 422).
- El emulador (JVM) es el servicio pesado del caso; los datos no persisten entre reinicios.

---

## ✅ Estado

Implementado y verificado (build + boot + health). Parte del **Lote 3** del roadmap v5.0 → v4.7.
