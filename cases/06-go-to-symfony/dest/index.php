<?php
/**
 * ==================================================================================================
 * RECEPTOR EMPRESARIAL SYMFONY LITE (Case 06: Go -> n8n -> Symfony + Redis)
 * ==================================================================================================
 * ¿Por qué Symfony para el receptor?
 * Symfony es el framework PHP de referencia en entornos empresariales europeos. Su arquitectura 
 * basada en componentes (HttpFoundation, Routing, DependencyInjection) lo hace ideal para 
 * aplicaciones de misión crítica que necesitan mantenimiento a largo plazo.
 * 
 * Diseño Dual (OOP + Procedural):
 * Este archivo contiene DOS implementaciones del mismo receptor:
 * 1. Clase `SocialBotController`: Versión OOP que imita un controlador Symfony real.
 * 2. Script Procedural: Front-Controller ligero que maneja rutas sin el Kernel de Symfony.
 * 
 * Persistencia en Redis:
 * Redis actúa como almacén de clave-valor con TTL (Time-To-Live). Cada post se guarda como 
 * `post:{id}` con una expiración de 24h. Esto es ideal para datos efímeros como feeds de RRSS,
 * donde no necesitamos retención permanente como en MySQL o PostgreSQL.
 *
 * ¿Por qué Redis y no SQL?
 * Redis alcanza latencias de ~1ms por operación, 100x más rápido que un INSERT en MySQL.
 * Para un receptor que necesita responder instantáneamente al bus de eventos, esta velocidad es crítica.
 */

namespace App\Controller;

/**
 * Clase SocialBotController (Ilustrativa)
 * 
 * Contexto:
 *   Esta clase representa cómo se vería el controlador en una aplicación Symfony Full-Stack real.
 *   En este entorno "Lite" de demostración, no estamos arrancando el Kernel de Symfony completo,
 *   sino simulando su comportamiento mediante el script procedural más abajo.
 * 
 * Equivalencia:
 *   En Symfony real: `Route("/webhook", methods={"POST"})`
 */
class SocialBotController
{
    private $logFile = __DIR__ . '/symfony.log';
    private $errorLogFile = __DIR__ . '/errors.log';

    // =================================================================================================
    // CONFIGURACIÓN DE REDIS (Case 06)
    // =================================================================================================
    private $redisHost;

    public function __construct()
    {
        $this->redisHost = getenv('DB_HOST') ?: 'db-redis';
    }

    private function saveToRedis($id, $data)
    {
        try {
            // Asumimos que phpredis está disponible en la imagen php:8.2-apache
            $redis = new \Redis(); // Use \Redis for global namespace
            if (@$redis->connect($this->redisHost, 6379, 1.0)) {
                $redis->set("post:$id", json_encode($data));
                $redis->expire("post:$id", 3600 * 24); // 24h retention
                return true;
            }
        } catch (\Exception $e) { // Use \Exception for global namespace
            error_log("Redis Error: " . $e->getMessage());
        }
        return false;
    }

    public function receive(Request $request): Response
    {
        $data = json_decode($request->getContent(), true);

        // Validación Symfony Style
        if (!$data || !isset($data['id'])) {
            return new JsonResponse(['ok' => false], 400);
        }

        $logLine = "[" . date('Y-m-d H:i:s') . "] SYMFONY-DEST | id={$data['id']} | text={$data['text']}\n";
        // Escritura atómica
        file_put_contents($this->logFile, $logLine, FILE_APPEND);

        // Persistencia en Redis
        $this->saveToRedis($data['id'], $data);

        return new JsonResponse(['ok' => true, 'message' => 'Symfony ha recibido el post']);
    }

    public function dashboard(): Response
    {
        // Motor de Plantillas Twig (Simulado)
        $logs = file_exists($this->logFile) ? file($this->logFile) : [];
        return $this->render('dashboard.html.twig', [
            'logs' => array_reverse($logs),
            'framework' => 'Symfony 7'
        ]);
    }
}

// =================================================================================================
// SIMULACIÓN DE MIDDLEWARE Y ENRUTAMIENTO
// =================================================================================================
// Dado que no tenemos servidor web (Nginx/Apache) ni Kernel de Symfony en este contenedor ligero,
// manejamos las rutas manualmente usando $_SERVER.

// 1. Endpoint Dead Letter Queue (DLQ)
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

// 2. Front Controller Simplificado
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Simula la acción `receive()` del controlador
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    $log = "[" . date('Y-m-d H:i:s') . "] SYMFONY-LITE | " . $input . "\n";
    file_put_contents('symfony.log', $log, FILE_APPEND);

    // Persistencia en Redis (Procedural fallback)
    $redisHost = getenv('DB_HOST') ?: 'db-redis';
    try {
        $redis = new \Redis();
        if (@$redis->connect($redisHost, 6379, 1.0)) {
            $redis->set("post:" . ($data['id'] ?? 'unknown'), $input);
        }
    } catch (\Exception $e) {
    }

    header('Content-Type: application/json');
    echo json_encode(['ok' => true]);
} else {
    // Simula la acción `dashboard()`
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
