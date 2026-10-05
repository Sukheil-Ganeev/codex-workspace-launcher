/**
 * WebSocket Server Template
 *
 * Production-ready WebSocket сервер для real-time приложений:
 * - Chat, notifications
 * - Live updates
 * - Room management
 * - Error handling & reconnection
 *
 * @example
 * npm install express socket.io dotenv
 */

const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const jwt = require('jsonwebtoken');

const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
  cors: {
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    methods: ['GET', 'POST'],
  },
  // Heartbeat
  pingInterval: 25000,
  pingTimeout: 60000,
});

// ==================== AUTHENTICATION ====================

/**
 * Middleware для аутентификации WebSocket соединения
 */
io.use((socket, next) => {
  try {
    const token = socket.handshake.auth.token;

    if (!token) {
      return next(new Error('Authentication required'));
    }

    // TODO: Проверить JWT токен
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    socket.userId = decoded.sub;
    socket.userEmail = decoded.email;
    socket.userRole = decoded.role;

    console.log(`[WebSocket] User authenticated: ${socket.userId}`);
    next();
  } catch (error) {
    console.error('[WebSocket] Auth error:', error.message);
    next(new Error('Authentication failed'));
  }
});

// ==================== CONNECTION HANDLERS ====================

/**
 * Обработка нового соединения
 */
io.on('connection', (socket) => {
  console.log(`[WebSocket] Connected: ${socket.id} (User: ${socket.userId})`);

  // Хранить активных пользователей
  const onlineUsers = io.sockets.sockets.size;
  io.emit('users:count', { count: onlineUsers });

  // ================ ROOM MANAGEMENT ================

  /**
   * Присоединиться к комнате
   * @event room:join
   */
  socket.on('room:join', (data) => {
    const { roomId } = data;

    if (!roomId) {
      return socket.emit('error', 'Room ID is required');
    }

    socket.join(roomId);
    console.log(`[WebSocket] User ${socket.userId} joined room ${roomId}`);

    // Уведомить других в комнате
    socket.to(roomId).emit('user:joined', {
      userId: socket.userId,
      userEmail: socket.userEmail,
      timestamp: new Date().toISOString(),
    });
  });

  /**
   * Покинуть комнату
   * @event room:leave
   */
  socket.on('room:leave', (data) => {
    const { roomId } = data;

    socket.leave(roomId);
    console.log(`[WebSocket] User ${socket.userId} left room ${roomId}`);

    socket.to(roomId).emit('user:left', {
      userId: socket.userId,
      timestamp: new Date().toISOString(),
    });
  });

  // ================ MESSAGING ================

  /**
   * Отправить сообщение в комнату
   * @event message:send
   */
  socket.on('message:send', (data) => {
    try {
      const { roomId, text, type = 'text' } = data;

      if (!roomId || !text) {
        return socket.emit('error', 'Room ID and message are required');
      }

      const message = {
        id: Date.now().toString(),
        userId: socket.userId,
        userEmail: socket.userEmail,
        text,
        type,
        timestamp: new Date().toISOString(),
      };

      // Отправить всем в комнате (включая отправителя)
      io.to(roomId).emit('message:receive', message);

      // TODO: Сохранить в БД для истории
      console.log(`[Message] ${socket.userId} -> ${roomId}: ${text}`);
    } catch (error) {
      socket.emit('error', error.message);
    }
  });

  /**
   * Печатает пользователь
   * @event user:typing
   */
  socket.on('user:typing', (data) => {
    const { roomId } = data;

    socket.to(roomId).emit('user:typing', {
      userId: socket.userId,
      userEmail: socket.userEmail,
    });
  });

  /**
   * Перестал печатать
   * @event user:stop-typing
   */
  socket.on('user:stop-typing', (data) => {
    const { roomId } = data;

    socket.to(roomId).emit('user:stop-typing', {
      userId: socket.userId,
    });
  });

  // ================ NOTIFICATIONS ================

  /**
   * Отправить приватное уведомление
   * @event notification:send
   */
  socket.on('notification:send', (data) => {
    const { targetUserId, title, body } = data;

    // Найти все сокеты пользователя
    const targetSockets = io.sockets.sockets;

    for (const [, targetSocket] of targetSockets) {
      if (targetSocket.userId === targetUserId) {
        targetSocket.emit('notification:receive', {
          id: Date.now().toString(),
          title,
          body,
          timestamp: new Date().toISOString(),
        });
        break;
      }
    }
  });

  // ================ REAL-TIME DATA ================

  /**
   * Обновление статуса
   * @event status:update
   */
  socket.on('status:update', (data) => {
    const { status } = data;

    socket.broadcast.emit('user:status', {
      userId: socket.userId,
      status,
    });
  });

  // ================ PRESENCE ================

  /**
   * Получить список активных пользователей в комнате
   * @event room:users
   */
  socket.on('room:users', (data) => {
    const { roomId } = data;

    const room = io.sockets.adapter.rooms.get(roomId);
    const userIds = Array.from(room || []).map((socketId) => {
      const s = io.sockets.sockets.get(socketId);
      return {
        userId: s.userId,
        userEmail: s.userEmail,
        socketId,
      };
    });

    socket.emit('room:users', { roomId, users: userIds });
  });

  // ================ DISCONNECTION ================

  /**
   * Обработка разрыва соединения
   */
  socket.on('disconnect', (reason) => {
    console.log(`[WebSocket] Disconnected: ${socket.id} (${reason})`);

    // Уведомить всех об отключении
    io.emit('user:offline', {
      userId: socket.userId,
      timestamp: new Date().toISOString(),
    });

    const onlineUsers = io.sockets.sockets.size;
    io.emit('users:count', { count: onlineUsers });
  });

  /**
   * Обработка ошибок соединения
   */
  socket.on('error', (error) => {
    console.error(`[WebSocket] Error ${socket.id}:`, error);
  });
});

// ==================== BROADCASTING ====================

/**
 * Функция для отправки уведомления всем пользователям
 *
 * @param {string} event - Название события
 * @param {Object} data - Данные события
 *
 * @example
 * broadcastToAll('notification', { title: 'System', body: 'Maintenance' });
 */
function broadcastToAll(event, data) {
  io.emit(event, {
    ...data,
    timestamp: new Date().toISOString(),
  });
}

/**
 * Отправить уведомление в комнату
 *
 * @param {string} roomId
 * @param {string} event
 * @param {Object} data
 */
function broadcastToRoom(roomId, event, data) {
  io.to(roomId).emit(event, {
    ...data,
    timestamp: new Date().toISOString(),
  });
}

// ==================== HTTP ROUTES ====================

app.get('/health', (req, res) => {
  const stats = {
    connectedClients: io.sockets.sockets.size,
    connectedNamespaces: Object.keys(io.nsps).length,
  };

  res.json({ status: 'healthy', socket: stats });
});

// ==================== SERVER START ====================

const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
  console.log(`[WebSocket] Server running on port ${PORT}`);
});

module.exports = { io, server, broadcastToAll, broadcastToRoom };

// Required environment variables:
// PORT=3000
// JWT_SECRET=your-secret-key
// ALLOWED_ORIGINS=http://localhost:3000,https://example.com
