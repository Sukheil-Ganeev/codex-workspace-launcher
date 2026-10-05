# Улучшения визуального дизайна презентаций

**ID:** EXP-007, EXP-008
**Дата:** 2026-02-04
**Контекст:** Презентация Claude CLI

## 1. Визуальный мокап на титульном слайде (EXP-007)

### Проблема
Титульный слайд с только текстом (заголовок + подзаголовок) выглядит скучно и не привлекает внимание. Пустое пространство справа "тянет" слайд.

### Решение
Добавить интерактивный мокап терминала/интерфейса, демонстрирующий суть продукта.

### CSS для мокапа терминала

```css
.terminal-mock {
    background: #1e1e1e;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    font-family: 'Fira Code', 'SF Mono', monospace;
}

.terminal-header {
    background: #323232;
    padding: 12px 16px;
    display: flex;
    gap: 8px;
}

.terminal-header .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.terminal-header .dot.red { background: #ff5f56; }
.terminal-header .dot.yellow { background: #ffbd2e; }
.terminal-header .dot.green { background: #27ca40; }

.terminal-body {
    padding: 20px;
    font-size: 14px;
    line-height: 1.6;
    color: #e0e0e0;
}

.terminal-prompt {
    color: #4ade80;  /* зеленый для промпта */
}

.terminal-command {
    color: #60a5fa;  /* синий для команды */
}

.terminal-output {
    color: #a0a0a0;  /* серый для вывода */
    margin-left: 20px;
}
```

### HTML структура

```html
<div class="terminal-mock">
    <div class="terminal-header">
        <span class="dot red"></span>
        <span class="dot yellow"></span>
        <span class="dot green"></span>
    </div>
    <div class="terminal-body">
        <div class="line">
            <span class="terminal-prompt">$</span>
            <span class="terminal-command">claude --help</span>
        </div>
        <div class="terminal-output">
            Claude CLI v1.0.0<br>
            Usage: claude [command] [options]
        </div>
    </div>
</div>
```

### Эффект
- Сразу показывает суть продукта
- Заполняет пустое пространство
- Создает "wow"-эффект на первом слайде
- Помогает аудитории понять контекст

---

## 2. SVG иконки в заголовках секций (EXP-008)

### Проблема
Все заголовки секций выглядят одинаково - просто текст. Нет визуальной иерархии, сложно сканировать презентацию.

### Решение
Добавить иконки в градиентных контейнерах перед заголовками.

### CSS для иконок

```css
.section-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 30px;
}

.icon {
    width: 48px;
    height: 48px;
    min-width: 48px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.icon svg {
    width: 24px;
    height: 24px;
    fill: none;
    stroke: white;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
}
```

### HTML структура

```html
<div class="section-header">
    <span class="icon">
        <svg viewBox="0 0 24 24">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
        </svg>
    </span>
    <h2>Название секции</h2>
</div>
```

### Популярные SVG иконки (inline)

```html
<!-- Rocket / Запуск -->
<svg viewBox="0 0 24 24"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 00-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 012-3.95A12.88 12.88 0 0122 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 01-4 2z"/></svg>

<!-- Terminal / Терминал -->
<svg viewBox="0 0 24 24"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>

<!-- Layers / Слои -->
<svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>

<!-- Zap / Молния -->
<svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>

<!-- Settings / Настройки -->
<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>

<!-- Check Circle / Галочка -->
<svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
```

### Эффект
- Визуальная иерархия - легко сканировать
- Каждая секция имеет свою "личность"
- Градиент добавляет глубину
- Профессиональный внешний вид

---

## 3. Градиентная боковая полоса для command-boxes

### Проблема
Блоки команд/кода выглядят плоско.

### Решение

```css
.command-box {
    background: #1e293b;
    border-radius: 12px;
    padding: 20px 20px 20px 30px;
    position: relative;
    overflow: hidden;
}

.command-box::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}
```

### Эффект
- Визуальный акцент на блоке кода
- Соответствует общей цветовой схеме (градиент иконок)
- Добавляет глубину без перегрузки

---

## Связанные файлы

- `_index.md` — уроки #7, #8
- `patterns/css-compactification.md` — компактификация при переполнении
