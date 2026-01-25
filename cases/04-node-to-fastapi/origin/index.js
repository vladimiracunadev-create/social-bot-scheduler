const fs = require('fs');
const axios = require('axios');

const WEBHOOK_URL = process.env.WEBHOOK_URL;
const POSTS_FILE = 'posts.json';

async function sendPost(post) {
    if (!WEBHOOK_URL) {
        console.log(`[DRY-RUN] Post ${post.id} enviado.`);
        return true;
    }
    try {
        const response = await axios.post(WEBHOOK_URL, post);
        if (response.status >= 200 && response.status < 300) {
            console.log(`Post ${post.id} enviado con éxito.`);
            return true;
        }
    } catch (error) {
        console.error(`Error enviando post ${post.id}:`, error.message);
    }
    return false;
}

async function processPosts() {
    if (!fs.existsSync(POSTS_FILE)) return;

    const data = JSON.parse(fs.readFileSync(POSTS_FILE, 'utf-8'));
    let changed = false;
    const now = new Date();

    for (let post of data) {
        const scheduledAt = new Date(post.scheduled_at);
        if (!post.published && scheduledAt <= now) {
            console.log(`Enviando post ${post.id}...`);
            const ok = await sendPost(post);
            if (ok) {
                post.published = true;
                changed = true;
            }
        }
    }

    if (changed) {
        fs.writeFileSync(POSTS_FILE, JSON.stringify(data, null, 2), 'utf-8');
    }
}

console.log('Emisor Node.js iniciado...');
setInterval(processPosts, 30000);
processPosts();
