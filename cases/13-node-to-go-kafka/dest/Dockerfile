# ==================================================================================================
# Case 13 — Consumer Go (kafka-go) + sink ClickHouse. Binario estático.
# ==================================================================================================
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY main.go ./
RUN go mod tidy && CGO_ENABLED=0 go build -o server .

FROM alpine:3.20
WORKDIR /app
COPY --from=build /src/server ./server
COPY index.html ./index.html
EXPOSE 8080
ENV PORT=8080
CMD ["./server"]
