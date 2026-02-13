<?php
/**
 * Destino de Migración: Legacy PHP Receiver
 * 
 * Contexto:
 *   Este script simula una aplicación heredada ("Legacy App") que recibe los posts enviados por el bot.
 *   En un escenario real, esto podría ser un CMS antiguo (WordPress, Drupal) o un sistema monolítico
 *   al que necesitamos enviar contenido desde nuestro nuevo microservicio en Python.
 * 
 * Funcionalidad:
 *   1. Actúa como endpoint HTTP (Webhook Receiver).
 *   2. Registra las peticiones en un archivo de log local (file-based logging).
 *   3. Sirve un dashboard simple (index.html) para visualizar el estado.
 *   4. Implementa un manejo básico de errores (Dead Letter Queue simulada).
 */

// =================================================================================================
// CONFIGURACIÓN DE LOGS E INFRAESTRUCTURA
// =================================================================================================
$logDir = __DIR__ . '/logs';
$logFile = $logDir . '/social_bot.log';     // Log de éxito (Happy Path)
$errorLogFile = $logDir . '/errors.log';    // Log de errores (DLQ)

// Garantizar que la carpeta de logs exista con permisos de escritura adecuados (0775)
if (!is_dir($logDir)) {
    mkdir($logDir, 0775, true);
}

// =================================================================================================
// ENDPOINT DE ERRORES (DEAD LETTER QUEUE)
// =================================================================================================
// Captura reportes de fallo enviados por el bot o sistemas externos.
if ($_SERVER['REQUEST_METHOD'] === 'POST' && strpos($_SERVER['REQUEST_URI'], '/errors') !== false) {
    $rawBody = file_get_contents('php://input');
    $errorData = json_decode($rawBody, true);
    
    // Formato estructurado para facilitar el parsing posterior (ej: con grep o ELK)
    $errorLine = sprintf(
        "[%s] CASE=%s | ERROR=%s | PAYLOAD=%s\n",
        date('Y-m-d H:i:s'),
        isset($errorData['case']) ? $errorData['case'] : 'unknown',
        isset($errorData['error']) ? json_encode($errorData['error']) : 'no error info',
        isset($errorData['payload']) ? json_encode($errorData['payload']) : 'no payload'
    );
    
    file_put_contents($errorLogFile, $errorLine, FILE_APPEND);
    
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(array('ok' => true, 'message' => 'Error logged to DLQ'));
    exit;
}

// =================================================================================================
// API DE LECTURA (POLLING)
// =================================================================================================
// Utilizado por el dashboard (index.html) para refrescar la vista de logs en tiempo real.
if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['action']) && $_GET['action'] === 'get_logs') {
    $logs = array();
    if (file_exists($logFile)) {
        // Lee el archivo en un array, ignorando líneas vacías para limpiar la salida
        $logs = file($logFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    }
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(array('ok' => true, 'logs' => $logs));
    exit;
}

// =================================================================================================
// VALIDACIÓN DE MÉTODO Y RUTEO
// =================================================================================================
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    // Si la petición es GET simple (sin action), servimos la interfaz gráfica (Dashboard)
    if ($_SERVER['REQUEST_METHOD'] === 'GET' && !isset($_GET['action'])) {
        if (file_exists(__DIR__ . '/index.html')) {
            header('Content-Type: text/html; charset=utf-8');
            readfile(__DIR__ . '/index.html');
            exit;
        }
    }

    // Para cualquier otro método no soportado (PUT, DELETE, PATCH), devolvemos 405
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(405); // Method Not Allowed
    echo json_encode(array(
        'ok' => false,
        'error' => 'Método no permitido. Usa POST para enviar datos o GET ?action=get_logs.',
    ));
    exit;
}

// A partir de aquí, solo procesamos POSTs
header('Content-Type: application/json; charset=utf-8');

// =================================================================================================
// PROCESAMIENTO DEL PAYLOAD
// =================================================================================================

// 1. Obtener datos crudos
$rawBody = file_get_contents('php://input');
$data = null;

// 2. Intentar decodificar JSON (Estándar moderno)
if ($rawBody !== '') {
    $tmp = json_decode($rawBody, true);
    if (json_last_error() === JSON_ERROR_NONE && is_array($tmp)) {
        $data = $tmp;
    }
}

// 3. Fallback: Soportar Form-Data (Legacy POST)
// Esto es útil si el cliente es un formulario HTML clásico en lugar de una API REST moderna.
if ($data === null && !empty($_POST)) {
    $data = $_POST;
}

// 4. Validación de Integridad
if ($data === null) {
    http_response_code(400); // Bad Request
    echo json_encode(array(
        'ok' => false,
        'error' => 'No se recibió un cuerpo válido (JSON o POST).',
    ));
    exit;
}

// =================================================================================================
// LÓGICA DE NEGOCIO Y PERSISTENCIA
// =================================================================================================

// Sanitización básica y extracción
$id = isset($data['id']) ? trim($data['id']) : '';
$text = isset($data['text']) ? trim($data['text']) : '';
$channel = isset($data['channel']) ? trim($data['channel']) : '';
$scheduledAt = isset($data['scheduled_at']) ? trim($data['scheduled_at']) : '';

// Comprobación de campos obligatorios
if ($id === '' || $text === '' || $channel === '') {
    http_response_code(422); // Unprocessable Entity (Semánticamente correcto para errores de validación)
    echo json_encode(array(
        'ok' => false,
        'error' => 'Faltan campos obligatorios: id, text, channel.',
        'data' => $data,
    ));
    exit;
}

// Registrar la operación exitosa
// Formato: [TIMESTAMP] metadatos | contenido
$logLine = sprintf(
    "[%s] id=%s | channel=%s | scheduled_at=%s | text=%s\n",
    date('Y-m-d H:i:s'),
    $id,
    $channel,
    $scheduledAt,
    // Limpiamos saltos de línea para mantener el log en una sola línea por entrada
    str_replace(array("\r", "\n"), ' ', $text)
);

// Escritura atómica (append)
file_put_contents($logFile, $logLine, FILE_APPEND);

// (Punto de Extensión): Aquí se conectaría con la base de datos real (MySQL/PostgreSQL)
// $db->query("INSERT INTO posts ...");

// Responder éxito al cliente
echo json_encode(array(
    'ok' => true,
    'message' => 'Post recibido y logueado correctamente.',
    'data' => array(
        'id' => $id,
        'channel' => $channel,
        'logged' => basename($logFile),
    ),
));
