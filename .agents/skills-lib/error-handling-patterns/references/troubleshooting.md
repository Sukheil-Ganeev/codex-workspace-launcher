# Troubleshooting — error-handling-patterns

## Проблема 1: Проглоченные ошибки (swallowed errors)
**Симптом:** Приложение молча ломается, данные теряются, но логи чистые. Пустые catch-блоки или `catch(e) {}`.
**Решение:** Ввести линтер-правило запрещающее пустые catch (ESLint `no-empty`, Clippy). Минимум — логировать ошибку. Установить глобальный обработчик необработанных исключений (`process.on('unhandledRejection')`, `Thread.setDefaultUncaughtExceptionHandler`). Провести аудит: `grep -r "catch" --include="*.ts" | grep -v "log\|throw\|return"`.

## Проблема 2: Потеря стэктрейса при перебросе ошибки
**Симптом:** В логах видно только обёртку ошибки, но не оригинальную причину. Невозможно найти root cause.
**Решение:** Всегда сохранять оригинальную ошибку как `cause`:
- JS/TS: `throw new AppError("msg", { cause: originalError })`
- Python: `raise AppError("msg") from original_error`
- Java: `throw new AppException("msg", originalException)`
- Go: `fmt.Errorf("context: %w", err)` (wrapping с `%w`)

## Проблема 3: Утечка внутренних деталей клиенту
**Симптом:** API возвращает стэктрейсы, имена таблиц БД, внутренние пути файлов в ответах ошибок. Уязвимость безопасности.
**Решение:** Разделить внутренние и внешние сообщения об ошибках. Внутренние — в логи (полный стэктрейс, SQL-запрос, параметры). Внешние — клиенту (общее описание + error code для поддержки). В production отключить debug-mode, stack-trace в ответах. Middleware-слой для маппинга внутренних ошибок в HTTP-ответы.

## Проблема 4: Каскадные сбои при отказе внешнего сервиса
**Симптом:** Один микросервис упал — через минуту лежит всё. Thread pool exhaustion, таймаут накапливается.
**Решение:** Реализовать Circuit Breaker (Resilience4j, Polly, opossum). Установить агрессивные таймауты (не дефолтные 30с, а 2-5с). Добавить bulkhead (изоляция thread pools). Реализовать fallback: кэшированные данные, дефолтные значения, деградированный режим. Health check с быстрым обнаружением.

## Проблема 5: Неотловленные ошибки в async-коде
**Симптом:** Promise rejection не обработан, async callback бросает исключение — приложение крашится или зависает.
**Решение:**
- Node.js: `process.on('unhandledRejection', handler)` + всегда await или .catch()
- Python: `loop.set_exception_handler()` + `await` для всех корутин
- Линтер: `@typescript-eslint/no-floating-promises`, `require-await`
- Паттерн: оборачивать все async entry points в try-catch на верхнем уровне

## Проблема 6: Retry storm (шторм повторов)
**Симптом:** Сервис перегружен, все клиенты одновременно ретраят, нагрузка растёт ещё больше вместо снижения.
**Решение:** Exponential backoff с jitter (случайная задержка): `delay = min(base * 2^attempt + random(0, base), maxDelay)`. Ограничить максимум попыток (3-5). Добавить Circuit Breaker на клиентской стороне. Серверу возвращать `Retry-After` header с рекомендованной задержкой.
