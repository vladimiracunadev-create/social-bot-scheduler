// ==================================================================================================
// Case 10 — Receptor Kotlin/Ktor (no-bloqueante) + PostgreSQL.
// ==================================================================================================
plugins {
    kotlin("jvm") version "2.0.21"
    kotlin("plugin.serialization") version "2.0.21"
    application
    id("com.gradleup.shadow") version "8.3.5"
}

group = "socialbot"
version = "1.0.0"

repositories { mavenCentral() }

val ktorVersion = "2.3.13"

dependencies {
    implementation("io.ktor:ktor-server-core-jvm:$ktorVersion")
    implementation("io.ktor:ktor-server-netty-jvm:$ktorVersion")
    implementation("io.ktor:ktor-server-content-negotiation-jvm:$ktorVersion")
    implementation("io.ktor:ktor-serialization-kotlinx-json-jvm:$ktorVersion")
    implementation("io.ktor:ktor-server-status-pages-jvm:$ktorVersion")
    implementation("org.postgresql:postgresql:42.7.4")
    implementation("ch.qos.logback:logback-classic:1.5.12")
}

application {
    mainClass.set("ApplicationKt")
}

kotlin { jvmToolchain(21) }
