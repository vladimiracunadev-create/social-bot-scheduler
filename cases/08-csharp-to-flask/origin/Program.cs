// ==================================================================================================
// EMISOR EMPRESARIAL .NET (Case 08: C# -> n8n -> Flask + MSSQL)
// ==================================================================================================
// ¿Por qué C# / .NET para el emisor?
// C# es el lenguaje dominante en entornos corporativos Microsoft. Este caso simula el escenario 
// donde una aplicación .NET legacy (ej: ERP, CRM) necesita enviar datos a un microservicio 
// moderno en Python (Flask) a través del bus de eventos n8n.
// 
// Patrones Clave de .NET en este archivo:
// - HttpClient Estático: Diseño recomendado por Microsoft para evitar Socket Exhaustion.
//   Instanciar HttpClient por request agotaría los puertos TCP del sistema operativo.
// - async/await: Modelo de concurrencia no-bloqueante nativo de C# 5.0+.
// - System.Text.Json: Serializador JSON de alto rendimiento, reemplazando a Newtonsoft.Json.
// - Task.Delay: Pausa no-bloqueante (no consume CPU mientras espera, a diferencia de Thread.Sleep).
// 
// Persistencia en SQL Server (Destino):
// MSSQL es la base de datos más pesada del ecosistema (~2GB RAM mínimo). El receptor Flask 
// utiliza pyodbc con el driver ODBC 18 para conectarse, demostrando la interoperabilidad 
// cross-platform (Python + Linux + MSSQL).

using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Generic;

class Program
{
    // Cliente HTTP Estático (Best Practice)
    // HttpClient está diseñado para ser reutilizado durante la vida útil de la aplicación.
    // Instanciarlo en cada petición ("using (var client = new HttpClient())") puede agotar los sockets (Socket Exhaustion).
    private static readonly HttpClient client = new HttpClient();

    // Punto de Entrada Asíncrono (C# 7.1+)
    static async Task Main(string[] args)
    {
        // 1. Configuración
        string webhookUrl = Environment.GetEnvironmentVariable("WEBHOOK_URL");
        
        // Fallback para desarrollo local
        if (string.IsNullOrEmpty(webhookUrl))
        {
            Console.WriteLine("⚠️ WEBHOOK_URL environment variable is not set. Using default.");
            // Nota: Este puerto 5678 sugiere que el tráfico pasa primero por n8n en el flujo completo,
            // aunque el caso se llame "C# to Flask".
            webhookUrl = "http://localhost:5678/webhook/social-bot-scheduler-csharp";
        }

        Console.WriteLine("🚀 C# .NET Social Bot Producer started...");
        Console.WriteLine($"🎯 Target: {webhookUrl}");

        // 2. Datos en Memoria (Simulación DB)
        // Usamos tipos anónimos (Anonymous Types) para simplicidad, serializados a JSON automáticamente.
        var posts = new List<object>
        {
            new { id = 1, text = "C# y .NET son robustos para empresas. 🏢", channel = "linkedin" },
            new { id = 2, text = "Flask es ligero y flexible. 🌶️", channel = "twitter" },
            new { id = 3, text = "La interoperabilidad es clave en microservicios. 🌐", channel = "facebook" }
        };

        // 3. Bucle Infinito (Producer Pattern)
        while (true)
        {
            foreach (var post in posts)
            {
                // Serialización JSON (System.Text.Json es nativo y de alto rendimiento)
                var json = JsonSerializer.Serialize(post);
                var data = new StringContent(json, Encoding.UTF8, "application/json");

                try
                {
                    Console.WriteLine($"📤 Sending post: {json}");
                    
                    // Envío Asíncrono (await)
                    // No bloquea el hilo principal, permitiendo alta concurrencia si se escalara.
                    var response = await client.PostAsync(webhookUrl, data);
                    
                    Console.WriteLine($"✅ Status: {response.StatusCode}");
                }
                catch (Exception e)
                {
                    Console.WriteLine($"❌ Error: {e.Message}");
                }

                // Espera no bloqueante
                await Task.Delay(5000);
            }
        }
    }
}
