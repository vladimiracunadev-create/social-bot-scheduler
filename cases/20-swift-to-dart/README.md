# 🧩 Caso 20: 🍎 Swift (Vapor) -> 🌉 n8n -> 🎯 Dart (Shelf) -> 🔥 Firebase Emulator

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Language: Swift](https://img.shields.io/badge/Language-Swift-F05138?logo=swift&logoColor=white)](https://swift.org/)
[![Language: Dart](https://img.shields.io/badge/Language-Dart-0175C2?logo=dart&logoColor=white)](https://dart.dev/)
[![Backend: Firebase](https://img.shields.io/badge/Backend-Firebase%20Emulator-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/docs/emulator-suite)

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Solo scaffolding y diseño.

Cubre el ecosistema **mobile-backend**: dos lenguajes asociados a apps móviles (Swift = iOS, Dart = Flutter) ejecutándose **server-side**, con Firebase Emulator Suite local para evitar dependencia de la nube de Google.

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: `Publisher.swift` (Vapor 4 sobre Swift on Linux) — async/await nativo.
2. **🌉 Puente**: **n8n** — webhook estándar.
3. **📥 Destino**: `server.dart` (Shelf + `shelf_router`) — handler async con isolates.
4. **📁 Persistencia**: **Firebase Emulator Suite local** — Firestore + Auth + Cloud Functions emulados.

> [!NOTE]
> Se usa la **CLI `firebase emulators:start`** para mantener el laboratorio 100% offline. Sin claves de proyecto reales.

---

## 🎯 Objetivos didácticos

- Swift on Linux: ecosistema fuera de Apple, paquetes con SwiftPM.
- Dart server-side: alternativa al stack Node con tipado estático.
- Firestore: NoSQL documental con sub-collections y reglas declarativas.
- Patrón mobile-backend: cómo el backend "habla móvil" sin ser el cliente.

---

## ⚠️ Consideraciones operacionales

- Imagen Swift Linux pesada (~500 MB). Usar multi-stage build agresivo.
- Firebase Emulator Suite requiere Java 11+ y Node.js para correr.
- **NUNCA** mezclar emulador local con proyecto Firebase real → variables de entorno claras.

---

## 📋 TODO de implementación

- [ ] `Package.swift` Vapor 4 con módulos mínimos.
- [ ] `pubspec.yaml` Dart con `shelf` + `firebase_dart`.
- [ ] `firebase.json` configurando emuladores: firestore, auth, functions, storage.
- [ ] Reglas Firestore versionadas en `dest/firestore.rules`.
- [ ] Workflow n8n `case20-mobile-backend.json`.
- [ ] Perfil `case20` en `docker-compose.yml`.

---

*Pendiente — parte del backlog exploratorio v5.0+.*
