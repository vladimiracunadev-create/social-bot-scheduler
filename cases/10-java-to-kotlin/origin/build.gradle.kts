// Case 10 — Emisor Java (Spring Boot, modelo bloqueante MVC) que reenvía a n8n.
plugins {
    java
    id("org.springframework.boot") version "4.1.2"
    id("io.spring.dependency-management") version "1.1.7"
}

group = "socialbot"
version = "1.0.0"

java { toolchain { languageVersion.set(JavaLanguageVersion.of(21)) } }

repositories { mavenCentral() }

// Spring Boot 3.5.16 gestiona jackson-bom 2.21.4, que arrastra jackson-databind
// con advisories abiertos (GHSA-5gvw-p9qm-jgwh y otros 8). Subir la propiedad del
// BOM reemplaza toda la familia Jackson de una vez.
ext["jackson-bom.version"] = "2.21.8"

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
}
