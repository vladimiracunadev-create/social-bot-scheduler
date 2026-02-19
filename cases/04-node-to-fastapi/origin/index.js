const fs = require('fs');

/**
 * EMISOR ORIENTADO A EVENTOS (Node.js)
 * -----------------------------------
 * ¿Por qué Node.js para el emisor?
 * Node.js es excelente para tareas de entrada/salida (I/O) masivas. En este flujo (04), 
 * el bot emisor utiliza un bucle de polling asíncrono que no bloquea la ejecución de otros 
 * procesos, permitiendo que el emisor escale de forma eficiente.
 * 
 * Estrategia:
 * - Polling No-Bloqueante: Uso de `setInterval` para verificar estados.
 * - Axios: Cliente HTTP moderno para manejar promesas y reintentos.
 * - JSON-DB: Persistencia ligera en archivos para mantener el estado del bot.
 */

const axios = require('axios');

// =================================================================================================
// CONFIGURACIÓN Y CONSTANTES
// =================================================================================================
// Se obtienen las configuraciones del entorno (Best Practice: 12-Factor App)
const WEBHOOK_URL = process.env.WEBHOOK_URL;
const POSTS_FILE = 'posts.json';

/**
 * Función encargada de realizar la petición HTTP al servicio destino.
 * 
 * Contexto:
 *   Encapsula la lógica de red y el manejo de errores para que el bucle principal
 *   se mantenga limpio y enfocado en la lógica de negocio.
 * 
 * @param {Object} post - Objeto post completo a enviar.
 * @returns {Promise<boolean>} - True si el envío fue exitoso, False en caso contrario.
 */
async function sendPost(post) {
    // Modo Dry-Run (Simulación)
    // Si no hay URL configurada, simulamos el envío para permitir pruebas locales sin dependencia del backend.
    if (!WEBHOOK_URL) {
        console.log(`[DRY-RUN] Post ${post.id} enviado.`);
        return true;
    }

    try {
        // Axios lanza una excepción automáticamente si el status code está fuera del rango 2xx.
        const response = await axios.post(WEBHOOK_URL, post);
        if (response.status >= 200 && response.status < 300) {
            console.log(`[OK] Post ${post.id} enviado con éxito.`);
            return true;
        }
    } catch (error) {
        // Manejo de errores de red (Socket hang up, Timeout, etc.)
        console.error(`[ERROR] Fallo enviando post ${post.id}:`, error.message);
    }
    return false;
}

/**
 * Ciclo Principal de Procesamiento.
 * 
 * Mecanismo:
 *   1. Lectura del archivo de estado (posts.json).
 *   2. Iteración y filtrado de posts pendientes.
 *   3. Envío secuencial (await en bucle) para garantizar orden.
 *   4. Escritura en disco solo si hubo cambios (Batch Update).
 */
async function processPosts() {
    // Si no existe la "base de datos", no hacemos nada.
    if (!fs.existsSync(POSTS_FILE)) return;

    // Lectura Síncrona
    // En scripts tipo demonio/cron que corren cada X segundos, la lectura síncrona es aceptable
    // y simplifica el flujo al evitar callbacks anidados.
    const data = JSON.parse(fs.readFileSync(POSTS_FILE, 'utf-8'));
    let changed = false;
    const now = new Date();

    for (let post of data) {
        const scheduledAt = new Date(post.scheduled_at);

        // Regla de Negocio: Publicar si fecha_programada <= ahora Y no está publicado
        if (!post.published && scheduledAt <= now) {
            console.log(`Procesando post ${post.id}...`);

            // Await dentro del bucle:
            // Esto hace que los posts se envíen uno por uno (Serial).
            // Si quisiéramos paralelismo, usaríamos Promise.all(), pero complicaría el manejo de errores parciales.
            const ok = await sendPost(post);
            if (ok) {
                post.published = true;
                changed = true;
            }
        }
    }

    // Persistencia Condicional
    // Evita escrituras innecesarias en el disco SSD/SD.
    if (changed) {
        fs.writeFileSync(POSTS_FILE, JSON.stringify(data, null, 2), 'utf-8');
        console.log("Base de datos actualizada.");
    }
}

// =================================================================================================
// ARRANQUE DEL BOOTSTRAP
// =================================================================================================
console.log('Iniciando Emisor Node.js (Daemon)...');

// Ejecución Inmediata
processPosts();

// Programación del Intervalo (Polling)
// Se ejecutará processPosts cada 30 segundos indefinidamente.
// Nota: setInterval no espera a que termine la ejecución anterior. Si processPosts tarda más de 30s,
// podrían solaparse ejecuciones (Race Condition potencial en fs.writeFileSync).
// En producción real, sería mejor usar setTimeout recursivo.
setInterval(processPosts, 30000);
