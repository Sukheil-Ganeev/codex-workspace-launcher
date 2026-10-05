# Cheatsheet — error-handling-patterns

## Выбор стратегии обработки ошибок
| Тип ошибки | Стратегия | Пример |
|------------|-----------|--------|
| Невалидный ввод | Fail fast + Result type | Ошибка валидации формы |
| Ресурс не найден | Return Result/Optional | 404 в API |
| Сетевой таймаут | Retry + backoff | HTTP 503, connection refused |
| Сервис недоступен | Circuit Breaker + fallback | Внешний API лежит |
| Нарушение бизнес-правила | Domain exception | Недостаточно средств |
| Programming bug | Crash / panic | Null pointer, index out of bounds |
| Нехватка ресурсов | Graceful shutdown | Out of memory, disk full |

## Паттерны по языкам

### JavaScript / TypeScript
```typescript
// Кастомная ошибка
class AppError extends Error {
  constructor(message: string, public code: string, options?: ErrorOptions) {
    super(message, options);
    this.name = 'AppError';
  }
}

// Result type
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

// Async error boundary
async function safeFetch<T>(fn: () => Promise<T>): Promise<Result<T>> {
  try {
    return { ok: true, value: await fn() };
  } catch (error) {
    return { ok: false, error: error as Error };
  }
}
```

### Python
```python
# Кастомная ошибка с контекстом
class AppError(Exception):
    def __init__(self, message, code=None, context=None):
        super().__init__(message)
        self.code = code
        self.context = context or {}

# Chaining
try:
    db.query(sql)
except DatabaseError as e:
    raise AppError("Query failed", code="DB_ERROR") from e

# Context manager для cleanup
@contextmanager
def managed_resource(name):
    resource = acquire(name)
    try:
        yield resource
    except Exception:
        resource.rollback()
        raise
    finally:
        resource.close()
```

### Go
```go
// Sentinel errors
var ErrNotFound = errors.New("not found")
var ErrForbidden = errors.New("forbidden")

// Wrapping
if err != nil {
    return fmt.Errorf("fetching user %d: %w", id, err)
}

// Проверка типа
if errors.Is(err, ErrNotFound) { /* 404 */ }

// Custom error type
type ValidationError struct {
    Field   string
    Message string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}
```

### Rust
```rust
// Result + ? operator
fn read_config(path: &str) -> Result<Config, AppError> {
    let content = fs::read_to_string(path)?;
    let config: Config = serde_json::from_str(&content)?;
    Ok(config)
}

// Custom error enum
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("Not found: {0}")]
    NotFound(String),
    #[error("Validation: {field} - {message}")]
    Validation { field: String, message: String },
    #[error(transparent)]
    Io(#[from] std::io::Error),
}
```

## Retry с exponential backoff
```
Попытка 1: delay = 100ms + jitter
Попытка 2: delay = 200ms + jitter
Попытка 3: delay = 400ms + jitter
Попытка 4: delay = 800ms + jitter
Попытка 5: delay = 1600ms + jitter (max)

jitter = random(0, delay * 0.5)
```

## Circuit Breaker — параметры
| Параметр | Типичное значение | Описание |
|----------|-------------------|----------|
| failureThreshold | 5 | Ошибок до размыкания |
| successThreshold | 3 | Успехов для закрытия |
| timeout | 30s | Время в состоянии Open |
| halfOpenRequests | 1 | Пробных запросов |
| monitorWindow | 60s | Окно подсчёта ошибок |

## Уровни логирования ошибок
| Уровень | Когда использовать | Пример |
|---------|-------------------|--------|
| FATAL | Приложение не может продолжить | Нет подключения к БД при старте |
| ERROR | Операция провалилась, нужна реакция | Необработанное исключение |
| WARN | Подозрительно, но обработано | Retry succeeded, fallback |
| INFO | Ожидаемая бизнес-ошибка | Невалидный ввод, 404 |
| DEBUG | Детали для разработчика | Стэктрейс retry, request body |

## Антипаттерны (НЕ делать)
| Антипаттерн | Почему плохо | Как правильно |
|-------------|-------------|---------------|
| `catch(e) {}` | Проглатывает ошибку | Логировать или пробросить |
| `catch(Exception e)` вверху | Ловит всё подряд | Ловить конкретные типы |
| `throw new Error("error")` | Неинформативно | Код + контекст + причина |
| Retry без backoff | Retry storm | Exponential backoff + jitter |
| Return null вместо ошибки | Скрытый NullPointer позже | Result/Optional type |
| Логировать + пробросить | Дублирование в логах | Одно из двух |
