package main

/**
 * RECEPTOR DE ALTO RENDIMIENTO (Go + MariaDB)
 * -----------------------------------------
 * ¿Por qué Go para el receptor?
 * Go brilla en la concurrencia nativa (Goroutines) y eficiencia de red. Mientras que lenguajes
 * interpretados sufren con miles de peticiones simultáneas, este binario compilado ofrece 
 * tiempos de respuesta en microsegundos, ideal para actuar como sumidero de múltiples bots.
 * 
 * Estrategia de Persistencia:
 * - Driver: go-sql-driver/mysql (MariaDB compatible).
 * - Sincronización: Uso de sync.Mutex para garantizar integridad en los logs compartidos.
 * - Resiliencia: Implementación de Pings y reintentos para soportar latencia en el arranque del contenedor MariaDB.
 */

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"sync"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

// =================================================================================================
// MODELOS DE DOMINIO
// =================================================================================================

// Post representa la estructura del objeto JSON enviado por el cliente Python.
// Se usan etiquetas `json:"..."` para el mapeo automático (Unmarshalling).
type Post struct {
	ID          string `json:"id"`
	Text        string `json:"text"`
	Channel     string `json:"channel"`
	ScheduledAt string `json:"scheduled_at"`
}

// =================================================================================================
// ESTADO GLOBAL (CONCURRENCY SAFE)
// =================================================================================================
// Go maneja cada petición HTTP en una goroutine separada.
// Para escribir en un archivo compartido sin condiciones de carrera (Race Conditions),
// necesitamos sincronizar el acceso usando un Mutex.

var (
	logMutex sync.Mutex // Semáforo para exclusión mutua en escritura de logs
	logFile  *os.File   // Descriptor de archivo abierto
	db       *sql.DB    // Conexión a MariaDB
)

// =================================================================================================
// MAIN - ENTRY POINT
// =================================================================================================

func main() {
	var err error
	
	// Abrir archivo de logs en modo Append
	// 0644 = Permisos de lectura/escritura para el dueño, lectura para otros.
	logFile, err = os.OpenFile("social_bot_go.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal(err) // Fatal termina el programa inmediatamente
	}
	// Asegurar que el archivo se cierre correctamente al terminar main (aunque sea un servidor persistente)
	defer logFile.Close()

	// --- DATABASE SETUP (MariaDB) ----------------------------------------------------------------
	dbHost := os.Getenv("DB_HOST")
	dbName := os.Getenv("DB_NAME")
	dbUser := os.Getenv("DB_USER")
	dbPass := os.Getenv("DB_PASS")

	dsn := fmt.Sprintf("%s:%s@tcp(%s:3306)/?charset=utf8mb4&parseTime=True&loc=Local", dbUser, dbPass, dbHost)
	
	// Reintento de conexión (esperar a que MariaDB esté lista)
	for i := 0; i < 10; i++ {
		db, err = sql.Open("mysql", dsn)
		if err == nil {
			err = db.Ping()
		}
		if err == nil {
			break
		}
		log.Printf("Esperando a MariaDB... %v", err)
		time.Sleep(2 * time.Second)
	}
	
	if err != nil {
		log.Printf("Error conectando a MariaDB: %v. Continuando solo con logs.", err)
	} else {
		defer db.Close()
		_, _ = db.Exec(fmt.Sprintf("CREATE DATABASE IF NOT EXISTS %s", dbName))
		_, _ = db.Exec(fmt.Sprintf("USE %s", dbName))
		_, err = db.Exec(`CREATE TABLE IF NOT EXISTS social_posts (
			id VARCHAR(50) PRIMARY KEY,
			text TEXT NOT NULL,
			channel VARCHAR(50) NOT NULL,
			scheduled_at DATETIME,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`)
		if err != nil {
			log.Printf("Error creando tabla: %v", err)
		}
	}

	// --- ROUTING HTTP ----------------------------------------------------------------------------
	
	// 1. Dashboard UI
	// Sirve el archivo estático index.html en la raíz.
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		http.ServeFile(w, r, "index.html")
	})

	// 2. API de Logs
	// Permite al frontend obtener el contenido actual del log de forma segura (Thread-Safe).
	http.HandleFunc("/logs", func(w http.ResponseWriter, r *http.Request) {
		// Bloqueamos el mutex antes de leer para asegurar consistencia si otro hilo está escribiendo
		logMutex.Lock()
		defer logMutex.Unlock()
		
		content, err := os.ReadFile("social_bot_go.log")
		if err != nil {
			http.Error(w, "Error leyendo logs", http.StatusInternalServerError)
			return
		}
		
		// Procesamiento manual de líneas (podría optimizarse con bufio.Scanner)
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

	// 3. Webhook Receiver
	// Endpoint principal donde el bot Python envía los posts.
	http.HandleFunc("/webhook", func(w http.ResponseWriter, r *http.Request) {
		// Validación estricta de Método
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
		// Intento 1: Decodificar JSON
		if err := json.Unmarshal(body, &post); err != nil {
			// Intento 2: Fallback a Form-Data (Multipart)
			// Esto permite probar con curl básico o formularios HTML sin JS
			post.ID = r.FormValue("id")
			post.Text = r.FormValue("text")
			post.Channel = r.FormValue("channel")
			post.ScheduledAt = r.FormValue("scheduled_at")
		}

		// Validación de Campos Obligatorios
		if post.ID == "" || post.Text == "" {
			http.Error(w, "Faltan campos obligatorios", http.StatusUnprocessableEntity)
			return
		}

		// Construcción de la línea de Log
		logLine := fmt.Sprintf("[%s] GO-RECEIVER | id=%s | channel=%s | text=%s\n",
			time.Now().Format("2006-01-02 15:04:05"),
			post.ID,
			post.Channel,
			post.Text,
		)

		// ESCRITURA SINCRONIZADA (Critical Section)
		// Go maneja cada request en un hilo diferente. Sin este Lock, múltiples hilos
		// intentando escribir en el mismo archivo provocarían corrupción de datos.
		logMutex.Lock()
		if _, err := logFile.WriteString(logLine); err != nil {
			log.Printf("Error escribiendo en log: %v", err)
		}
		logMutex.Unlock()

		// PERSISTENCIA EN DB (MariaDB)
		// Se utiliza SQL parametrizado (`?`) para evitar ataques de SQL Injection por diseño.
		// El uso de `ON DUPLICATE KEY UPDATE` dota al sistema de Idempotencia: si el bot envía
		// el mismo ID dos veces por error de red, el sistema solo actualiza el registro existente.
		if db != nil {
			query := `INSERT INTO social_posts (id, text, channel, scheduled_at) 
					  VALUES (?, ?, ?, ?) 
					  ON DUPLICATE KEY UPDATE text=?, channel=?, scheduled_at=?`
			_, err = db.Exec(query, post.ID, post.Text, post.Channel, post.ScheduledAt, post.Text, post.Channel, post.ScheduledAt)
			if err != nil {
				log.Printf("Error guardando en MariaDB: %v", err)
			}
		}

		fmt.Printf("Post recibido en Go: %s\n", post.ID)

		// Respuesta JSON
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"ok":      true,
			"message": "Post recibido por receptor Go",
			"case":    "02-python-n8n-go",
		})
	})

	// 4. Dead Letter Queue (/errors)
	// Manejo robusto de reportes de error externos.
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

		// Apertura dinámica del log de errores
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

		// Reutilizamos el mismo Mutex para evitar escrituras solapadas si decidimos unificar logs en futuro,
		// aunque estrictamente hablando errors.log es diferente a social_bot_go.log.
		// Para máxima seguridad, usamos el lock global.
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

	// Arranque del Servidor
	fmt.Println("Servidor Go escuchando en :8080...")
	// ListenAndServe bloquea indefinidamente hasta que ocurra un error fatal
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}
