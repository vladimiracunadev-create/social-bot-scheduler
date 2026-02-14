import json

FPATH = "n8n/workflows/case-01-python-to-php.json"
with open(FPATH, "r", encoding="utf-8") as f:
    data = json.load(f)

for node in data["nodes"]:
    if (
        node["type"] == "n8n-nodes-base.set"
        or node["type"] == "n8n-nodes-base.executeCommand"
    ):
        node["type"] = "n8n-nodes-base.executeCommand"
        node["typeVersion"] = 2
        node["parameters"] = {"command": "echo success"}
        node["name"] = "Execute Command"

with open(FPATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("Modified Case 01 to v2")
