// ==================================================================================================
// EMISOR DE MÁXIMA SEGURIDAD (Case 07: Rust -> n8n -> Ruby/Sinatra + Cassandra)
// ==================================================================================================
// ¿Por qué Rust para el emisor?
// Rust es el lenguaje de sistemas más seguro disponible. A diferencia de C/C++, su sistema de 
// Ownership y Borrowing elimina toda una categoría de bugs (Use-After-Free, Data Races, Buffer 
// Overflows) en TIEMPO DE COMPILACIÓN, sin Garbage Collector.
// 
// En este caso, Rust actúa como el productor más exigente del ecosistema. Si el bot puede 
// enviar datos correctamente desde Rust, cualquier otro lenguaje también puede.
// 
// Conceptos Clave de Rust en este archivo:
// - `#[derive(Serialize, Deserialize)]`: Macros que generan código automáticamente (Metaprogramming).
// - `match`: Pattern Matching exhaustivo que OBLIGA a manejar éxito Y error (Result<T, E>).
// - `&posts`: Referencia compartida para evitar la transferencia de propiedad (Move Semantics).
// - `reqwest::blocking`: Cliente HTTP síncrono (en prod se usaría `tokio` para async).

use std::thread;
use std::time::Duration;
use std::env;
use serde::{Deserialize, Serialize};
use dotenv::dotenv;

// =================================================================================================
// ESTRUCTURAS DE DATOS (Structs)
// =================================================================================================

// Derive macro: Genera automáticamente código para Serialización/Deserialización (Serde).
// En Rust, la memoria es gestionada sin Garbage Collector, mediante el sistema de Ownership.
#[derive(Serialize, Deserialize)]
struct Post {
    id: u32,
    text: String,
    channel: String,
}

// =================================================================================================
// FUNCIÓN PRINCIPAL
// =================================================================================================

fn main() {
    // Carga de variables de entorno desde .env (si existe)
    dotenv().ok();
    
    // ".expect()" maneja el Result: Si falla (None/Err), hace Panic con el mensaje.
    // Es la forma idiomática de "Fail Fast" en arranque.
    let webhook_url = env::var("WEBHOOK_URL").expect("WEBHOOK_URL not set");
    
    println!("🚀 Rust Social Bot Producer started...");
    println!("🎯 Target: {}", webhook_url);

    // Vector de Posts (Heap Allocation)
    // El macro vec! simplifica la creación de arrays dinámicos.
    let posts = vec![
        Post { id: 1, text: "Rust es increíblemente rápido y seguro. 🦀".to_string(), channel: "twitter".to_string() },
        Post { id: 2, text: "La gestión de memoria en Rust es única. 🧠".to_string(), channel: "facebook".to_string() },
        Post { id: 3, text: "Sinatra y Ruby hacen una gran pareja con Rust. 💎".to_string(), channel: "instagram".to_string() },
    ];

    // Cliente HTTP Bloqueante
    // Para simplificar este ejemplo, no usamos tokio (async runtime).
    // En producción de alto rendimiento, usaríamos `reqwest` async con `tokio`.
    let client = reqwest::blocking::Client::new();

    // Bucle Infinito (Daemon)
    loop {
        // Iteramos sobre referencias (&posts) para no "mover" (Move Semantics) el vector
        // y poder reutilizarlo en la siguiente iteración.
        for post in &posts {
            println!("📤 Sending post {}: {}", post.id, post.text);
            
            // Pattern Matching para manejo de errores (Result<T, E>)
            // Rust te obliga a manejar explícitamente el éxito y el fracaso.
            match client.post(&webhook_url).json(post).send() {
                Ok(resp) => println!("✅ Status: {}", resp.status()),
                Err(e) => println!("❌ Error: {}", e),
            }
            
            // Pausa del hilo principal
            thread::sleep(Duration::from_secs(5));
        }
    }
}
