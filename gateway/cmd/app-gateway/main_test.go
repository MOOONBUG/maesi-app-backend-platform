package main

import (
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHeartbeatIsIdempotent(t *testing.T) {
	h := withRequestID(idempotentHeartbeat(newStore()))
	a := httptest.NewRequest(http.MethodPost, "/v1/session/heartbeat", nil)
	a.Header.Set("Idempotency-Key", "device:42")
	w1 := httptest.NewRecorder()
	h.ServeHTTP(w1, a)
	b := httptest.NewRequest(http.MethodPost, "/v1/session/heartbeat", nil)
	b.Header.Set("Idempotency-Key", "device:42")
	w2 := httptest.NewRecorder()
	h.ServeHTTP(w2, b)
	x, _ := io.ReadAll(w1.Result().Body)
	y, _ := io.ReadAll(w2.Result().Body)
	if w1.Code != 200 || w2.Code != 200 || string(x) != string(y) || w2.Header().Get("X-Idempotent-Replay") != "true" {
		t.Fatal("not idempotent")
	}
}
func TestHeartbeatRequiresKey(t *testing.T) {
	w := httptest.NewRecorder()
	withRequestID(idempotentHeartbeat(newStore())).ServeHTTP(w, httptest.NewRequest(http.MethodPost, "/v1/session/heartbeat", nil))
	if w.Code != 400 {
		t.Fatal(w.Code)
	}
}
