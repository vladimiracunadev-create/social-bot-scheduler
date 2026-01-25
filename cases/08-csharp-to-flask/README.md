# Caso 08: ❄️ C# (.NET) -> 🔗 n8n -> 🌶️ Flask

Este eje tecnológico integra el ecosistema empresarial de Microsoft .NET con la flexibilidad y ligereza de Python/Flask.

## 🏗️ Arquitectura del Flujo
1.  **Origen (Emisor)**: `Program.cs` (.NET 8.0) - Utiliza clientes HTTP nativos de alto rendimiento.
2.  **Puente (Orquestador)**: n8n (Nodo Webhook -> Nodo HTTP Request)
3.  **Destino (Receptor)**: `app.py` (Python 3.9 / Flask)

## ❄️ Funcionamiento: Origen (C#)
El emisor en C# demuestra la robustez del lenguaje corporativo por excelencia:
- **Lógica**: Define una lista de objetos anónimos con posts de prueba, los serializa a JSON y los despacha mediante `HttpClient`.
- **Tecnologías**: 
    - `System.Net.Http`: Para comunicaciones web seguras y eficientes.
    - `System.Text.Json`: Serialización nativa de alto rendimiento.
- **Ejecución**: Se corre con `dotnet run` desde la carpeta `origin/`.

## 🌶️ Funcionamiento: Destino (Flask)
El receptor utiliza Flask para ofrecer una API y un dashboard minimalista:
- **Tecnología**: Flask (WSGI app).
- **Procesamiento**: Recibe el POST en `/webhook`, extrae el texto y canal, y mantiene una lista en memoria de los posts recientes.
- **Dashboard**: Utiliza el motor de plantillas `Jinja2` para renderizar `index.html` con los datos en tiempo real.

## 🚦 Verificación
- **URL Dashboard**: [http://localhost:8088](http://localhost:8088)
- **Endpoint Webhook**: `POST /webhook` (Interno: 5000)
