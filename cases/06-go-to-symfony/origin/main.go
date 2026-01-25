package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

type Post struct {
	ID          string   `json:"id"`; Text string `json:"text"`
	Channels    []string `json:"channels"`; ScheduledAt string `json:"scheduled_at"`
	Published   bool     `json:"published"`
}

func main() {
	webhookURL := os.Getenv("WEBHOOK_URL")
	for {
		process(webhookURL); time.Sleep(30 * time.Second)
	}
}

func process(url string) {
	file, _ := os.ReadFile("posts.json")
	var posts []Post; json.Unmarshal(file, &posts)
	changed := false; now := time.Now()

	for i := range posts {
		scheduled, _ := time.Parse("2006-01-02T15:04:05", posts[i].ScheduledAt)
		if !posts[i].Published && (scheduled.Before(now) || scheduled.Equal(now)) {
			if send(url, posts[i]) { posts[i].Published = true; changed = true }
		}
	}
	if changed { d, _ := json.MarshalIndent(posts, "", "  "); os.WriteFile("posts.json", d, 0644) }
}

func send(url string, post Post) bool {
	if url == "" { fmt.Printf("[DRY-RUN] %s enviado.\n", post.ID); return true }
	b, _ := json.Marshal(post)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(b))
	if err == nil && resp.StatusCode < 300 { fmt.Printf("Post %s OK (Go to Symfony).\n", post.ID); return true }
	return false
}
