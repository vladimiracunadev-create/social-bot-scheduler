const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;
const LOG_FILE = path.join(__dirname, 'social_bot_node.log');

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Endpoint para recibir posts
app.post('/webhook', (req, res) => {
    const post = req.body;

    if (!post.id || !post.text) {
        return res.status(422).json({ ok: false, error: 'Faltan campos obligatorios' });
    }

    const logLine = `[${new Date().toISOString()}] NODE-RECEIVER | id=${post.id} | channel=${post.channel || 'default'} | text=${post.text}\n`;

    fs.appendFileSync(LOG_FILE, logLine);
    console.log(`Post recibido en Node: ${post.id}`);

    res.json({
        ok: true,
        message: 'Post recibido por receptor Node/Express',
        case: '03-go-to-node'
    });
});

// Endpoint para el dashboard
app.get('/logs', (req, res) => {
    if (!fs.existsSync(LOG_FILE)) {
        return res.json({ ok: true, logs: [] });
    }
    const logs = fs.readFileSync(LOG_FILE, 'utf-8').split('\n').filter(Boolean);
    res.json({ ok: true, logs });
});

// Endpoint de ERRORES (DLQ)
app.post('/errors', (req, res) => {
    const errorData = req.body;
    const ERROR_LOG_FILE = path.join(__dirname, 'errors.log');

    const errorLine = `[${new Date().toISOString()}] CASE=${errorData.case || 'unknown'} | ERROR=${JSON.stringify(errorData.error || 'no error info')} | PAYLOAD=${JSON.stringify(errorData.payload || 'no payload')}\n`;

    fs.appendFileSync(ERROR_LOG_FILE, errorLine);
    console.log(`Error logged to DLQ: ${errorData.case}`);

    res.json({
        ok: true,
        message: 'Error logged to DLQ'
    });
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Servidor Node.js escuchando en puerto ${PORT}`);
});
