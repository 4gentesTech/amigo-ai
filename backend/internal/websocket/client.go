package websocket

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/gorilla/websocket"
)

const (
	// Tempo para escrever mensagem
	writeWait = 10 * time.Second

	// Tempo para ler próxima mensagem
	pongWait = 60 * time.Second

	// Intervalo de ping
	pingPeriod = (pongWait * 9) / 10

	// Tamanho máximo de mensagem
	maxMessageSize = 2048
)

var (
	newline = []byte{'\n'}
	space   = []byte{' '}
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		// Em produção, validar origem
		return true
	},
}

// Client representa um cliente WebSocket
type Client struct {
	hub  *Hub
	conn *websocket.Conn
	send chan []byte
}

// Message representa a estrutura de mensagem do contrato
type Message struct {
	Type      string                 `json:"type"`
	SessionID string                 `json:"session_id"`
	Content   string                 `json:"content"`
	Timestamp string                 `json:"timestamp"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
}

// readPump lê mensagens do WebSocket
func (c *Client) readPump() {
	defer func() {
		c.hub.unregister <- c
		c.conn.Close()
	}()

	c.conn.SetReadDeadline(time.Now().Add(pongWait))
	c.conn.SetReadLimit(maxMessageSize)
	c.conn.SetPongHandler(func(string) error {
		c.conn.SetReadDeadline(time.Now().Add(pongWait))
		return nil
	})

	for {
		_, message, err := c.conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("Erro de leitura: %v", err)
			}
			break
		}

		message = bytes.TrimSpace(bytes.Replace(message, newline, space, -1))

		// Parse da mensagem
		var msg Message
		if err := json.Unmarshal(message, &msg); err != nil {
			log.Printf("Erro ao parsear mensagem: %v", err)
			continue
		}

		// Log seguro: apenas session_id e tipo
		log.Printf("Mensagem recebida - SessionID: %s, Type: %s", msg.SessionID, msg.Type)

		// Processa mensagem (aqui seria a integração com Agent/Redis)
		// Por enquanto, apenas echo
		c.hub.broadcast <- message
	}
}

// writePump envia mensagens para o WebSocket
func (c *Client) writePump() {
	ticker := time.NewTicker(pingPeriod)
	defer func() {
		ticker.Stop()
		c.conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.send:
			c.conn.SetWriteDeadline(time.Now().Add(writeWait))
			if !ok {
				c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			w, err := c.conn.NextWriter(websocket.TextMessage)
			if err != nil {
				return
			}
			w.Write(message)

			// Adiciona mensagens enfileiradas
			n := len(c.send)
			for i := 0; i < n; i++ {
				w.Write(newline)
				w.Write(<-c.send)
			}

			if err := w.Close(); err != nil {
				return
			}

		case <-ticker.C:
			c.conn.SetWriteDeadline(time.Now().Add(writeWait))
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

// ServeWS lida com requisições WebSocket
func ServeWS(hub *Hub, w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Erro ao fazer upgrade:", err)
		return
	}

	client := &Client{hub: hub, conn: conn, send: make(chan []byte, 256)}
	client.hub.register <- client

	// Inicia goroutines
	go client.writePump()
	go client.readPump()
}
