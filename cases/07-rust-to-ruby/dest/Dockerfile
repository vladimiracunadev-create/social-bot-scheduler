FROM ruby:3.2-alpine

WORKDIR /app


RUN apk add --no-cache build-base
RUN gem install sinatra rackup puma

COPY . .

EXPOSE 4567

CMD ["ruby", "app.rb"]
