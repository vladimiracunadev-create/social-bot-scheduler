<?php

namespace App\Console\Commands;

class SendSocialPost
{
    protected $signature = 'post:send';
    protected $description = 'Envía posts pendientes a n8n';

    public function handle()
    {
        $webhookUrl = getenv('WEBHOOK_URL');
        $postsFile = 'posts.json';

        if (!file_exists($postsFile)) {
            echo "Error: posts.json no encontrado.\n";
            return;
        }

        $posts = json_decode(file_get_contents($postsFile), true);
        $changed = false;
        $now = new \DateTime();

        foreach ($posts as &$post) {
            $scheduledAt = new \DateTime($post['scheduled_at']);
            if (!$post['published'] && $scheduledAt <= $now) {
                echo "Enviando post {$post['id']} (Laravel Artisan)...\n";
                if ($this->sendToWebhook($webhookUrl, $post)) {
                    $post['published'] = true;
                    $changed = true;
                }
            }
        }

        if ($changed) {
            file_put_contents($postsFile, json_encode($posts, JSON_PRETTY_PRINT));
        }
    }

    private function sendToWebhook($url, $post)
    {
        if (!$url) {
            echo "[DRY-RUN] Post {$post['id']} enviado.\n";
            return true;
        }

        $options = [
            'http' => [
                'header' => "Content-type: application/json\r\n",
                'method' => 'POST',
                'content' => json_encode($post),
            ],
        ];
        $context = stream_context_create($options);
        $result = file_get_contents($url, false, $context);

        return $result !== false;
    }
}

// Simulación de ejecución Artisan
$command = new SendSocialPost();
$command->handle();
