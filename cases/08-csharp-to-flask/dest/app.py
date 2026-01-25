import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
posts = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        if request.form:  # Handle form data if needed, but we expect JSON
            data = request.form

        new_post = {
            "id": len(posts) + 1,
            "text": data.get("text", data.get("content", "No content")),
            "channel": data.get("channel", data.get("platform", "unknown")),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        posts.insert(0, new_post)
        if len(posts) > 20:
            posts.pop()

        print(f"📥 New post received: {new_post['text']}")
        return jsonify({"status": "success", "message": "Post received"})
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/posts")
def get_posts():
    return jsonify(posts)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
