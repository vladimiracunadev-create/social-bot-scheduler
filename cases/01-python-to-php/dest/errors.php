<?php
// Dead Letter Queue (DLQ) para el Caso 01
header('Content-Type: application/json');

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if ($data) {
    $log_entry = "[" . date('Y-m-d H:i:s') . "] ERROR: " . ($data['error'] ?? 'Unknown') . 
                 " | Case: " . ($data['case'] ?? '01') . 
                 " | Fingerprint: " . ($data['fingerprint'] ?? 'N/A') . "\n";
    
    file_put_contents('logs/dlq.log', $log_entry, FILE_APPEND);
    
    echo json_encode(["status" => "success", "message" => "Error registered in DLQ"]);
} else {
    http_response_code(400);
    echo json_encode(["status" => "error", "message" => "Invalid payload"]);
}
?>
