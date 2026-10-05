# EXP-107: Dark Mode -- контраст текста на цветных плашках

> Дата: 2026-02-14 | Категория: fix/warning | Проект: Taplink-презентация

## Проблема

В dark mode карточки с rgba-фонами (opacity 8-10%) становились нечитаемыми -- текст сливался с фоном. Особенно критично для:
- Карточки с цветными плашками (синий, зелёный, фиолетовый фон)
- Highlight-box элементы
- Таблицы с тонированными строками
- Теги и бейджи

## Причина

rgba opacity 8-10% создаёт еле заметный цвет на светлом фоне, но на тёмном фоне (#1a1a2e, #22223a) этого недостаточно -- цвет карточки не отличается от окружения, и текст теряет контраст.

## Решение

### Правило 1: Минимальный контраст WCAG AA 4.5:1

Все текстовые элементы должны иметь контраст минимум 4.5:1 относительно фона.

### Правило 2: Отдельный блок [data-theme="dark"] для КАЖДОГО типа элемента

```css
/* ===== LIGHT MODE (по умолчанию) ===== */
.card {
    background: rgba(59, 130, 246, 0.08);  /* Лёгкий синий тинт */
    color: #1e293b;
}

.highlight-box {
    background: rgba(16, 185, 129, 0.08);
    color: #1e293b;
}

.tag {
    background: rgba(139, 92, 246, 0.1);
    color: #6d28d9;
}

/* ===== DARK MODE ===== */
[data-theme="dark"] .card {
    background: #22223a;  /* Твёрдый тёмный фон, НЕ rgba! */
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

[data-theme="dark"] .highlight-box {
    background: rgba(16, 185, 129, 0.20);  /* Увеличить до 20-25% */
    color: #e2e8f0;
}

[data-theme="dark"] .tag {
    background: rgba(139, 92, 246, 0.22);  /* Увеличить до 20-25% */
    color: #c4b5fd;  /* Светлый вариант фиолетового */
}

/* Таблицы */
[data-theme="dark"] .styled-table th {
    background: rgba(59, 130, 246, 0.20);
    color: #e2e8f0;
}

[data-theme="dark"] .styled-table tr:nth-child(even) {
    background: rgba(255, 255, 255, 0.04);
}

[data-theme="dark"] .styled-table td {
    color: #cbd5e1;
    border-color: rgba(255, 255, 255, 0.06);
}

/* Блоки кода */
[data-theme="dark"] .code-block {
    background: #0f0f1e;
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

/* Highlight boxes / callouts */
[data-theme="dark"] .callout-info {
    background: rgba(59, 130, 246, 0.15);
    border-left: 3px solid #3b82f6;
    color: #e2e8f0;
}

[data-theme="dark"] .callout-warning {
    background: rgba(245, 158, 11, 0.15);
    border-left: 3px solid #f59e0b;
    color: #e2e8f0;
}

[data-theme="dark"] .callout-success {
    background: rgba(16, 185, 129, 0.15);
    border-left: 3px solid #10b981;
    color: #e2e8f0;
}
```

### Правило 3: Opacity шкала для dark mode

| Элемент | Light opacity | Dark opacity |
|---------|--------------|--------------|
| Карточка фон | 0.05-0.08 | 0.15-0.25 (или solid #22223a) |
| Тег/бейдж фон | 0.08-0.12 | 0.20-0.28 |
| Таблица заголовок | 0.08-0.12 | 0.18-0.25 |
| Таблица чётная строка | 0.03-0.05 | 0.04-0.06 |
| Бордеры | rgba(0,0,0,0.08) | rgba(255,255,255,0.08) |
| Тени | box-shadow с rgba | НЕ использовать (или минимальный) |

### Правило 4: Цвета текста для dark mode

```css
[data-theme="dark"] {
    /* Основные */
    --text-primary: #e2e8f0;     /* Основной текст */
    --text-secondary: #94a3b8;   /* Вторичный */
    --text-muted: #64748b;       /* Приглушённый */

    /* Акценты (светлые варианты) */
    --text-blue: #93c5fd;        /* Вместо #2563eb */
    --text-green: #6ee7b7;       /* Вместо #059669 */
    --text-purple: #c4b5fd;      /* Вместо #7c3aed */
    --text-orange: #fdba74;      /* Вместо #ea580c */
    --text-red: #fca5a5;         /* Вместо #dc2626 */
}
```

## Чеклист проверки dark mode

- [ ] Все карточки: фон различим от общего фона страницы
- [ ] Все тексты: контраст >= 4.5:1
- [ ] Заголовки: контраст >= 3:1 (крупный текст допускает 3:1)
- [ ] Теги/бейджи: текст читаемый на тёмном фоне бейджа
- [ ] Таблицы: строки различимы друг от друга
- [ ] Блоки кода: текст кода читаемый
- [ ] Бордеры: видимые, но не яркие
- [ ] Иконки/SVG: видимые (currentColor или явный цвет)

## Связанные записи

- EXP-092: rgba невидим на тёмном, gradient + border
- EXP-098: Purple-on-purple невидимый текст
- EXP-095: bg-glow opacity 0.30+ для видимости
