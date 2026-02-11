require 'sinatra'
require 'json'

set :bind, '0.0.0.0'
set :port, 4567

$posts = []

get '/' do
  erb :index
end

post '/webhook' do
  content_type :json
  data = JSON.parse(request.body.read)
  
  new_post = {
    'id' => $posts.length + 1,
    'text' => data['text'],
    'channel' => data['channel'],
    'timestamp' => Time.now.strftime("%Y-%m-%d %H:%M:%S")
  }
  
  $posts.unshift(new_post)
  if $posts.length > 20
    $posts.pop
  end
  
  puts "📥 New post received: #{new_post['text']}"
  { status: 'success', message: 'Post received' }.to_json
end

post '/errors' do
  content_type :json
  data = JSON.parse(request.body.read)
  
  error_line = "[#{Time.now.strftime('%Y-%m-%d %H:%M:%S')}] CASE=#{data['case'] || 'unknown'} | ERROR=#{data['error'].to_json} | PAYLOAD=#{data['payload'].to_json}\n"
  
  File.open('errors.log', 'a') do |f|
    f.write(error_line)
  end
  
  puts "🚨 Error logged to DLQ: #{data['case']}"
  { status: 'success', message: 'Error logged to DLQ' }.to_json
end

get '/api/posts' do
  content_type :json
  $posts.to_json
end
