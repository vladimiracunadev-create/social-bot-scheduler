//! ================================================================================================
//! EMISOR MQTT EN RUST (Case 17: Rust MQTT -> Mosquitto -> Node -> InfluxDB)
//! ================================================================================================
//! Publica los posts programados en el broker Mosquitto vía MQTT (rumqttc, API síncrona). El
//! subscriber Node consume del mismo topic y persiste en InfluxDB. Rust aporta seguridad de memoria
//! y un binario pequeño (perfil release con LTO + strip) para el rol de publisher de baja latencia.
//!
//! Sin TLS (default-features = false): el broker es local dentro de la red del laboratorio.

use rumqttc::{Client, MqttOptions, QoS};
use serde_json::Value;
use std::{env, fs, thread, time::Duration};

fn main() {
    let host = env::var("MQTT_HOST").unwrap_or_else(|_| "localhost".to_string());
    let port: u16 = env::var("MQTT_PORT")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(1883);
    let topic = env::var("MQTT_TOPIC").unwrap_or_else(|_| "social/posts".to_string());

    let mut opts = MqttOptions::new("case17-rust-publisher", &host, port);
    opts.set_keep_alive(Duration::from_secs(5));

    let (client, mut connection) = Client::new(opts, 10);

    // El event loop debe drenarse para que las publicaciones salgan; lo movemos a un hilo.
    let handle = thread::spawn(move || {
        for notification in connection.iter() {
            if notification.is_err() {
                break;
            }
        }
    });

    let raw = fs::read_to_string("posts.json").expect("no se pudo leer posts.json");
    let posts: Vec<Value> = serde_json::from_str(&raw).expect("posts.json no es JSON válido");

    for post in &posts {
        let published = post
            .get("published")
            .and_then(Value::as_bool)
            .unwrap_or(false);
        if published {
            continue;
        }
        let payload = serde_json::to_string(post).unwrap();
        let id = post.get("id").and_then(Value::as_str).unwrap_or("?");
        match client.publish(&topic, QoS::AtLeastOnce, false, payload.into_bytes()) {
            Ok(_) => println!("[OK] Publicado {id} en topic '{topic}'"),
            Err(e) => eprintln!("[ERROR] Fallo publicando {id}: {e}"),
        }
        thread::sleep(Duration::from_millis(200));
    }

    // Damos margen a que se vacíe la cola y cerramos limpio.
    thread::sleep(Duration::from_millis(500));
    let _ = client.disconnect();
    let _ = handle.join();
}
