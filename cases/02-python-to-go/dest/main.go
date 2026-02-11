package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"sync"
	"time"
)

type Post struct {
	ID          string `json:"id"`
	Text        string `json:"text"`
	Channel     string `json:"channel"`
	ScheduledAt string `json:"scheduled_at"`
}

var (
	logMutex sync.Mutex
	logFile  *os.File
)

func main() {
	var err error
	logFile, err = os.OpenFile("social_bot_go.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer logFile.Close()

	// Servir DASHBOARD (index.html)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		http.ServeFile(w, r, "index.html")
	})

	// Endpoint de LOGS para el dashboard
	http.HandleFunc("/logs", func(w http.ResponseWriter, r *http.Request) {
		logMutex.Lock()
		defer logMutex.Unlock()
		
		content, err := os.ReadFile("social_bot_go.log")
		if err != nil {
			http.Error(w, "Error leyendo logs", http.StatusInternalServerError)
			return
		}
		
		// Convertir líneas a array
		lines := []string{}
		currLine := ""
		for _, b := range content {
			if b == '\n' {
				lines = append(lines, currLine)
				currLine = ""
			} else {
				currLine += string(b)
			}
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"ok": true,
			"logs": lines,
		})
	})

	http.HandleFunc("/webhook", func(w http.ResponseWriter, r *http.Request) {
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

		logMutex.Lock()
		if _, err := logFile.WriteString(logLine); err != nil {
			log.Printf("Error escribiendo en log: %v", err)
		}
		logMutex.Unlock()

		fmt.Printf("Post recibido en Go: %s\n", post.ID)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"ok":      true,
			"message": "Post recibido por receptor Go",
			"case":    "02-python-n8n-go",
		})
	})

	// Endpoint de ERRORES (DLQ)
	http.HandleFunc("/errors", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Método no permitido", http.StatusMethodNotAllowed)
			return
		}

		body, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "Error leyendo cuerpo", http.StatusBadRequest)
			return
		}

		var errorData map[string]interface{}
		if err := json.Unmarshal(body, &errorData); err != nil {
			http.Error(w, "Error parseando JSON", http.StatusBadRequest)
			return
		}

		errorLogFile, err := os.OpenFile("errors.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			http.Error(w, "Error abriendo archivo de errores", http.StatusInternalServerError)
			return
		}
		defer errorLogFile.Close()

		errorLine := fmt.Sprintf("[%s] CASE=%v | ERROR=%v | PAYLOAD=%v\n",
			time.Now().Format("2006-01-02 15:04:05"),
			errorData["case"],
			errorData["error"],
			errorData["payload"],
		)

		logMutex.Lock()
		if _, err := errorLogFile.WriteString(errorLine); err != nil {
			log.Printf("Error escribiendo en errors.log: %v", err)
		}
		logMutex.Unlock()

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"ok":      true,
			"message": "Error logged to DLQ",
		})
	})

	fmt.Println("Servidor Go escuchando en :8080...")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}
