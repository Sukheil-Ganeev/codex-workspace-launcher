# vercel.json — Полные примеры конфигурации

> Перенесено из SKILL.md секции 5, 7, 11 (FAQ #7)

## Полная структура базового файла

```json
{
  "version": 2,
  "name": "my-app",
  "builds": [],
  "routes": [],
  "redirects": [],
  "rewrites": [],
  "headers": [],
  "env": {},
  "build": {
    "env": {}
  }
}
```

---

## Redirects (301/302)

**Назначение:** Перенаправление пользователя на другой URL с изменением адресной строки.

```json
{
  "redirects": [
    {
      "source": "/old-page",
      "destination": "/new-page",
      "permanent": true
    },
    {
      "source": "/blog/:slug",
      "destination": "/news/:slug",
      "permanent": false
    },
    {
      "source": "/old-blog/:path*",
      "destination": "/blog/:path*",
      "permanent": true
    }
  ]
}
```

**Параметры:**
- `source`: Исходный путь (поддерживает wildcards)
- `destination`: Целевой путь
- `permanent`: `true` = 301 (постоянный), `false` = 302 (временный)

**Расширенные примеры:**
```json
{
  "redirects": [
    // Редирект на внешний сайт
    {
      "source": "/github",
      "destination": "https://github.com/username",
      "permanent": false
    },
    // Удаление trailing slash
    {
      "source": "/:path*\\/$",
      "destination": "/:path*",
      "permanent": true
    },
    // Локализация по заголовку Accept-Language
    {
      "source": "/",
      "has": [
        {
          "type": "header",
          "key": "accept-language",
          "value": "(?<lang>ru|en).*"
        }
      ],
      "destination": "/:lang",
      "permanent": false
    }
  ]
}
```

---

## Rewrites (внутренние)

**Назначение:** Проксирование запроса на другой URL БЕЗ изменения адресной строки.

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.example.com/:path*"
    },
    {
      "source": "/blog/:slug",
      "destination": "/blog/[slug]"
    }
  ]
}
```

**Расширенные примеры:**
```json
{
  "rewrites": [
    // Проксирование к внешнему API
    {
      "source": "/api/external/:endpoint*",
      "destination": "https://external-api.com/:endpoint*"
    },
    // SPA fallback
    {
      "source": "/((?!api|_next|static).*)",
      "destination": "/index.html"
    },
    // Микрофронтенды
    {
      "source": "/shop/:path*",
      "destination": "https://shop.example.com/:path*"
    }
  ]
}
```

---

## Headers

### Базовые security headers

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### CORS Headers для API

```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "Content-Type, Authorization"
        }
      ]
    }
  ]
}
```

### Полный набор Security Headers (рекомендуется для production)

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains"
        },
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ]
}
```

---

## Environment Variables в vercel.json

```json
{
  "env": {
    "API_URL": "https://api.example.com",
    "PUBLIC_KEY": "pk_test_123"
  },
  "build": {
    "env": {
      "BUILD_TIME_API_KEY": "@build-api-key"
    }
  }
}
```

**Важно:** Для секретов используйте Vercel Dashboard или CLI:
```bash
vercel env add SECRET_KEY
```

---

## Build Configuration

```json
{
  "build": {
    "env": {
      "NODE_VERSION": "18"
    }
  },
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "outputDirectory": "dist"
}
```

**Параметры:**
- `framework`: Автоопределение или ручная установка
- `buildCommand`: Команда сборки (переопределяет автоматическую)
- `devCommand`: Команда для локальной разработки
- `installCommand`: Команда установки зависимостей
- `outputDirectory`: Папка с результатом сборки

---

## Routes (устаревшее, используйте redirects/rewrites)

```json
{
  "routes": [
    {
      "src": "/api/hello",
      "dest": "/api/hello.js"
    }
  ]
}
```

---

## Примеры для разных типов проектов

### Статичный сайт

```json
{
  "redirects": [
    {
      "source": "/home",
      "destination": "/",
      "permanent": true
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### SPA (React/Vue)

```json
{
  "rewrites": [
    {
      "source": "/((?!api|_next|static|favicon.ico).*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### API Routes

```json
{
  "rewrites": [
    {
      "source": "/api/v1/:endpoint*",
      "destination": "/api/:endpoint*"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "Content-Type, Authorization"
        }
      ]
    }
  ]
}
```

### Next.js (minimal config)

```json
{
  "framework": "nextjs",
  "redirects": [
    {
      "source": "/old-path",
      "destination": "/new-path",
      "permanent": true
    }
  ]
}
```

**Важно:** Next.js проекты обычно НЕ требуют `vercel.json`, так как конфигурация делается в `next.config.js`.

---

## Редирект www <-> без www

### С www на без www (рекомендуется)
```json
{
  "redirects": [
    {
      "source": "/:path*",
      "has": [
        {
          "type": "host",
          "value": "www.example.com"
        }
      ],
      "destination": "https://example.com/:path*",
      "permanent": true
    }
  ]
}
```

### Без www на www
```json
{
  "redirects": [
    {
      "source": "/:path*",
      "has": [
        {
          "type": "host",
          "value": "example.com"
        }
      ],
      "destination": "https://www.example.com/:path*",
      "permanent": true
    }
  ]
}
```

---

## Настройка кэширования

```json
{
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

**Важно:** API routes НЕ кэшируются по умолчанию!
