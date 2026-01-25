using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Generic;

class Program
{
    private static readonly HttpClient client = new HttpClient();

    static async Task Main(string[] args)
    {
        string webhookUrl = Environment.GetEnvironmentVariable("WEBHOOK_URL");
        if (string.IsNullOrEmpty(webhookUrl))
        {
            Console.WriteLine("⚠️ WEBHOOK_URL environment variable is not set. Using default.");
            webhookUrl = "http://localhost:5678/webhook/social-bot-scheduler-csharp";
        }

        Console.WriteLine("🚀 C# .NET Social Bot Producer started...");
        Console.WriteLine($"🎯 Target: {webhookUrl}");

        var posts = new List<object>
        {
            new { id = 1, text = "C# y .NET son robustos para empresas. 🏢", channel = "linkedin" },
            new { id = 2, text = "Flask es ligero y flexible. 🌶️", channel = "twitter" },
            new { id = 3, text = "La interoperabilidad es clave en microservicios. 🌐", channel = "facebook" }
        };

        while (true)
        {
            foreach (var post in posts)
            {
                var json = JsonSerializer.Serialize(post);
                var data = new StringContent(json, Encoding.UTF8, "application/json");

                try
                {
                    Console.WriteLine($"📤 Sending post: {json}");
                    var response = await client.PostAsync(webhookUrl, data);
                    Console.WriteLine($"✅ Status: {response.StatusCode}");
                }
                catch (Exception e)
                {
                    Console.WriteLine($"❌ Error: {e.Message}");
                }

                await Task.Delay(5000);
            }
        }
    }
}
