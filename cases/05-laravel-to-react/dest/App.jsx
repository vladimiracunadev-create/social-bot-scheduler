import React, { useState, useEffect } from 'react';

/**
 * Componente Principal React
 * 
 * Funcionalidad:
 *   - Polling periódico a la API para obtener logs actualizados.
 *   - Renderizado de dashboard con estética moderna (Glassmorphism).
 */
function App() {
    const [logs, setLogs] = useState([]);

    // Función de Fetching Asíncrono
    const fetchLogs = async () => {
        try {
            const res = await fetch('/api/logs');
            const data = await res.json();
            // Invertimos array para mostrar lo más reciente arriba
            setLogs(data.reverse());
        } catch (e) {
            console.error("Error fetching logs:", e);
        }
    };

    // Efecto de Montaje + Intervalo
    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000); // Polling cada 5s
        return () => clearInterval(interval); // Cleanup al desmontar
    }, []);

    return (
        <div style={{ padding: '40px', fontFamily: '"Outfit", sans-serif', backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc' }}>
            {/* Header con gradiente y clip de texto */}
            <h1 style={{ background: 'linear-gradient(90deg, #61dafb, #a855f7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                ⚛️ React Enterprise Dashboard
            </h1>
            <div style={{ background: 'rgba(30, 41, 59, 0.7)', padding: '20px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)' }}>
                <h2>Últimas Publicaciones</h2>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ color: '#94a3b8', textAlign: 'left' }}>
                            <th>Registro</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody>
                        {/* Mapeo de Logs */}
                        {logs.map((log, i) => (
                            <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                <td style={{ padding: '12px' }}>{log}</td>
                                <td><span style={{ color: '#61dafb' }}>✓ Recibido</span></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default App;
