# syntax=docker/dockerfile:1
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY cmd ./cmd
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/app-gateway ./cmd/app-gateway
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/app-gateway /app-gateway
EXPOSE 8080
USER nonroot:nonroot
ENTRYPOINT ["/app-gateway"]
