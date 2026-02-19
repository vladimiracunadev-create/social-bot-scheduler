package main

/**
 * EMISOR DE ALTA CONFIABILIDAD (Go)
 * --------------------------------
 * ¿Por qué Go para el emisor?
 * En este caso (03-go-to-node), Go actúa como un daemon ligero. Su capacidad de compilar 
 * a un binario estático sin dependencias externas (como un runtime de Python o Node) 
 * lo hace ideal para entornos de infraestructura mínima o sistemas embebidos que 
 * necesitan reportar datos a una API central.
 * 
 * Patrones aplicados:
 * - 12-Factor App: Configuración externa vía variables de entorno.
 * - Daemon Loop: Bucle infinito con control de intervalos para evitar CPU spikes.
 * - JSON Marshalling: Mapeo estricto del esquema de publicación.
 */

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

// =================================================================================================
// ESTRUCTURAS DE DATOS
// =================================================================================================

// Post define el esquema de datos para una publicación.
// Coincide con la estructura JSON almacenada en `posts.json`.
type Post struct {
	ID          string   `json:"id"`
	Text        string   `json:"text"`
	Channels    []string `json:"channels"`
	ScheduledAt string   `json:"scheduled_at"` // Formato ISO-8601 esperado (ej: "2023-10-27T10:00:00")
	Published   bool     `json:"published"`
}

// =================================================================================================
// LÓGICA PRINCIPAL DEL BOT
// =================================================================================================

func main() {
	// Configuración vía Variables de Entorno (12-Factor App)
	webhookURL := os.Getenv("WEBHOOK_URL")
	if webhookURL == "" {
		fmt.Println("WARN: WEBHOOK_URL no definida. Modo Dry-Run activo (no se enviarán peticiones reales).")
	}

	// Bucle Infinito (Daemon)
	// El bot corre indefinidamente, verificando nuevos posts cada 30 segundos.
	// En un entorno de producción (K8s), si este proceso muere, el orquestador lo reiniciaría.
	for {
		processPosts(webhookURL)
		
		// Espera bloqueante para evitar consumo excesivo de CPU (Busy Wait)
		time.Sleep(30 * time.Second)
	}
}

// processPosts contiene la lógica de negocio core: Cargar -> Filtrar -> Enviar -> Guardar.
func processPosts(url string) {
	// 1. Carga de Datos
	file, err := os.ReadFile("posts.json")
	if err != nil {
		fmt.Printf("Error leyendo posts.json: %v\n", err)
		return
	}

	var posts []Post
	if err := json.Unmarshal(file, &posts); err != nil {
		fmt.Printf("Error parseando posts.json: %v\n", err)
		return
	}

	changed := false
	now := time.Now()

	// 2. Iteración y Filtrado
	// Usamos índice `i` para modificar el slice original directamente. 
	// Si usáramos `for _, post := range posts`, `post` sería una copia y los cambios no persistirían.
	for i := range posts {
		// Parsing de fecha. Se asume formato estricto.
		scheduled, err := time.Parse("2006-01-02T15:04:05", posts[i].ScheduledAt)
		if err != nil {
			fmt.Printf("Error fecha invalida en post %s: %v\n", posts[i].ID, err)
			continue
		}

		// Regla de Negocio: Publicar si no está publicado Y ya pasó su hora programada
		if !posts[i].Published && (scheduled.Before(now) || scheduled.Equal(now)) {
			fmt.Printf("Enviando post %s...\n", posts[i].ID)
			
			// 3. Envío (Efecto Secundario)
			if sendPost(url, posts[i]) {
				// 4. Actualización de Estado (Memoria)
				posts[i].Published = true
				changed = true
			}
		}
	}

	// 5. Persistencia
	// Solo escribimos en disco si hubo cambios para minimizar I/O.
	if changed {
		data, _ := json.MarshalIndent(posts, "", "  ")
		// 0644: Lectura/Escritura usuario, Lectura grupo/otros
		os.WriteFile("posts.json", data, 0644)
		fmt.Println("Base de datos actualizada.")
	}
}

// sendPost abstrae la comunicación HTTP con el servicio externo.
func sendPost(url string, post Post) bool {
	// Modo Simulación (Dry Run)
	if url == "" {
		fmt.Printf("[DRY-RUN] Post %s enviado simuladamente.\n", post.ID)
		return true
	}

	body, _ := json.Marshal(post)
	// Timeout por defecto del cliente HTTP es infinito, cuidado en producción.
	// Aquí usamos el cliente Default, pero sería mejor usar uno con Timeout configurado.
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(body))
	if err != nil {
		fmt.Printf("Error enviando post: %v\n", err)
		return false
	}
	defer resp.Body.Close()

	// Verificación de éxito (Códigos 2xx)
	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		fmt.Printf("Post %s enviado con éxito (Status: %d).\n", post.ID, resp.StatusCode)
		return true
	}
	
	// Lectura del cuerpo de error para depuración
	b, _ := io.ReadAll(resp.Body)
	fmt.Printf("Error del servidor (Status: %d): %s\n", resp.StatusCode, string(b))
	return false
}
