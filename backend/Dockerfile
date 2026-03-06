FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copia módulos
COPY go.mod go.sum ./
RUN go mod download

# Copia código fonte
COPY . .

# Build
RUN CGO_ENABLED=0 GOOS=linux go build -o /backend ./cmd/api

# Imagem final
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /backend .

EXPOSE 8080

CMD ["./backend"]
