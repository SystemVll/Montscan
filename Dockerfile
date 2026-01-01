# BUILD
FROM golang:1.21-alpine AS builder

WORKDIR /app

RUN apk add --no-cache git

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o montscan .

# RUNTIME
FROM alpine:3.19

WORKDIR /app

RUN apk add --no-cache \
    poppler-utils \
    ca-certificates \
    tzdata

COPY --from=builder /app/montscan .

RUN mkdir -p /app/scans

EXPOSE 21 21000-21010

CMD ["./montscan"]
