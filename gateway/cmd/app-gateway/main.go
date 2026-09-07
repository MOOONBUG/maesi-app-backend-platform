package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"sync"
	"syscall"
	"time"
)

type response struct {
	RequestID string `json:"request_id"`
	Status    string `json:"status"`
	Message   string `json:"message,omitempty"`
}
type idempotencyStore struct {
	mu      sync.Mutex
	results map[string][]byte
}

func newStore() *idempotencyStore { return &idempotencyStore{results: map[string][]byte{}} }
func (s *idempotencyStore) get(k string) ([]byte, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	v, ok := s.results[k]
	return append([]byte(nil), v...), ok
}
func (s *idempotencyStore) put(k string, v []byte) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.results[k] = append([]byte(nil), v...)
}
func requestID(r *http.Request) string {
	if v := strings.TrimSpace(r.Header.Get("X-Request-ID")); v != "" {
		return v
	}
	b := make([]byte, 8)
	if _, e := rand.Read(b); e == nil {
		return hex.EncodeToString(b)
	}
	return "generated-" + time.Now().UTC().Format("20060102150405.000000000")
}
func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

type requestIDKey struct{}

func withRequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		id := requestID(r)
		w.Header().Set("X-Request-ID", id)
		next.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), requestIDKey{}, id)))
	})
}
func idempotentHeartbeat(store *idempotencyStore) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		id := r.Context().Value(requestIDKey{}).(string)
		key := strings.TrimSpace(r.Header.Get("Idempotency-Key"))
		if key == "" {
			writeJSON(w, 400, response{RequestID: id, Status: "invalid_request", Message: "Idempotency-Key is required"})
			return
		}
		if cached, ok := store.get(key); ok {
			w.Header().Set("X-Idempotent-Replay", "true")
			w.WriteHeader(200)
			_, _ = w.Write(cached)
			return
		}
		select {
		case <-time.After(5 * time.Millisecond):
		case <-r.Context().Done():
			return
		}
		body, _ := json.Marshal(response{RequestID: "", Status: "accepted", Message: "heartbeat recorded"})
		body = append(body, byte(10))
		store.put(key, body)
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(body)
	})
}
func main() {
	addr := os.Getenv("GATEWAY_ADDR")
	if addr == "" {
		addr = ":8080"
	}
	store := newStore()
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) { writeJSON(w, 200, map[string]string{"status": "ok"}) })
	mux.HandleFunc("/readyz", func(w http.ResponseWriter, _ *http.Request) { writeJSON(w, 200, map[string]string{"status": "ready"}) })
	mux.Handle("/v1/session/heartbeat", idempotentHeartbeat(store))
	server := &http.Server{Addr: addr, Handler: withRequestID(mux), ReadHeaderTimeout: 3 * time.Second, ReadTimeout: 10 * time.Second, WriteTimeout: 10 * time.Second, IdleTimeout: 60 * time.Second}
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	go func() {
		log.Printf("app-gateway listening on %s", addr)
		if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatal(err)
		}
	}()
	<-ctx.Done()
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	_ = server.Shutdown(shutdownCtx)
}
