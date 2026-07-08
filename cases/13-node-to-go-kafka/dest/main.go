// ================================================================================================
// CONSUMER GO + SINK CLICKHOUSE (Case 13: Node+Kafka -> n8n -> Go consumer -> ClickHouse)
// ================================================================================================
// Patrón CQRS / event-streaming: los posts entran como eventos a un topic Kafka y un consumer Go
// los proyecta ("sink") en ClickHouse, una BD columnar OLAP. Este servicio Go cumple un doble rol
// sobre el mismo topic:
//
//   1. PRODUCER: en el contrato REST del laboratorio (`POST /webhook`) publica el post en Kafka.
//   2. CONSUMER: una goroutine lee del topic y hace INSERT en ClickHouse (vía su interfaz HTTP).
//
// Así, tanto el emisor Node (que produce directo a Kafka) como n8n (HTTP -> /webhook -> Kafka)
// convergen en el mismo pipeline Kafka -> ClickHouse.
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"

	"github.com/segmentio/kafka-go"
)

var (
	kafkaBroker = getenv("KAFKA_BROKER", "kafka-13:9092")
	topic       = getenv("KAFKA_TOPIC", "social-posts")
	chURL       = getenv("CLICKHOUSE_URL", "http://clickhouse-13:8123")
	chUser      = getenv("CLICKHOUSE_USER", "sbuser")
	chPass      = getenv("CLICKHOUSE_PASSWORD", "change-me-case13-local")
	httpPort    = getenv("PORT", "8080")
)

type Post struct {
	ID          string `json:"id"`
	Text        string `json:"text"`
	Channel     string `json:"channel"`
	ScheduledAt string `json:"scheduled_at"`
}

func getenv(k, d string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return d
}

// --- ClickHouse (interfaz HTTP) ---
func chExec(query string, body []byte) ([]byte, error) {
	u := chURL + "/?query=" + url.QueryEscape(query)
	req, err := http.NewRequest("POST", u, bytes.NewReader(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("X-ClickHouse-User", chUser)
	req.Header.Set("X-ClickHouse-Key", chPass)
	req.Header.Set("Content-Type", "text/plain")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	b, _ := io.ReadAll(resp.Body)
	if resp.StatusCode >= 300 {
		return b, fmt.Errorf("clickhouse %d: %s", resp.StatusCode, string(b))
	}
	return b, nil
}

func initClickHouse() {
	// ReplacingMergeTree ORDER BY id: idempotente por id (los duplicados por re-consumo se
	// colapsan en el merge), coherente con el ON CONFLICT del resto de casos.
	ddl := `CREATE TABLE IF NOT EXISTS social_posts (
		id String, text String, channel String,
		created_at DateTime DEFAULT now()
	) ENGINE = ReplacingMergeTree ORDER BY id`
	for i := 0; i < 40; i++ {
		if _, err := chExec(ddl, nil); err == nil {
			log.Println("[bootstrap] Tabla social_posts lista en ClickHouse.")
			return
		} else {
			log.Printf("[bootstrap] ClickHouse no listo (intento %d): %v", i+1, err)
		}
		time.Sleep(2 * time.Second)
	}
	log.Fatal("No se pudo inicializar ClickHouse a tiempo.")
}

// --- Kafka ---
var writer *kafka.Writer

func initKafka() {
	writer = &kafka.Writer{
		Addr:                   kafka.TCP(kafkaBroker),
		Topic:                  topic,
		Balancer:               &kafka.LeastBytes{},
		AllowAutoTopicCreation: true,
	}
}

// Asegura que el topic exista antes de que arranque el consumer (DialLeader lo crea si
// auto-create está habilitado). Evita que el lector se cuelgue esperando un topic inexistente.
func ensureTopic() {
	for i := 0; i < 20; i++ {
		conn, err := kafka.DialLeader(context.Background(), "tcp", kafkaBroker, topic, 0)
		if err == nil {
			_ = conn.Close()
			log.Printf("[bootstrap] Topic %s listo.", topic)
			return
		}
		log.Printf("[bootstrap] topic no listo (intento %d): %v", i+1, err)
		time.Sleep(2 * time.Second)
	}
}

// Consumer: lee la partición 0 desde el inicio (sin grupo, sin coordinación) y proyecta cada
// evento en ClickHouse. Simple y determinista para el laboratorio de un solo broker/partición.
func consumeLoop() {
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:   []string{kafkaBroker},
		Topic:     topic,
		Partition: 0,
		MaxBytes:  10e6,
	})
	defer reader.Close()
	if err := reader.SetOffset(kafka.FirstOffset); err != nil {
		log.Printf("[consumer] SetOffset: %v", err)
	}
	for {
		m, err := reader.ReadMessage(context.Background())
		if err != nil {
			log.Printf("[consumer] error: %v", err)
			time.Sleep(2 * time.Second)
			continue
		}
		var p Post
		if err := json.Unmarshal(m.Value, &p); err != nil {
			continue
		}
		row, _ := json.Marshal(map[string]string{"id": p.ID, "text": p.Text, "channel": p.Channel})
		if _, err := chExec("INSERT INTO social_posts (id, text, channel) FORMAT JSONEachRow", row); err != nil {
			log.Printf("[sink] error insertando en ClickHouse: %v", err)
		} else {
			log.Printf("[sink] Post proyectado en ClickHouse: %s", p.ID)
		}
	}
}

// --- HTTP (contrato REST del laboratorio) ---
func writeJSON(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(v)
}

func main() {
	initClickHouse()
	initKafka()
	ensureTopic()
	go consumeLoop()

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, 200, map[string]any{"ok": true, "engine": "kafka+clickhouse"})
	})

	http.HandleFunc("/webhook", func(w http.ResponseWriter, r *http.Request) {
		var p Post
		if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
			writeJSON(w, 400, map[string]any{"ok": false, "error": "JSON invalido"})
			return
		}
		if p.ID == "" || p.Text == "" {
			writeJSON(w, 422, map[string]any{"ok": false, "error": "id y text son obligatorios"})
			return
		}
		if p.Channel == "" {
			p.Channel = "default"
		}
		val, _ := json.Marshal(p)
		if err := writer.WriteMessages(context.Background(), kafka.Message{Key: []byte(p.ID), Value: val}); err != nil {
			writeJSON(w, 502, map[string]any{"ok": false, "error": err.Error()})
			return
		}
		writeJSON(w, 200, map[string]any{"ok": true, "message": "Post publicado en Kafka (sink -> ClickHouse)", "case": "13-node-to-go-kafka"})
	})

	http.HandleFunc("/errors", func(w http.ResponseWriter, r *http.Request) {
		b, _ := io.ReadAll(r.Body)
		log.Printf("Error en DLQ: %s", string(b))
		writeJSON(w, 200, map[string]any{"ok": true, "message": "Error registrado en DLQ"})
	})

	http.HandleFunc("/logs", func(w http.ResponseWriter, r *http.Request) {
		q := "SELECT id, channel, text, toString(created_at) AS ca FROM social_posts ORDER BY created_at DESC LIMIT 20 FORMAT JSONEachRow"
		b, err := chExec(q, nil)
		if err != nil {
			writeJSON(w, 502, map[string]any{"ok": false, "error": err.Error(), "logs": []string{}})
			return
		}
		logs := []string{}
		for _, line := range strings.Split(strings.TrimSpace(string(b)), "\n") {
			if line == "" {
				continue
			}
			var row map[string]string
			if json.Unmarshal([]byte(line), &row) == nil {
				logs = append(logs, fmt.Sprintf("[%s] CLICKHOUSE | id=%s | channel=%s | text=%s", row["ca"], row["id"], row["channel"], row["text"]))
			}
		}
		writeJSON(w, 200, map[string]any{"ok": true, "logs": logs})
	})

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if b, err := os.ReadFile("index.html"); err == nil {
			w.Header().Set("Content-Type", "text/html")
			_, _ = w.Write(b)
			return
		}
		_, _ = w.Write([]byte("<h1>Dashboard no encontrado</h1>"))
	})

	log.Printf("Receiver Case 13 escuchando en :%s (motor: Kafka + ClickHouse)", httpPort)
	log.Fatal(http.ListenAndServe(":"+httpPort, nil))
}
