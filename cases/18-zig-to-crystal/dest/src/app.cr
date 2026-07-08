# ==================================================================================================
# RECEPTOR CRYSTAL/KEMAL (Case 18: Zig -> n8n -> Crystal (Kemal) + Neo4j)
# ==================================================================================================
# Crystal ofrece sintaxis tipo Ruby con rendimiento compilado (LLVM). Kemal es su microframework web
# (estilo Sinatra). La persistencia es un grafo Neo4j: cada post es un nodo `(:Post)`, accedido vía
# la API HTTP transaccional de Neo4j con Cypher — sin necesidad de un driver Bolt nativo.
#
# Cumple el contrato REST homogéneo del laboratorio: /webhook, /errors, /logs, /health, /.

require "kemal"
require "http/client"
require "json"
require "base64"

NEO4J_URL  = ENV["NEO4J_URL"]? || "http://neo4j-18:7474"
NEO4J_USER = ENV["NEO4J_USER"]? || "neo4j"
NEO4J_PASS = ENV["NEO4J_PASS"]? || "change-me-case18-local"
PORT       = (ENV["PORT"]? || "8080").to_i

# --- Cliente Neo4j (API HTTP transaccional, Cypher) ---
def neo4j_query(cypher : String, params : Hash(String, String)) : HTTP::Client::Response
  body = {statements: [{statement: cypher, parameters: params}]}.to_json
  headers = HTTP::Headers{
    "Content-Type"  => "application/json",
    "Authorization" => "Basic #{Base64.strict_encode("#{NEO4J_USER}:#{NEO4J_PASS}")}",
  }
  HTTP::Client.post("#{NEO4J_URL}/db/neo4j/tx/commit", headers: headers, body: body)
end

# Espera a que Neo4j acepte consultas (el arranque de la JVM tarda).
def wait_for_neo4j
  60.times do |attempt|
    begin
      resp = neo4j_query("RETURN 1", {} of String => String)
      if resp.status_code == 200
        puts "[bootstrap] Neo4j listo."
        return
      end
    rescue ex
      puts "[bootstrap] Neo4j no listo (intento #{attempt + 1}): #{ex.message}"
    end
    sleep 2.seconds
  end
  raise "Neo4j no respondió a tiempo."
end

wait_for_neo4j

get "/health" do |env|
  env.response.content_type = "application/json"
  {ok: true, engine: "neo4j"}.to_json
end

post "/webhook" do |env|
  raw = env.request.body.try(&.gets_to_end) || "{}"
  payload = JSON.parse(raw).as_h? || {} of String => JSON::Any
  id = payload["id"]?.try(&.as_s?)
  text = payload["text"]?.try(&.as_s?)
  if id.nil? || text.nil? || id.empty? || text.empty?
    env.response.status_code = 422
    env.response.content_type = "application/json"
    next {ok: false, error: "id y text son obligatorios"}.to_json
  end
  channel = payload["channel"]?.try(&.as_s?) || "default"
  neo4j_query(
    "MERGE (p:Post {id:$id}) SET p.text=$text, p.channel=$channel, p.created_at=timestamp()",
    {"id" => id, "text" => text, "channel" => channel}
  )
  puts "Post persistido en Neo4j: #{id}"
  env.response.content_type = "application/json"
  {ok: true, message: "Post persistido en Neo4j (Crystal/Kemal)", case: "18-zig-to-crystal"}.to_json
end

post "/errors" do |env|
  puts "Error en DLQ: #{env.request.body.try(&.gets_to_end)}"
  env.response.content_type = "application/json"
  {ok: true, message: "Error registrado en DLQ"}.to_json
end

get "/logs" do |env|
  logs = [] of String
  resp = neo4j_query(
    "MATCH (p:Post) RETURN p.id, p.channel, p.text, p.created_at ORDER BY p.created_at DESC LIMIT 20",
    {} of String => String
  )
  if resp.status_code == 200
    data = JSON.parse(resp.body)
    rows = data["results"][0]["data"].as_a
    rows.each do |entry|
      r = entry["row"].as_a
      logs << "[#{r[3]}] NEO4J | id=#{r[0]} | channel=#{r[1]} | text=#{r[2]}"
    end
  end
  env.response.content_type = "application/json"
  {ok: true, logs: logs}.to_json
end

get "/" do |env|
  env.response.content_type = "text/html"
  File.exists?("./public/index.html") ? File.read("./public/index.html") : "<h1>Dashboard no encontrado</h1>"
end

Kemal.config.host_binding = "0.0.0.0"
Kemal.config.port = PORT
Kemal.run
