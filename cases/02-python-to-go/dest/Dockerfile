FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY main.go .
COPY index.html .

RUN go mod init social-bot-dest-go && \
    go get github.com/go-sql-driver/mysql

RUN go build -o main main.go

FROM alpine:3.20.6
WORKDIR /root/
COPY --from=builder /app/main .
COPY index.html .
EXPOSE 8080
CMD ["./main"]
