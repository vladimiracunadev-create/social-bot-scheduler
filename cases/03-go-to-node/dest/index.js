const express = require('express');
const fs = require('fs');
const path = require('path');

// =================================================================================================
// CONFIGURACIÓN DE LA APP EXPRESS
// =================================================================================================
const app = express();
const PORT = 3000;

// Persistencia de Logs Basada en Archivos
// Se utiliza path.join para garantizar compatibilidad entre sistemas operativos (Windows/Linux/Mac).
const LOG_FILE = path.join(__dirname, 'social_bot_node.log');

// Middlewares
// - json(): Parsea body JSON entrante (Content-Type: application/json)
// - urlencoded(): Parsea datos de formulario (application/x-www-form-urlencoded)
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

/**
 * Endpoint Receptor (Webhook)
 * Recibe las publicaciones enviadas por el bot en Go.
 * 
 * Método: POST
 * Ruta: /webhook
 */
app.post('/webhook', (req, res) => {
    const post = req.body;

    // Validación Básica
    // Se retorna 422 Unprocessable Entity si faltan datos críticos.
    if (!post.id || !post.text) {
        return res.status(422).json({ ok: false, error: 'Faltan campos obligatorios (id, text)' });
    }

    // Construcción de Línea de Log
    // ISO 8601 Timestamp para facilitar parsing.
    const logLine = `[${new Date().toISOString()}] NODE-RECEIVER | id=${post.id} | channel=${post.channel || 'default'} | text=${post.text}\n`;

    try {
        // Escritura Síncrona (appendFileSync)
        // En aplicaciones de alto rendimiento, se preferiría streams o logging asíncrono (winston/pino),
        // pero para este caso de uso garantiza que el dato se escriba antes de responder.
        fs.appendFileSync(LOG_FILE, logLine);
        console.log(`[INFO] Post recibido en Node: ${post.id}`);

        res.json({
            ok: true,
            message: 'Post recibido correctamente por Node/Express',
            case: '03-go-to-node'
        });
    } catch (err) {
        console.error("Error escribiendo log:", err);
        res.status(500).json({ ok: false, error: 'Error interno guardando log' });
    }
});

/**
 * Endpoint de Consulta de Logs
 * Utilizado por el Dashboard HTML para mostrar actividad reciente.
 */
app.get('/logs', (req, res) => {
    if (!fs.existsSync(LOG_FILE)) {
        return res.json({ ok: true, logs: [] });
    }
    // Leer todo el archivo en memoria (No recomendado para logs gigantes, usar streams/paginación en prod)
    const logs = fs.readFileSync(LOG_FILE, 'utf-8').split('\n').filter(Boolean);
    res.json({ ok: true, logs });
});

/**
 * Endpoint Dead Letter Queue (DLQ)
 * Recibe reportes de error externos.
 */
app.post('/errors', (req, res) => {
    const errorData = req.body;
    const ERROR_LOG_FILE = path.join(__dirname, 'errors.log');

    const errorLine = `[${new Date().toISOString()}] CASE=${errorData.case || 'unknown'} | ERROR=${JSON.stringify(errorData.error || 'no error info')} | PAYLOAD=${JSON.stringify(errorData.payload || 'no payload')}\n`;

    try {
        fs.appendFileSync(ERROR_LOG_FILE, errorLine);
        console.log(`[ERROR] Reporte guardado en DLQ: ${errorData.case}`);

        res.json({
            ok: true,
            message: 'Error logged to DLQ'
        });
    } catch (err) {
        res.status(500).json({ ok: false, error: 'Fallo al escribir en DLQ' });
    }
});

// Servir el Dashboard Estático
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Inicio del Servidor
// Escucha en 0.0.0.0 para aceptar conexiones externas (ej: desde otro contenedor Docker)
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Servidor Node.js activo y escuchando en puerto ${PORT}`);
});
