// ================================================================================================
// SERVIDOR gRPC EN GO (Case 15: Go gRPC -> n8n -> Python gRPC client -> CockroachDB)
// ================================================================================================
// El servidor Go expone el servicio SocialService (definido en social.proto) sobre gRPC. El cliente
// Python (dest) lo invoca para persistir y consultar posts. La persistencia es CockroachDB — SQL
// distribuido con consenso Raft, wire-compatible con PostgreSQL (driver lib/pq).
package main

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"net"
	"os"
	"time"

	_ "github.com/lib/pq"
	"google.golang.org/grpc"
)

type server struct {
	UnimplementedSocialServiceServer
	db *sql.DB
}

func (s *server) Publish(ctx context.Context, p *Post) (*Ack, error) {
	_, err := s.db.ExecContext(ctx,
		`INSERT INTO social_posts (id, text, channel, scheduled_at) VALUES ($1, $2, $3, $4)
		 ON CONFLICT (id) DO UPDATE SET text = excluded.text`,
		p.Id, p.Text, p.Channel, p.ScheduledAt)
	if err != nil {
		return &Ack{Ok: false, Message: err.Error()}, nil
	}
	log.Printf("Post persistido en CockroachDB: %s", p.Id)
	return &Ack{Ok: true, Message: "Post persistido en CockroachDB (gRPC)"}, nil
}

func (s *server) ListRecent(ctx context.Context, _ *Empty) (*Logs, error) {
	rows, err := s.db.QueryContext(ctx,
		`SELECT id, channel, text, created_at FROM social_posts ORDER BY created_at DESC LIMIT 20`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	out := &Logs{}
	for rows.Next() {
		var id, channel, text string
		var createdAt time.Time
		if err := rows.Scan(&id, &channel, &text, &createdAt); err != nil {
			return nil, err
		}
		out.Logs = append(out.Logs, &LogLine{
			Line: fmt.Sprintf("[%s] COCKROACH | id=%s | channel=%s | text=%s",
				createdAt.Format(time.RFC3339), id, channel, text),
		})
	}
	return out, nil
}

func getenv(k, d string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return d
}

func mustDB() *sql.DB {
	host := getenv("DB_HOST", "cockroach-15")
	port := getenv("DB_PORT", "26257")
	dsn := func(db string) string {
		return fmt.Sprintf("postgresql://root@%s:%s/%s?sslmode=disable", host, port, db)
	}

	// 1) Conecta a defaultdb y crea la base 'social'.
	for i := 0; i < 30; i++ {
		root, err := sql.Open("postgres", dsn("defaultdb"))
		if err == nil {
			if err = root.Ping(); err == nil {
				_, _ = root.Exec(`CREATE DATABASE IF NOT EXISTS social`)
				_ = root.Close()
				break
			}
		}
		log.Printf("[bootstrap] CockroachDB no listo (intento %d): %v", i+1, err)
		time.Sleep(2 * time.Second)
	}

	// 2) Conecta a 'social' y crea la tabla.
	db, err := sql.Open("postgres", dsn("social"))
	if err != nil {
		log.Fatal(err)
	}
	for i := 0; i < 30; i++ {
		if err = db.Ping(); err == nil {
			break
		}
		time.Sleep(2 * time.Second)
	}
	if _, err := db.Exec(`CREATE TABLE IF NOT EXISTS social_posts (
		id TEXT PRIMARY KEY,
		text TEXT NOT NULL,
		channel TEXT NOT NULL DEFAULT 'default',
		scheduled_at TEXT,
		created_at TIMESTAMPTZ NOT NULL DEFAULT now())`); err != nil {
		log.Fatal(err)
	}
	log.Println("[bootstrap] Tabla social_posts lista en CockroachDB.")
	return db
}

func main() {
	db := mustDB()

	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatal(err)
	}
	s := grpc.NewServer()
	RegisterSocialServiceServer(s, &server{db: db})
	log.Println("Servidor gRPC Case 15 escuchando en :50051")
	if err := s.Serve(lis); err != nil {
		log.Fatal(err)
	}
}
