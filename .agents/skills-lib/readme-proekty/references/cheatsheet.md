# Шпаргалка: README элементы

## Badges (shields.io)

### Формат
```
![Label](https://img.shields.io/badge/LABEL-VALUE-COLOR?logo=LOGO&logoColor=white)
```

### Цвета
| Цвет | Код | Использование |
|------|-----|---------------|
| brightgreen | `brightgreen` | Статус OK, тесты проходят |
| green | `green` | Активный, поддерживается |
| yellow | `yellow` | Лицензия, предупреждение |
| orange | `orange` | Beta, эксперимент |
| red | `red` | Deprecated, ошибка |
| blue | `blue` | Информация, версия |
| 3776AB | `3776AB` | Python (фирменный цвет) |
| 2CA5E0 | `2CA5E0` | Telegram |
| 25D366 | `25D366` | WhatsApp |
| 009688 | `009688` | FastAPI |

### Популярные логотипы
python, javascript, typescript, react, vue, angular, nodejs, go, rust, java, docker, kubernetes, postgresql, redis, mongodb, telegram, whatsapp, fastapi, flask, django, pytest, github, gitlab, aws, googlecloud, azure

### Примеры готовых badges
```markdown
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-24-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-passing-brightgreen?logo=pytest&logoColor=white)
![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)
```

## Mermaid диаграммы

### Flowchart (самая частая)
````markdown
```mermaid
flowchart TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```
````

### Sequence Diagram
````markdown
```mermaid
sequenceDiagram
    Client->>Bot: Voice message
    Bot->>Whisper: Transcribe
    Whisper-->>Bot: Text
    Bot->>Gemini: Summarize
    Gemini-->>Bot: Summary
    Bot->>Client: Result
```
````

### Subgraphs
````markdown
```mermaid
flowchart TD
    subgraph Frontend
        A[React] --> B[API Client]
    end
    subgraph Backend
        C[FastAPI] --> D[Database]
    end
    B --> C
```
````

## HTML в Markdown (GitHub поддерживает)

### Центрирование
```html
<div align="center">
  <h1>Title</h1>
  <p>Description</p>
</div>
```

### Collapsible
```html
<details>
<summary>Click to expand</summary>

Content here (need empty line after summary!)

</details>
```

### Back to top
```html
<p align="right"><a href="#readme-top">⬆ Back to top</a></p>
```

### Изображение с размером
```html
<img src="image.png" alt="Description" width="600">
```
