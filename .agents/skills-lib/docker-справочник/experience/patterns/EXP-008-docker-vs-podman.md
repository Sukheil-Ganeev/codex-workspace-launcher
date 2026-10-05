---
id: EXP-008
date: 2026-02-17
type: pattern
severity: low
tags: [podman, containerd, nerdctl, alternatives]
---

## Паттерн

Сравнение Docker с альтернативами -- частый вопрос в FAQ.

## Когда использовать

Когда спрашивают: "Какие альтернативы Docker?", "Стоит ли переходить на Podman?", "Что лучше для Kubernetes?"

## Правильный способ

| Критерий | Docker | Podman | containerd+nerdctl |
|----------|--------|--------|-------------------|
| Daemon | dockerd (daemon) | Нет (daemonless) | containerd |
| Rootless | Да (с Engine 27+) | По умолчанию | Да |
| Kubernetes | Нет (но Docker Desktop) | Да (CRI) | Да (CRI) |
| Compose | Встроен (v2/v5) | podman-compose | nerdctl compose |
| Desktop GUI | Docker Desktop ($) | Podman Desktop (free) | Нет |
| Экосистема | Крупнейшая (Hub, Scout, Build Cloud) | Растущая | Минимальная |
| Лицензия | Freemium (Engine=free, Desktop=paid >250 чел.) | Apache 2.0 | Apache 2.0 |

## Урок

Docker остаётся стандартом для разработки. Podman -- для корпораций избегающих лицензии Docker Desktop. containerd+nerdctl -- для минималистов и K8s-first окружений. Для большинства проектов Docker -- оптимальный выбор.
