package main

import (
	"log"
	"net/http"
	"os"

	"github.com/amigo/backend/internal/websocket"
)

func main() {
	// Configuração de logging seguro
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)
	log.Println("Iniciando AMIGO Backend...")

	// Cria Hub de WebSocket
	hub := websocket.NewHub()
	go hub.Run()

	// Rotas
	http.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
		websocket.ServeWS(hub, w, r)
	})

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"healthy"}`))
	})

	// Porta
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Backend rodando na porta %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal("Erro ao iniciar servidor:", err)
	}
}
