use std::thread;
use std::time::Duration;
use std::env;
use serde::{Deserialize, Serialize};
use dotenv::dotenv;

#[derive(Serialize, Deserialize)]
struct Post {
    id: u32,
    content: String,
    platform: String,
}

fn main() {
    dotenv().ok();
    let webhook_url = env::var("WEBHOOK_URL").expect("WEBHOOK_URL not set");
    println!("🚀 Rust Social Bot Producer started...");
    println!("🎯 Target: {}", webhook_url);

    let posts = vec![
        Post { id: 1, content: "Rust es increíblemente rápido y seguro. 🦀".to_string(), platform: "twitter".to_string() },
        Post { id: 2, content: "La gestión de memoria en Rust es única. 🧠".to_string(), platform: "facebook".to_string() },
        Post { id: 3, content: "Sinatra y Ruby hacen una gran pareja con Rust. 💎".to_string(), platform: "instagram".to_string() },
    ];

    let client = reqwest::blocking::Client::new();

    loop {
        for post in &posts {
            println!("📤 Sending post {}: {}", post.id, post.content);
            match client.post(&webhook_url).json(post).send() {
                Ok(resp) => println!("✅ Status: {}", resp.status()),
                Err(e) => println!("❌ Error: {}", e),
            }
            thread::sleep(Duration::from_secs(5));
        }
    }
}
