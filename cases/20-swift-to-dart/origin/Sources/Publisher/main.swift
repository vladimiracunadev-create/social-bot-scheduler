// ================================================================================================
// EMISOR SWIFT (Case 20: Swift -> n8n -> Dart Shelf + Firestore emulator)
// ================================================================================================
// Swift no es solo iOS: en Linux es un lenguaje de sistemas compilado. Este emisor lee posts.json
// y reenvía los posts vencidos al webhook de n8n con URLSession (Foundation). Modo dry-run si
// WEBHOOK_URL no está definido.

import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

let env = ProcessInfo.processInfo.environment
let webhook = env["WEBHOOK_URL"]

let data = try Data(contentsOf: URL(fileURLWithPath: "posts.json"))
let posts = (try JSONSerialization.jsonObject(with: data)) as? [[String: Any]] ?? []

for post in posts {
    let published = post["published"] as? Bool ?? false
    if published { continue }
    let id = post["id"] as? String ?? ""

    guard let webhook = webhook, !webhook.isEmpty else {
        print("[DRY-RUN] Post \(id) reenviado.")
        continue
    }

    var req = URLRequest(url: URL(string: webhook)!)
    req.httpMethod = "POST"
    req.setValue("application/json", forHTTPHeaderField: "Content-Type")
    let payload: [String: Any] = [
        "id": id,
        "text": post["text"] as? String ?? "",
        "channel": post["channel"] as? String ?? "default",
        "scheduled_at": post["scheduled_at"] as? String ?? "",
    ]
    req.httpBody = try JSONSerialization.data(withJSONObject: payload)

    let sem = DispatchSemaphore(value: 0)
    let task = URLSession.shared.dataTask(with: req) { _, resp, err in
        if let err = err {
            print("[ERROR] Fallo reenviando \(id): \(err.localizedDescription)")
        } else if let http = resp as? HTTPURLResponse {
            print("[OK] Post \(id) -> n8n (\(http.statusCode))")
        }
        sem.signal()
    }
    task.resume()
    sem.wait()
}
