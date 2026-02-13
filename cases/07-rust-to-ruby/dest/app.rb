require 'sinatra'
require 'json'

# ==================================================================================================
# CONFIGURACIÓN SINATRA
# ==================================================================================================
# Bind 0.0.0.0 permite acceso externo (necesario para Docker/Red).
set :bind, '0.0.0.0'
set :port, 4567

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
