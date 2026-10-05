---
id: EXP-004
date: 2026-02-17
type: improvement
severity: medium
tags: [model-runner, ai, llm, compose]
---

## Паттерн

Docker Model Runner -- локальный запуск LLM через Docker Desktop.

## Когда использовать

Когда нужно запустить локальную LLM-модель (llama, phi, mistral) без внешних зависимостей. Полезно для: AI-ботов, RAG-пайплайнов, тестирования промптов.

## Решение

Model Runner: Beta с Desktop 4.40 (апрель 2025), GA к февралю 2026.
- API совместим с OpenAI (`/v1/chat/completions`)
- Интеграция с Compose: `provider.type: model` (Compose v2.35+)
- Поддержка GPU (NVIDIA, Apple Silicon)

```yaml
# compose.yaml
services:
  ai:
    provider:
      type: model
      options:
        model: ai/llama3.2
```

## Урок

AI-интеграции Docker -- быстро развивающаяся область. При обновлении справочника всегда проверять: Model Runner, MCP Toolkit, Docker AI Agent.
