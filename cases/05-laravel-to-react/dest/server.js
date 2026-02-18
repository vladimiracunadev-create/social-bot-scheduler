const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { MongoClient } = require('mongodb');

const app = express();
const PORT = 4000;
const LOG_FILE = 'posts_react.log';

// =================================================================================================
// CONFIGURACIÓN DE BASE DE DATOS (MongoDB)
// =================================================================================================
const dbHost = process.env.DB_HOST || 'db-mongodb';
const dbName = process.env.DB_NAME || 'social_bot';
const mongoUrl = `mongodb://${dbHost}:27017`;
const client = new MongoClient(mongoUrl);

let db;
async function initDB() {
    try {
        await client.connect();
        db = client.db(dbName);
        console.log("[INFO] MongoDB connected.");
    } catch (err) {
        console.error("[ERROR] MongoDB connection failed:", err.message);
    }
}
initDB();

// =================================================================================================
// MIDDLEWARES
// =================================================================================================
// CORS: Habilitar peticiones Cross-Origin si el frontend corre en puerto distinto (ej: 3000 vs 4000).
app.use(cors());
app.use(express.json());

// Servir frontend React
// En producción, esto apuntaría a `build` o `dist`.
app.use(express.static(path.join(__dirname, 'public')));

// =================================================================================================
// ENDPOINTS
// =================================================================================================

/**
 * Endpoint Webhook
 * Recibe los datos enviados por el script PHP (Laravel).
 */
app.post('/webhook', (req, res) => {
    const post = req.body;
    // Log formato texto plano para simplificar lectura desde FS
    const logLine = `[${new Date().toISOString()}] REACT-DASHBOARD | id=${post.id} | channel=${post.channel} | text=${post.text}\n`;

    try {
        fs.appendFileSync(LOG_FILE, logLine);
        res.json({ ok: true, message: 'Recibido por React API' });

        // Persistencia asíncrona en MongoDB
        if (db) {
            db.collection('social_posts').updateOne(
                { id: post.id },
                { $set: { ...post, updated_at: new Date() } },
                { upsert: true }
            ).catch(err => console.error("[ERROR] MongoDB Insert failed:", err.message));
        }
    } catch (err) {
        console.error("Error escribiendo log:", err);
        res.status(500).json({ ok: false, error: "Internal Server Error" });
    }
});

/**
 * Endpoint DLQ (Dead Letter Queue)
 */
app.post('/errors', (req, res) => {
    const errorData = req.body;
    const ERROR_LOG_FILE = 'errors.log';

    const errorLine = `[${new Date().toISOString()}] CASE=${errorData.case || 'unknown'} | ERROR=${JSON.stringify(errorData.error || 'no error info')} | PAYLOAD=${JSON.stringify(errorData.payload || 'no payload')}\n`;

    fs.appendFileSync(ERROR_LOG_FILE, errorLine);
    console.log(`Error logged to DLQ: ${errorData.case}`);

    res.json({ ok: true, message: 'Error logged to DLQ' });
});

/**
 * API Logs
 * Retorna los logs para que el componente React los visualice.
 */
app.get('/api/logs', (req, res) => {
    if (!fs.existsSync(LOG_FILE)) return res.json([]);

    // Lectura y transformación a Array
    const logs = fs.readFileSync(LOG_FILE, 'utf-8').trim().split('\n').filter(Boolean);
    res.json(logs);
});

// Start
app.listen(PORT, '0.0.0.0', () => {
    console.log(`React API escuchando en puerto ${PORT}`);
});
