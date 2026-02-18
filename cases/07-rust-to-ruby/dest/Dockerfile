FROM ruby:3.2-alpine

WORKDIR /app


RUN apk add --no-cache build-base
RUN apk add --no-cache build-base openssl-dev zlib-dev && \
    gem install sinatra thin cassandra-driver rackup puma

COPY . .

EXPOSE 4567

CMD ["ruby", "app.rb"]
