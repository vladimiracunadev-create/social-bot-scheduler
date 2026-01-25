FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY main.go .
RUN go build -o receiver main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/receiver .
EXPOSE 8080
CMD ["./receiver"]
