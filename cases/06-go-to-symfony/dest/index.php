<?php

namespace App\Controller;

class SocialBotController
{
    private $logFile = __DIR__ . '/../../var/log/social_bot_symfony.log';

    public function receive(Request $request): Response
    {
        $data = json_decode($request->getContent(), true);
        if (!$data || !isset($data['id'])) {
            return new JsonResponse(['ok' => false], 400);
        }

        $logLine = "[" . date('Y-m-d H:i:s') . "] SYMFONY-DEST | id={$data['id']} | text={$data['text']}\n";
        file_put_contents($this->logFile, $logLine, FILE_APPEND);

        return new JsonResponse(['ok' => true, 'message' => 'Symfony ha recibido el post']);
    }

    public function dashboard(): Response
    {
        $logs = file_exists($this->logFile) ? file($this->logFile) : [];
        return $this->render('dashboard.html.twig', [
            'logs' => array_reverse($logs),
            'framework' => 'Symfony 7'
        ]);
    }
}

// Endpoint de ERRORES (DLQ)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && strpos($_SERVER['REQUEST_URI'], '/errors') !== false) {
    $rawBody = file_get_contents('php://input');
    $errorData = json_decode($rawBody, true);

    $errorLine = sprintf(
        "[%s] CASE=%s | ERROR=%s | PAYLOAD=%s\n",
        date('Y-m-d H:i:s'),
        $errorData['case'] ?? 'unknown',
        json_encode($errorData['error'] ?? 'no error info'),
        json_encode($errorData['payload'] ?? 'no payload')
    );

    file_put_contents('errors.log', $errorLine, FILE_APPEND);

    header('Content-Type: application/json');
    echo json_encode(['ok' => true, 'message' => 'Error logged to DLQ']);
    exit;
}

// Simulación de receptor Symfony Lite
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = file_get_contents('php://input');
    $log = "[" . date('Y-m-d H:i:s') . "] SYMFONY-LITE | " . $input . "\n";
    file_put_contents('symfony.log', $log, FILE_APPEND);
    header('Content-Type: application/json');
    echo json_encode(['ok' => true]);
} else {
    $logs = file_exists('symfony.log') ? file('symfony.log') : [];
    ?>
    <!DOCTYPE html>
    <html lang="es">

    <head>
        <meta charset="UTF-8">
        <title>Symfony Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Outfit', sans-serif;
                background: #1a1a1a;
                color: #fff;
                padding: 40px;
            }

            .badge {
                background: #000;
                color: #fff;
                padding: 5px 10px;
                border: 1px solid #555;
            }

            .log-box {
                background: #222;
                border: 1px solid #333;
                padding: 15px;
                margin-top: 20px;
            }
        </style>
    </head>

    <body>
        <h1>🐘 Symfony <span class="badge">Enterprise Dashboard</span></h1>
        <p>Logs recibidos desde n8n:</p>
        <div class="log-box">
            <?php foreach (array_reverse($logs) as $l): ?>
                <p style="border-bottom: 1px solid #333; padding: 5px;">
                    <?php echo htmlspecialchars($l); ?>
                </p>
            <?php endforeach; ?>
        </div>
        <script>setTimeout(() => location.reload(), 5000);</script>
    </body>

    </html>
    <?php
}
