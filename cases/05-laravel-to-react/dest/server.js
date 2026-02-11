const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 4000;
const LOG_FILE = 'posts_react.log';

app.use(cors());
app.use(express.json());

// Servir frontend React (compilado o estático)
app.use(express.static(path.join(__dirname, 'public')));

app.post('/webhook', (req, res) => {
    const post = req.body;
    const logLine = `[${new Date().toISOString()}] REACT-DASHBOARD | id=${post.id} | channel=${post.channel} | text=${post.text}\n`;
    fs.appendFileSync(LOG_FILE, logLine);
    res.json({ ok: true, message: 'Recibido por React API' });
});

app.post('/errors', (req, res) => {
    const errorData = req.body;
    const ERROR_LOG_FILE = 'errors.log';

    const errorLine = `[${new Date().toISOString()}] CASE=${errorData.case || 'unknown'} | ERROR=${JSON.stringify(errorData.error || 'no error info')} | PAYLOAD=${JSON.stringify(errorData.payload || 'no payload')}\n`;

    fs.appendFileSync(ERROR_LOG_FILE, errorLine);
    console.log(`Error logged to DLQ: ${errorData.case}`);

    res.json({ ok: true, message: 'Error logged to DLQ' });
});

app.get('/api/logs', (req, res) => {
    if (!fs.existsSync(LOG_FILE)) return res.json([]);
    const logs = fs.readFileSync(LOG_FILE, 'utf-8').trim().split('\n').filter(Boolean);
    res.json(logs);
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`React API escuchando en puerto ${PORT}`);
});
