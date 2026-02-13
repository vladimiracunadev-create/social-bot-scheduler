import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request

# ==================================================================================================
# CONFIGURACIÓN FLASK
# ==================================================================================================
app = Flask(__name__)

# Almacenamiento Volátil (Memoria RAM)
# En una arquitectura real, esto se sustituiría por una DB (PostgreSQL/Redis).
posts = []


@app.route("/")
def index():
    """
    Ruta Raíz: Renderiza el Dashboard HTML usando Jinja2.
    """
    return render_template("index.html")


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Webhook Receptor

    Procesa los posts enviados por el bot C#.
    """
    try:
        # Flask parsea automáticamente JSON o Form-Data según el Content-Type
        data = request.json
        if request.form:  # Fallback si C# enviara x-www-form-urlencoded
            data = request.form

        new_post = {
            "id": len(posts) + 1,
            "text": data.get("text", data.get("content", "No content")),
            "channel": data.get("channel", data.get("platform", "unknown")),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Inserción en cabeza (LIFO visual)
        posts.insert(0, new_post)

        # Rotación de logs (Mantiene solo los últimos 20)
        if len(posts) > 20:
            posts.pop()

        print(f"📥 New post received: {new_post['text']}")
        return jsonify({"status": "success", "message": "Post received"})

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/errors", methods=["POST"])
def errors():
    """
    Dead Letter Queue (DLQ)
    """
    try:
        error_data = request.json

        error_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CASE={error_data.get('case', 'unknown')} | ERROR={error_data.get('error', 'no error info')} | PAYLOAD={error_data.get('payload', 'no payload')}\n"

        # Escritura síncrona en archivo (bloqueante, pero simple para Flask desarrollo)
        with open("errors.log", "a", encoding="utf-8") as f:
            f.write(error_line)

        print(f"🚨 Error logged to DLQ: {error_data.get('case')}")
        return jsonify({"status": "success", "message": "Error logged to DLQ"})
    except Exception as e:
        print(f"❌ Error processing DLQ: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/posts")
def get_posts():
    """API JSON para consumo AJAX desde el Dashboard."""
    return jsonify(posts)


if __name__ == "__main__":
    # Ejecución del servidor de desarrollo integrado de Flask
    # host="0.0.0.0" expone el puerto al exterior (Docker).
    app.run(host="0.0.0.0", port=5000)
