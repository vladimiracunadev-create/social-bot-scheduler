# 🧩 Caso 08: 🔷 C# (.NET) -> 🌉 n8n -> 🌶️ Flask

[![Language: C#](https://img.shields.io/badge/Language-C%23-239120?logo=c-sharp&logoColor=white)](https://learn.microsoft.com/en-us/dotnet/csharp/)
[![Language: Python/Flask](https://img.shields.io/badge/Language-Flask-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Database: SQL Server](https://img.shields.io/badge/Database-SQL_Server-CC2927?logo=microsoft-sql-server&logoColor=white)](https://www.microsoft.com/sql-server/)

Este eje tecnológico integra la robustez del ecosistema empresarial de **Microsoft .NET** con la agilidad y ligereza de un receptor basado en **Python/Flask**.

---

## 🏗️ Arquitectura del Flujo

1.  **📤 Origen**: `Program.cs` (.NET 8.0) - Emisor corporativo de alto rendimiento.
2.  **🌉 Puente**: **n8n** (Webhook e Inyección HTTP)
3.  **📥 Destino**: `app.py` (Python 3.9 / Flask)
4.  **📁 Persistencia**: **SQL Server 2022** (Enterprise Relational)

---

## 🔷 Origen: .NET Enterprise Dispatcher

El emisor en C# demuestra la capacidad de integración de los lenguajes corporativos modernos:
- **Lógica**: Define objetos anónimos tipados, los serializa con **System.Text.Json** y los despacha vía **HttpClient**.
- **Tecnología**: Uso de inyección de dependencias y clientes HTTP optimizados para rendimiento masivo.

> [!TIP]
> Para poner en marcha este entorno empresarial:
> ```bash
> docker-compose --profile case08 up -d
> ```

---

## 🌶️ Destino: Flask API & Dashboard

El receptor utiliza Flask para ofrecer un punto de entrada liviano y un dashboard de visualización rápida:
- **Tecnología**: Framework **Flask** con motor de plantillas **Jinja2**.
- **Procesamiento**: Recibe y procesa el evento asíncrono para persistirlo en el motor de base de datos.
- **Base de Datos**: Gestión de datos relacionales complejos en **SQL Server**.

---

## 🛡️ Guardrails (Resiliencia)

Este caso implementa defensas para asegurar la integridad de los datos empresariales:

- **🔄 Reintentos Automáticos**: n8n aplica una política de 3 reintentos con intervalo de 1s ante latencias en el receptor Flask o SQL Server.
- **📥 Dead Letter Queue (DLQ)**: Los mensajes que no logran persistirse se derivan a una cola de auditoría para su recuperación.
- **🔍 Transaccionalidad**: SQL Server garantiza que los datos de los posts cumplan con todas las restricciones de integridad relacional.

---

## 🚦 Verificación y Acceso

- **🌐 Dashboard**: [http://localhost:8088](http://localhost:8088)
- **⚙️ API Endpoint**: `POST /webhook`
- **📁 Auditoría**: Consultable mediante SQL Management Studio o Azure Data Studio conectando al puerto interno.

---

*Desarrollado como parte del Social Bot Scheduler v4.0*

