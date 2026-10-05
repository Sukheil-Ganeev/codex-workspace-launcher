# Abaya Bot — Опыт реализации Волн 6-7

## Дата: 2026-03-01
## Контекст: Реализация Wave 6 (Admin & Management) + Wave 7 (External Integrations)

## Ключевые уроки

### 1. Subagent-Driven Development работает отлично для больших волн
- 9 фич за одну сессию (4 + 5), 233 новых теста
- Каждая задача = отдельный субагент с полным контекстом из плана
- Spec review после каждой задачи ловит проблемы рано
- Главное окно остаётся диспетчером — не читает большие файлы

### 2. Порядок задач критичен
- Всегда начинать с Prisma миграций (фундамент для всех фич)
- Сервисы перед flows (flows зависят от сервисов)
- Backend API перед frontend (Next.js зависит от REST endpoints)
- Простые фичи первыми (Video Preview = 8 тестов, быстрая победа)

### 3. API contract mismatches — главный риск при разделении frontend/backend
- Backend возвращает `{ data: ..., pagination: { page, limit, total } }`
- Frontend ожидает `{ data: ..., total, page, totalPages }`
- Login: backend `{ data: { token } }` vs frontend `{ token }`
- Решение: `fetchPaginated<T>()` helper + автоматический unwrap в fetchApi

### 4. bcrypt salt rounds: 12 в production, 4 в тестах
- bcrypt.hash с rounds=12 занимает >5 секунд
- Vitest default timeout = 5000ms → тесты падают по таймауту
- Решение: использовать rounds=4 в тестах

### 5. Fire-and-forget pattern для non-critical operations
- Journey tracking: `.catch(() => {})` — никогда не ломает основной flow
- Funnel event logging: try/catch + ignore errors
- Tracking updates: graceful degradation при недоступности API

### 6. Channel Adapter Pattern для омниканальности
- MessageSender interface: sendText, sendImage, sendButtons, sendList, sendVideo
- whatsappSender и instagramSender реализуют один интерфейс
- Instagram ограничения: text menus вместо lists, quick replies (макс 13) вместо buttons
- FSM и flow handlers работают без изменений

### 7. Mock mode для всех внешних API
- BNPL (Tabby/Tamara): mock response когда нет API key
- Tracking (Aramex/DHL): mock tracking data
- Instagram sender: log messages + return mock IDs
- Позволяет разрабатывать и тестировать без реальных аккаунтов

### 8. Периодические jobs — простой setInterval
- Daily snapshot: 24h interval
- Tracking checker: 2h interval
- Broadcast executor: 5min interval
- Flash sale checker: 60s interval (из Wave 4)
- Все очищаются в onClose hook

## Паттерны кода

### Singleton service
```typescript
export class MyService {
  async method(): Promise<void> { ... }
}
export const myService = new MyService();
```

### Admin route registration
```typescript
app.register(async (app) => {
  app.get('/endpoint', { preHandler: [authMiddleware] }, handler);
  app.post('/endpoint', { preHandler: [authMiddleware, requireRole('admin', 'manager')] }, handler);
}, { prefix: '/api/admin' });
```

### Pagination response
```typescript
reply.send({
  data: items,
  pagination: { page, limit, total }
});
```

## Статистика сессии
- Волна 6: 4 фичи, ~123 теста, 3 новые модели
- Волна 7: 5 фич, ~110 тестов, 2 новые модели
- Итого: 9 фич, 233 теста, 5 моделей
- Финальный проект: 2,607 тестов, 64 файла, 21 модель, 29 сервисов
