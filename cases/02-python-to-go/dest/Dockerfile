FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod ./
COPY main.go .
COPY index.html .

# go mod tidy generates go.sum on the fly so the repo doesn't need to ship one.
RUN go mod tidy && go build -o main main.go

FROM alpine:3.20.6
WORKDIR /root/
COPY --from=builder /app/main .
COPY index.html .
EXPOSE 8080
CMD ["./main"]
