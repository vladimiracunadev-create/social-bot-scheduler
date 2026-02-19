# ==================================================================================================
# RECEPTOR MINIMALISTA DE ALTO ACOPLAMIENTO (Case 07: Rust -> n8n -> Ruby/Sinatra + Cassandra)
# ==================================================================================================
# ¿Por qué Ruby/Sinatra para el receptor?
# Sinatra es el micro-framework original que inspiró a Flask (Python), Express (Node.js), y Gin (Go).
# Su filosofía "Convention over Configuration" permite crear un Webhook receptor funcional 
# en menos de 50 líneas de código, demostrando que la complejidad del receptor no necesita 
# escalar con la complejidad del emisor (Rust).
# 
# Persistencia en Apache Cassandra:
# Cassandra es una base de datos NoSQL distribuida, diseñada para manejar cantidades masivas 
# de datos con alta disponibilidad y sin punto único de fallo (SPOF). Es la base de datos 
# más exigente en recursos de todo el ecosistema (requiere ~2GB RAM mínimo por nodo).
# 
# ⚠️ Hallazgo del Stress Test:
# En máquinas con RAM limitada (<10GB), Cassandra fue el primer servicio en ser eliminado 
# por el OOM Killer del kernel, documentado en DOCKER_RESOURCES.md.
# 
# Patrones aplicados:
# - FIFO Queue (In-Memory): Cola limitada a 20 posts (rotación automática).
# - Rack::Protection: Desactivación selectiva de HostAuthorization para entornos Docker internos.
# - Idempotencia: Cassandra usa INSERT que sobrescribe por PRIMARY KEY automáticamente.

require 'sinatra'
require 'json'
require 'cassandra'

# ==================================================================================================
# CONFIGURACIÓN DE BASE DE DATOS (Cassandra)
# ==================================================================================================
$cassandra_host = ENV['DB_HOST'] || 'db-cassandra'
$cassandra_cluster = nil
$cassandra_session = nil

def init_cassandra
  begin
    $cassandra_cluster = Cassandra.cluster(hosts: [$cassandra_host])
    $cassandra_session = $cassandra_cluster.connect
    
    # Crear Keyspace y Tabla
    $cassandra_session.execute("CREATE KEYSPACE IF NOT EXISTS social_bot WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}")
    $cassandra_session.execute("USE social_bot")
    $cassandra_session.execute("CREATE TABLE IF NOT EXISTS social_posts (id text PRIMARY KEY, text text, channel text, scheduled_at text, created_at timestamp)")
    puts "[INFO] Cassandra initialized."
  rescue => e
    puts "[ERROR] Cassandra failed: #{e.message}"
  end
end

init_cassandra

# ==================================================================================================
# CONFIGURACIÓN SINATRA
# ==================================================================================================
# Bind 0.0.0.0 permite acceso externo (necesario para Docker/Red).
set :bind, '0.0.0.0'
set :port, 4567

# Desactivar explícitamente el HostAuthorization de Rack::Protection
# En entornos n8n/Docker, esto bloquea peticiones de hostnames internos.
set :protection, :except => [:host_authorization, :json_csrf] # json_csrf también puede dar problemas
set :host_authorization, { permitted_hosts: [] } # Permitir todos los hosts

# Estado Global en Memoria (No persistente)
# Simula una base de datos. En producción, esto sería Redis o PostgreSQL.
# Ruby maneja la memoria automáticamente (GC).
$posts = []

# ==================================================================================================
# ENDPOINTS (RUTAS)
# ==================================================================================================

# Ruta Raíz: Renderiza la vista ERB (Embedded Ruby)
get '/' do
  erb :index
end

# Webhook Receptor
# Recibe el JSON del bot en Rust.
post '/webhook' do
  content_type :json
  
  # Lectura y Parsing del Cuerpo de la Petición
  request.body.rewind # Buena práctica por si el body ya fue leído
  data = JSON.parse(request.body.read)
  
  # Transformación de Datos
  new_post = {
    'id' => $posts.length + 1,
    'text' => data['text'],
    'channel' => data['channel'],
    'timestamp' => Time.now.strftime("%Y-%m-%d %H:%M:%S")
  }
  
  # Gestión de la Cola en Memoria (FIFO limitado a 20)
  $posts.unshift(new_post) # Agrega al inicio
  if $posts.length > 20
    $posts.pop # Elimina el último (el más viejo)
  end
  
  puts "📥 New post received: #{new_post['text']}"
  
  # Retorno explícito de JSON
  # En Ruby, la última expresión evaluada es el valor de retorno.
  { status: 'success', message: 'Post received' }.to_json

  # Persistencia en Cassandra
  if $cassandra_session
    begin
      insert = $cassandra_session.prepare("INSERT INTO social_posts (id, text, channel, scheduled_at, created_at) VALUES (?, ?, ?, ?, ?)")
      $cassandra_session.execute(insert, arguments: [data['id'], data['text'], data['channel'], data['scheduled_at'], Time.now])
    rescue => e
      puts "[ERROR] Cassandra Insert error: #{e.message}"
    end
  end
end

# Dead Letter Queue (DLQ)
# Manejo de reportes de error.
post '/errors' do
  content_type :json
  data = JSON.parse(request.body.read)
  
  error_line = "[#{Time.now.strftime('%Y-%m-%d %H:%M:%S')}] CASE=#{data['case'] || 'unknown'} | ERROR=#{data['error'].to_json} | PAYLOAD=#{data['payload'].to_json}\n"
  
  # Escritura a Archivo (Append Mode)
  # El bloque File.open asegura que el descriptor se cierre automáticamente al terminar el bloque.
  File.open('errors.log', 'a') do |f|
    f.write(error_line)
  end
  
  puts "🚨 Error logged to DLQ: #{data['case']}"
  { status: 'success', message: 'Error logged to DLQ' }.to_json
end

# API para el Frontend (Polling)
get '/api/posts' do
  content_type :json
  $posts.to_json
end
