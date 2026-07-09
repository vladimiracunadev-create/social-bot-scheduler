FROM ruby:3.2-alpine

WORKDIR /app


RUN apk add --no-cache build-base
# sorted_set: cassandra-driver 3.2.5 usa SortedSet, removido del stdlib en Ruby 3.2.
RUN apk add --no-cache build-base openssl-dev zlib-dev && \
    gem install sinatra thin cassandra-driver sorted_set rackup puma

COPY . .

EXPOSE 4567

CMD ["ruby", "app.rb"]
