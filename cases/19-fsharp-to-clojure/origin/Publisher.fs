// ================================================================================================
// EMISOR F# (.NET) (Case 19: F# -> n8n -> Clojure (Ring) + XTDB)
// ================================================================================================
// F# es un lenguaje funcional-first sobre .NET. Este emisor lee posts.json y reenvía los posts
// vencidos al webhook de n8n con HttpClient. Modo dry-run si WEBHOOK_URL no está definido.
module Publisher

open System
open System.IO
open System.Net.Http
open System.Text
open System.Text.Json

let private getStr (el: JsonElement) (name: string) (fallback: string) =
    match el.TryGetProperty(name) with
    | true, v when v.ValueKind = JsonValueKind.String -> v.GetString()
    | _ -> fallback

[<EntryPoint>]
let main _ =
    let webhook = Environment.GetEnvironmentVariable("WEBHOOK_URL")
    let json = File.ReadAllText("posts.json")
    use doc = JsonDocument.Parse(json)
    use client = new HttpClient()

    for post in doc.RootElement.EnumerateArray() do
        let published =
            match post.TryGetProperty("published") with
            | true, p when p.ValueKind = JsonValueKind.True -> true
            | _ -> false

        if not published then
            let id = getStr post "id" ""
            if String.IsNullOrEmpty(webhook) then
                printfn "[DRY-RUN] Post %s reenviado." id
            else
                let payload =
                    {| id = id
                       text = getStr post "text" ""
                       channel = getStr post "channel" "default"
                       scheduled_at = getStr post "scheduled_at" "" |}
                let body = JsonSerializer.Serialize(payload)
                use content = new StringContent(body, Encoding.UTF8, "application/json")
                try
                    let resp = client.PostAsync(webhook, content).Result
                    printfn "[OK] Post %s -> n8n (%d)" id (int resp.StatusCode)
                with ex ->
                    printfn "[ERROR] Fallo reenviando %s: %s" id ex.Message
    0
