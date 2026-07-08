package socialbot;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestTemplate;

/**
 * ================================================================================================
 * EMISOR SPRING BOOT (Case 10: Java Spring Boot -> n8n -> Kotlin Ktor + PostgreSQL)
 * ================================================================================================
 * Representa el stack JVM "enterprise clásico": Spring Boot con el modelo MVC bloqueante y
 * RestTemplate. Contrasta con el receptor Ktor (no-bloqueante, corrutinas). Lee posts.json y
 * reenvía los vencidos al webhook de n8n. Modo dry-run si WEBHOOK_URL no está definido.
 */
@SpringBootApplication
public class OrderPublisher implements CommandLineRunner {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static void main(String[] args) {
        SpringApplication.run(OrderPublisher.class, args);
    }

    @Override
    public void run(String... args) throws Exception {
        String webhook = System.getenv("WEBHOOK_URL");
        Path postsFile = Path.of(System.getenv().getOrDefault("POSTS_FILE", "posts.json"));

        JsonNode posts = MAPPER.readTree(Files.readString(postsFile));
        RestTemplate http = new RestTemplate();
        Instant now = Instant.now();

        for (JsonNode post : posts) {
            boolean published = post.path("published").asBoolean(false);
            if (published) {
                continue;
            }
            String id = post.path("id").asText();
            if (webhook == null || webhook.isBlank()) {
                System.out.println("[DRY-RUN] Post " + id + " reenviado.");
                continue;
            }
            try {
                Map<String, Object> body = new HashMap<>();
                body.put("id", id);
                body.put("text", post.path("text").asText());
                body.put("channel", post.path("channel").asText("default"));
                body.put("scheduled_at", post.path("scheduled_at").asText(""));

                org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                http.postForEntity(webhook, new org.springframework.http.HttpEntity<>(body, headers), String.class);
                System.out.println("[OK] Post " + id + " aceptado por n8n.");
            } catch (Exception e) {
                System.out.println("[ERROR] Fallo reenviando " + id + ": " + e.getMessage());
            }
        }
        System.out.println("Emisor Spring Boot finalizado.");
    }
}
