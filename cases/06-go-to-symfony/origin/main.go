package main

/**
 * EMISOR COMPACTO (Case 06: Go -> n8n -> Symfony + Redis)
 * -------------------------------------------------------
 * ¿Por qué Go para el emisor y Symfony para el destino?
 * Este caso simula un escenario empresarial donde una aplicación de alta performance (Go)
 * necesita alimentar un CMS o ERP empresarial basado en Symfony (PHP). Es el patrón 
 * inverso al Caso 05: aquí el código moderno alimenta al legado.
 * 
 * Estilo de Código:
 * Este emisor usa un estilo Go más compacto (one-liners) para demostrar
 * la flexibilidad sintáctica del lenguaje, contrastando con el estilo más 
 * verborreico de los Casos 02 y 03.
 * 
 * Persistencia en Redis (Destino):
 * Redis actúa como cache temporal con TTL de 24h, ideal para datos efímeros
 * como publicaciones de redes sociales que no requieren persistencia a largo plazo.
 */

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

// =================================================================================================
// ESTRUCTURA DE DATOS
// =================================================================================================

// Post representa el objeto de transferencia.
// Se usa un diseño de struct compacto de una sola línea para demostración,
// aunque en producción se prefiere un campo por línea para legibilidad.
type Post struct {
	ID          string   `json:"id"`; Text string `json:"text"`
	Channels    []string `json:"channels"`; ScheduledAt string `json:"scheduled_at"`
	Published   bool     `json:"published"`
}

// =================================================================================================
// LÓGICA PRINCIPAL
// =================================================================================================

func main() {
	webhookURL := os.Getenv("WEBHOOK_URL")
	
	// Loop de Eventos Simplificado
	// Verifica tareas cada 30 segundos.
	for {
		process(webhookURL); 
		time.Sleep(30 * time.Second)
	}
}

// process encapsula la lógica de verificación de base de datos y envío.
func process(url string) {
	// Lectura de archivo (Simulación de DB)
	// Se ignora el error de lectura (_) asumiendo que el archivo existe en el entorno controlado.
	file, _ := os.ReadFile("posts.json")
	var posts []Post; json.Unmarshal(file, &posts)
	
	changed := false; now := time.Now()

	for i := range posts {
		// Parsing de fecha estricto (ISO 8601)
		scheduled, _ := time.Parse("2006-01-02T15:04:05", posts[i].ScheduledAt)
		
		// Lógica de Negocio: Publicar si fecha <= ahora y no publicado
		if !posts[i].Published && (scheduled.Before(now) || scheduled.Equal(now)) {
			// Envío y actualización atómica en memoria
			if send(url, posts[i]) { 
				posts[i].Published = true; 
				changed = true 
			}
		}
	}
	
	// Persistencia
	if changed { 
		d, _ := json.MarshalIndent(posts, "", "  "); 
		// 0644: Permisos estándar de archivo (rw-r--r--)
		os.WriteFile("posts.json", d, 0644) 
	}
}

// send realiza la petición HTTP POST al endpoint de Symfony.
func send(url string, post Post) bool {
	// Dry-Run
	if url == "" { fmt.Printf("[DRY-RUN] %s enviado.\n", post.ID); return true }
	
	b, _ := json.Marshal(post)
	// Petición HTTP síncrona
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(b))
	
	// Validación de Éxito (Status 2xx)
	if err == nil && resp.StatusCode < 300 { 
		fmt.Printf("Post %s OK (Go to Symfony).\n", post.ID); 
		return true 
	}
	return false
}
