from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import os

app = FastAPI(title="Social Bot Receiver - FastAPI")
LOG_FILE = "social_bot_fastapi.log"


class Post(BaseModel):
    id: str
    text: str
    channel: str = "default"
    scheduled_at: str = None


@app.post("/webhook")
async def receive_post(post: Post):
    log_line = f"[{datetime.now().isoformat()}] FASTAPI-RECEIVER | id={post.id} | channel={post.channel} | text={post.text}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

    print(f"Post recibido en FastAPI: {post.id}")
    return {
        "ok": True,
        "message": "Post recibido por FastAPI",
        "case": "04-node-to-fastapi",
    }


@app.get("/logs")
async def get_logs():
    if not os.path.exists(LOG_FILE):
        return {"ok": True, "logs": []}
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = f.readlines()
    return {"ok": True, "logs": [line.strip() for line in logs]}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
