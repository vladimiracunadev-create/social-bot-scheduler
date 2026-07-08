/**
 * ==================================================================================================
 * RECEPTOR KOTLIN/KTOR (Case 10: Java Spring Boot -> n8n -> Kotlin Ktor + PostgreSQL)
 * ==================================================================================================
 * Contraste didáctico con el emisor Spring MVC (bloqueante): Ktor es un servidor asíncrono sobre
 * corrutinas. Cada request se maneja en un contexto suspendible sobre el event-loop de Netty, sin
 * bloquear hilos. Persistencia en PostgreSQL vía JDBC directo (sin ORM) para mantener el binario
 * ligero y el flujo explícito.
 *
 * Cumple el contrato REST homogéneo del laboratorio: /webhook, /errors, /logs, /health, /.
 */

import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.*
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.plugins.statuspages.StatusPages
import io.ktor.server.request.receive
import io.ktor.server.response.respond
import io.ktor.server.response.respondText
import io.ktor.server.routing.get
import io.ktor.server.routing.post
import io.ktor.server.routing.routing
import io.ktor.http.HttpStatusCode
import kotlinx.serialization.Serializable
import java.sql.Connection
import java.sql.DriverManager

// --- Configuración 12-Factor ---
private val PORT = System.getenv("PORT")?.toIntOrNull() ?: 8080
private val DB_HOST = System.getenv("DB_HOST") ?: "db-postgres-10"
private val DB_NAME = System.getenv("DB_NAME") ?: "social_bot"
private val DB_USER = System.getenv("DB_USER") ?: "postgres"
private val DB_PASS = System.getenv("DB_PASS") ?: "change-me"
private val JDBC_URL = "jdbc:postgresql://$DB_HOST:5432/$DB_NAME"

@Serializable
data class Post(
    val id: String? = null,
    val text: String? = null,
    val channel: String = "default",
    val scheduled_at: String? = null,
)

@Serializable
data class Ok(val ok: Boolean, val message: String = "", val case: String = "", val engine: String = "")

@Serializable
data class Logs(val ok: Boolean, val logs: List<String>)

@Serializable
data class Err(val ok: Boolean, val error: String)

private fun db(): Connection = DriverManager.getConnection(JDBC_URL, DB_USER, DB_PASS)

private fun initDb() {
    // Reintenta hasta que Postgres acepte conexiones (el healthcheck del compose ya lo espera).
    repeat(30) { attempt ->
        try {
            db().use { c ->
                c.createStatement().execute(
                    """CREATE TABLE IF NOT EXISTS social_posts (
                           id TEXT PRIMARY KEY,
                           text TEXT NOT NULL,
                           channel TEXT NOT NULL DEFAULT 'default',
                           scheduled_at TEXT,
                           created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                       )"""
                )
            }
            println("[bootstrap] Tabla social_posts lista en PostgreSQL.")
            return
        } catch (e: Exception) {
            println("[bootstrap] Postgres no listo (intento ${attempt + 1}): ${e.message}")
            Thread.sleep(2000)
        }
    }
    error("No se pudo inicializar PostgreSQL a tiempo.")
}

fun main() {
    initDb()
    embeddedServer(Netty, port = PORT, host = "0.0.0.0", module = Application::module).start(wait = true)
}

fun Application.module() {
    install(ContentNegotiation) { json() }
    install(StatusPages) {
        exception<Throwable> { call, cause ->
            call.respond(HttpStatusCode.InternalServerError, Err(false, cause.message ?: "error"))
        }
    }
    routing {
        get("/health") { call.respond(Ok(true, engine = "postgresql")) }

        post("/webhook") {
            val post = call.receive<Post>()
            if (post.id.isNullOrBlank() || post.text.isNullOrBlank()) {
                call.respond(HttpStatusCode.UnprocessableEntity, Err(false, "id y text son obligatorios"))
                return@post
            }
            db().use { c ->
                c.prepareStatement(
                    """INSERT INTO social_posts (id, text, channel, scheduled_at)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT (id) DO UPDATE SET text = EXCLUDED.text"""
                ).use { st ->
                    st.setString(1, post.id)
                    st.setString(2, post.text)
                    st.setString(3, post.channel)
                    st.setString(4, post.scheduled_at)
                    st.executeUpdate()
                }
            }
            println("Post persistido en PostgreSQL: ${post.id}")
            call.respond(Ok(true, "Post persistido en PostgreSQL (Ktor)", "10-java-to-kotlin"))
        }

        post("/errors") {
            val body = call.receive<Map<String, String>>()
            println("Error en DLQ: $body")
            call.respond(Ok(true, "Error registrado en DLQ"))
        }

        get("/logs") {
            val logs = mutableListOf<String>()
            db().use { c ->
                c.prepareStatement(
                    "SELECT id, channel, text, created_at FROM social_posts ORDER BY created_at DESC LIMIT 20"
                ).use { st ->
                    val rs = st.executeQuery()
                    while (rs.next()) {
                        logs.add(
                            "[${rs.getString("created_at")}] POSTGRES | id=${rs.getString("id")} " +
                                "| channel=${rs.getString("channel")} | text=${rs.getString("text")}"
                        )
                    }
                }
            }
            call.respond(Logs(true, logs))
        }

        get("/") {
            val html = Application::class.java.classLoader.getResource("index.html")?.readText()
                ?: "<h1>Dashboard no encontrado</h1>"
            call.respondText(html, io.ktor.http.ContentType.Text.Html)
        }
    }
}
