package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"
)

type Post struct {
	ID          string `json:"id"`
	Text        string `json:"text"`
	Channel     string `json:"channel"`
	ScheduledAt string `json:"scheduled_at"`
}

func main() {
	logFile, err := os.OpenFile("social_bot_go.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer logFile.Close()

	http.HandleFunc("/social-bot", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Método no permitido", http.StatusMethodNotAllowed)
			return
		}

		body, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "Error leyendo cuerpo", http.StatusBadRequest)
			return
		}

		var post Post
		if err := json.Unmarshal(body, &post); err != nil {
			// Intentar leer como form si no es JSON
			post.ID = r.FormValue("id")
			post.Text = r.FormValue("text")
			post.Channel = r.FormValue("channel")
			post.ScheduledAt = r.FormValue("scheduled_at")
		}

		if post.ID == "" || post.Text == "" {
			http.Error(w, "Faltan campos obligatorios", http.StatusUnprocessableEntity)
			return
		}

		logLine := fmt.Sprintf("[%s] GO-RECEIVER | id=%s | channel=%s | text=%s\n",
			time.Now().Format("2006-01-02 15:04:05"),
			post.ID,
			post.Channel,
			post.Text,
		)

		if _, err := logFile.WriteString(logLine); err != nil {
			log.Printf("Error escribiendo en log: %v", err)
		}

		fmt.Printf("Post recibido en Go: %s\n", post.ID)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"ok":      true,
			"message": "Post recibido por receptor Go",
			"case":    "02-python-n8n-go",
		})
	})

	fmt.Println("Servidor Go escuchando en :8080...")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}
