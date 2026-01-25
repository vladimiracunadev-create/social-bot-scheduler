package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

type Post struct {
	ID          string   `json:"id"`
	Text        string   `json:"text"`
	Channels    []string `json:"channels"`
	ScheduledAt string   `json:"scheduled_at"`
	Published   bool     `json:"published"`
}

func main() {
	webhookURL := os.Getenv("WEBHOOK_URL")
	if webhookURL == "" {
		fmt.Println("WARN: WEBHOOK_URL no definida. Modo Dry-Run.")
	}

	for {
		processPosts(webhookURL)
		time.Sleep(30 * time.Second)
	}
}

func processPosts(url string) {
	file, err := os.ReadFile("posts.json")
	if err != nil {
		fmt.Printf("Error leyendo posts.json: %v\n", err)
		return
	}

	var posts []Post
	json.Unmarshal(file, &posts)

	changed := false
	now := time.Now()

	for i := range posts {
		scheduled, _ := time.Parse("2006-01-02T15:04:05", posts[i].ScheduledAt)
		if !posts[i].Published && (scheduled.Before(now) || scheduled.Equal(now)) {
			fmt.Printf("Enviando post %s...\n", posts[i].ID)
			if sendPost(url, posts[i]) {
				posts[i].Published = true
				changed = true
			}
		}
	}

	if changed {
		data, _ := json.MarshalIndent(posts, "", "  ")
		os.WriteFile("posts.json", data, 0644)
	}
}

func sendPost(url string, post Post) bool {
	if url == "" {
		fmt.Printf("[DRY-RUN] Post %s enviado.\n", post.ID)
		return true
	}

	body, _ := json.Marshal(post)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(body))
	if err != nil {
		fmt.Printf("Error enviando post: %v\n", err)
		return false
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		fmt.Printf("Post %s enviado con éxito.\n", post.ID)
		return true
	}
	
	b, _ := io.ReadAll(resp.Body)
	fmt.Printf("Error del servidor: %s\n", string(b))
	return false
}
