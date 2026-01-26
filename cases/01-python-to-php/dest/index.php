<?php
/**
 * social_bot_receiver.php
 * 
 * Receptor de publicaciones desde n8n (social-bot-scheduler).
 * Compatible con PHP 5.4 a 8.x.
 */

// --- CONFIG LOG ----------------------------------------------------------
$logDir = __DIR__ . '/logs';
$logFile = $logDir . '/social_bot.log';

if (!is_dir($logDir)) {
    // Crear carpeta logs si no existe
    mkdir($logDir, 0775, true);
}

// --- HANDLE ACTIONS ------------------------------------------------------
if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['action']) && $_GET['action'] === 'get_logs') {
    $logs = array();
    if (file_exists($logFile)) {
        $logs = file($logFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    }
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(array('ok' => true, 'logs' => $logs));
    exit;
}

// --- VALIDAR MÉTODO ------------------------------------------------------
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    // Si es GET y no es la acción get_logs, intentamos servir el dashboard
    if ($_SERVER['REQUEST_METHOD'] === 'GET' && !isset($_GET['action'])) {
        if (file_exists(__DIR__ . '/index.html')) {
            header('Content-Type: text/html; charset=utf-8');
            readfile(__DIR__ . '/index.html');
            exit;
        }
    }

    // Si no fue GET para el dashboard, devolvemos 405 para otros métodos o GETs inválidos
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(405); // Method Not Allowed
    echo json_encode(array(
        'ok' => false,
        'error' => 'Método no permitido. Usa POST para enviar datos o GET ?action=get_logs.',
    ));
    exit;
}

// Siempre respondemos JSON para POST
header('Content-Type: application/json; charset=utf-8');

// --- LEER CUERPO (JSON o POST clásico) -----------------------------------
$rawBody = file_get_contents('php://input');
$data = null;

// Intentar JSON
if ($rawBody !== '') {
    $tmp = json_decode($rawBody, true);
    if (json_last_error() === JSON_ERROR_NONE && is_array($tmp)) {
        $data = $tmp;
    }
}

// Si no era JSON pero hay $_POST, usamos $_POST
if ($data === null && !empty($_POST)) {
    $data = $_POST;
}

// Si sigue sin datos válidos:
if ($data === null) {
    http_response_code(400); // Bad Request
    echo json_encode(array(
        'ok' => false,
        'error' => 'No se recibió un cuerpo válido (JSON o POST).',
    ));
    exit;
}

// --- EXTRAER CAMPOS ------------------------------------------------------
$id = isset($data['id']) ? trim($data['id']) : '';
$text = isset($data['text']) ? trim($data['text']) : '';
$channel = isset($data['channel']) ? trim($data['channel']) : '';
$scheduledAt = isset($data['scheduled_at']) ? trim($data['scheduled_at']) : '';

// Validar mínimos obligatorios
if ($id === '' || $text === '' || $channel === '') {
    http_response_code(422); // Unprocessable Entity
    echo json_encode(array(
        'ok' => false,
        'error' => 'Faltan campos obligatorios: id, text, channel.',
        'data' => $data,
    ));
    exit;
}

// --- GUARDAR EN LOG ------------------------------------------------------
$logLine = sprintf(
    "[%s] id=%s | channel=%s | scheduled_at=%s | text=%s\n",
    date('Y-m-d H:i:s'),
    $id,
    $channel,
    $scheduledAt,
    str_replace(array("\r", "\n"), ' ', $text)
);

file_put_contents($logFile, $logLine, FILE_APPEND);

// (Opcional futuro: aquí podrías insertar en MySQL, enviar correo, etc.)

// --- RESPUESTA OK --------------------------------------------------------
echo json_encode(array(
    'ok' => true,
    'message' => 'Post recibido y logueado correctamente.',
    'data' => array(
        'id' => $id,
        'channel' => $channel,
        'logged' => basename($logFile),
    ),
));
