/**
 * WebSocket Client Template
 * Шаблон для подключения к WebSocket серверу
 *
 * Использование в браузере или Node.js:
 *   node websocket_client.js
 *
 * Для Node.js установите: npm install ws
 */

// Для Node.js (в браузере WebSocket встроен)
const WebSocket = typeof window !== 'undefined' ? window.WebSocket : require('ws');

// ============= Configuration =============

const WS_URL = process.env.WS_URL || 'wss://api.example.com/ws';
const API_KEY = process.env.API_KEY || 'your_api_key';

// ============= WebSocket Client Class =============

class WebSocketClient {
    constructor(url, options = {}) {
        this.url = url;
        this.options = options;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
        this.reconnectDelay = options.reconnectDelay || 3000;
        this.handlers = new Map();
    }

    /**
     * Подключение к серверу
     */
    connect() {
        return new Promise((resolve, reject) => {
            console.log(`Connecting to ${this.url}...`);

            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;

                // Аутентификация после подключения
                if (this.options.apiKey) {
                    this.send({
                        type: 'auth',
                        api_key: this.options.apiKey
                    });
                }

                resolve();
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            };

            this.ws.onclose = (event) => {
                console.log(`WebSocket closed: ${event.code} ${event.reason}`);
                this.handleReconnect();
            };
        });
    }

    /**
     * Отправка сообщения
     */
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error('WebSocket not connected');
        }
    }

    /**
     * Обработка входящих сообщений
     */
    handleMessage(data) {
        const type = data.type;

        if (this.handlers.has(type)) {
            this.handlers.get(type)(data);
        } else if (this.handlers.has('*')) {
            this.handlers.get('*')(data);
        } else {
            console.log('Unhandled message:', data);
        }
    }

    /**
     * Регистрация обработчика
     */
    on(type, handler) {
        this.handlers.set(type, handler);
    }

    /**
     * Автоматическое переподключение
     */
    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

            setTimeout(() => {
                this.connect().catch(console.error);
            }, this.reconnectDelay);
        } else {
            console.error('Max reconnect attempts reached');
        }
    }

    /**
     * Закрытие соединения
     */
    close() {
        if (this.ws) {
            this.maxReconnectAttempts = 0; // Отключить автопереподключение
            this.ws.close();
        }
    }
}

// ============= Live Tracking Example =============

async function trackTransfer(transferId) {
    const client = new WebSocketClient(WS_URL, { apiKey: API_KEY });

    // Обработчики событий
    client.on('auth_success', (data) => {
        console.log('Authenticated successfully');

        // Подписаться на обновления трансфера
        client.send({
            type: 'subscribe',
            channel: 'transfer_tracking',
            transfer_id: transferId
        });
    });

    client.on('location_update', (data) => {
        console.log('Location update:', {
            lat: data.lat,
            lng: data.lng,
            speed: data.speed,
            eta_minutes: data.eta_minutes
        });

        // Обновить маркер на карте
        // updateMapMarker(data.lat, data.lng);
    });

    client.on('transfer_status', (data) => {
        console.log('Transfer status:', data.status);
        // arrived, in_progress, completed
    });

    client.on('eta_update', (data) => {
        console.log(`ETA: ${data.minutes} minutes`);
    });

    client.on('error', (data) => {
        console.error('Server error:', data.message);
    });

    // Подключиться
    await client.connect();

    return client;
}

// ============= Chat Example =============

async function connectToChat(roomId) {
    const client = new WebSocketClient(WS_URL, { apiKey: API_KEY });

    client.on('auth_success', () => {
        // Присоединиться к комнате
        client.send({
            type: 'join_room',
            room_id: roomId
        });
    });

    client.on('new_message', (data) => {
        console.log(`[${data.sender}]: ${data.text}`);

        // Отобразить сообщение в UI
        // displayMessage(data.sender, data.text, data.timestamp);
    });

    client.on('user_joined', (data) => {
        console.log(`${data.username} joined the chat`);
    });

    client.on('user_left', (data) => {
        console.log(`${data.username} left the chat`);
    });

    client.on('typing', (data) => {
        console.log(`${data.username} is typing...`);
    });

    await client.connect();

    // Функция отправки сообщения
    const sendMessage = (text) => {
        client.send({
            type: 'send_message',
            room_id: roomId,
            text: text
        });
    };

    // Функция показа "печатает..."
    const sendTyping = () => {
        client.send({
            type: 'typing',
            room_id: roomId
        });
    };

    return { client, sendMessage, sendTyping };
}

// ============= Main =============

async function main() {
    try {
        // Пример: отслеживание трансфера
        console.log('Starting transfer tracking...');
        const trackingClient = await trackTransfer('transfer-123');

        // Через 30 секунд закрыть
        setTimeout(() => {
            trackingClient.close();
            console.log('Tracking stopped');
        }, 30000);

    } catch (error) {
        console.error('Error:', error);
    }
}

// Export
module.exports = {
    WebSocketClient,
    trackTransfer,
    connectToChat
};

// Запуск если вызван напрямую
if (typeof require !== 'undefined' && require.main === module) {
    main();
}
