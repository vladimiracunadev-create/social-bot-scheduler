# ==================================================================================================
# Case 15 — Servidor gRPC Go. Contexto de build = raíz del caso (para acceder a proto/).
# ==================================================================================================
FROM golang:1.23-alpine AS build
RUN apk add --no-cache protobuf git
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.35.1 \
    && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.5.1
ENV PATH="/root/go/bin:${PATH}"
WORKDIR /src
COPY origin/go.mod ./
COPY proto/social.proto ./social.proto
# Genera los stubs Go (social.pb.go + social_grpc.pb.go) en el paquete main.
RUN protoc --go_out=. --go_opt=paths=source_relative \
    --go-grpc_out=. --go-grpc_opt=paths=source_relative social.proto
COPY origin/server.go ./
RUN go mod tidy && go build -o server .

FROM alpine:3.20
WORKDIR /app
COPY --from=build /src/server ./server
EXPOSE 50051
CMD ["./server"]
