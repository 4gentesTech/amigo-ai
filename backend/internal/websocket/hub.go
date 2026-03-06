package websocket

import (
	"log"
)

// Hub mantém conexões ativas e broadcast de mensagens
type Hub struct {
	// Clientes registrados
	clients map[*Client]bool

	// Mensagens de broadcast
	broadcast chan []byte

	// Registro de novos clientes
	register chan *Client

	// Desregistro de clientes
	unregister chan *Client
}

// NewHub cria uma nova instância do Hub
func NewHub() *Hub {
	return &Hub{
		broadcast:  make(chan []byte),
		register:   make(chan *Client),
		unregister: make(chan *Client),
		clients:    make(map[*Client]bool),
	}
}

// Run inicia o loop principal do Hub
func (h *Hub) Run() {
	for {
		select {
		case client := <-h.register:
			h.clients[client] = true
			// Log seguro: apenas contagem, sem dados do cliente
			log.Printf("Cliente registrado. Total: %d", len(h.clients))

		case client := <-h.unregister:
			if _, ok := h.clients[client]; ok {
				delete(h.clients, client)
				close(client.send)
				log.Printf("Cliente desregistrado. Total: %d", len(h.clients))
			}

		case message := <-h.broadcast:
			// Broadcast para todos os clientes
			// IMPORTANTE: Não loga o conteúdo da mensagem
			for client := range h.clients {
				select {
				case client.send <- message:
				default:
					close(client.send)
					delete(h.clients, client)
				}
			}
		}
	}
}
