<?php

namespace App\Console\Commands;

/**
 * Clase SendSocialPost (Simulación Artisan)
 * 
 * Contexto:
 *   En un entorno Laravel real, esta clase extendería de `Illuminate\Console\Command`.
 *   Aquí se simula un comando de consola que podría ejecutarse vía crontab (ej: `php artisan post:send`).
 * 
 * Responsabilidad:
 *   Actuar como el "Worker" que chequea la base de datos (JSON) y despacha trabajos
 *   al microservicio de frontend (React/Node).
 */
class SendSocialPost
{
    // Firma del comando (como se invocaría en CLI real)
    protected $signature = 'post:send';
    protected $description = 'Envía posts pendientes a n8n';

    /**
     * Lógica de Ejecución Principal.
     */
    public function handle()
    {
        // 1. Configuración
        $webhookUrl = getenv('WEBHOOK_URL');
        $postsFile = 'posts.json';

        if (!file_exists($postsFile)) {
            echo "Error: posts.json no encontrado.\n";
            return;
        }

        // 2. Carga de Estado
        // Uso de punteros (&$post) para modificar el array original directamente en el loop.
        $posts = json_decode(file_get_contents($postsFile), true);
        $changed = false;
        $now = new \DateTime();

        // 3. Procesamiento
        foreach ($posts as &$post) {
            $scheduledAt = new \DateTime($post['scheduled_at']);

            // Regla de Negocio
            if (!$post['published'] && $scheduledAt <= $now) {
                echo "Enviando post {$post['id']} (Laravel Artisan)...\n";

                // 4. Despacho
                if ($this->sendToWebhook($webhookUrl, $post)) {
                    $post['published'] = true;
                    $changed = true;
                }
            }
        }

        // 5. Persistencia
        if ($changed) {
            file_put_contents($postsFile, json_encode($posts, JSON_PRETTY_PRINT));
        }
    }

    /**
     * Cliente HTTP Rudimentario.
     * 
     * Nota Técnica:
     *   En Laravel real usaríamos la Facade `Http` (Guzzle wrapper).
     *   Aquí usamos streams nativos de PHP para minimizar dependencias en este entorno de simulación.
     */
    private function sendToWebhook($url, $post)
    {
        // Dry-Run
        if (!$url) {
            echo "[DRY-RUN] Post {$post['id']} enviado.\n";
            return true;
        }

        // Configuración de Contexto de Stream para POST JSON
        $options = [
            'http' => [
                'header' => "Content-type: application/json\r\n",
                'method' => 'POST',
                'content' => json_encode($post),
                'timeout' => 5, // Importante para evitar bloqueos largos
            ],
        ];
        $context = stream_context_create($options);

        // Ejecución de la petición
        // EL operador @ silencia warnings, pero validamos con !== false.
        $result = @file_get_contents($url, false, $context);

        if ($result === false) {
            $error = error_get_last();
            echo "Error en webhook: " . ($error['message'] ?? 'Unknown') . "\n";
            return false;
        }

        return true;
    }
}

// =================================================================================================
// BOOTSTRAPPER 
// =================================================================================================
// Simulación de ejecución Artisan
$command = new SendSocialPost();
$command->handle();
