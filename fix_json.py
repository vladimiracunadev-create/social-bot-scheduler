import json
import os

path = r'cases\03-go-to-node\dest\package.json'
data = {
    "name": "social-bot-node",
    "version": "1.0.0",
    "description": "",
    "main": "server.js",
    "dependencies": {
        "express": "^4.18.2"
    },
    "scripts": {
        "start": "node server.js"
    },
    "author": "",
    "license": "ISC"
}

# Ensure directory exists
os.makedirs(os.path.dirname(path), exist_ok=True)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Fixed {path}")
