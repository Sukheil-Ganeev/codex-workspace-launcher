# EXP-029: Тёплые light-терминалы вместо тёмных на светлой теме

## Проблема

Тёмные терминалы (#1E1E2E) на светлом фоне (#FAFAF8) создают визуальный "шок" — глаз прыгает между двумя крайними уровнями яркости. Терминалы доминируют на слайде, забирая всё внимание.

## Решение

Warm light терминалы:

```css
.term {
  background: #FDFCF9;           /* Тёплый белый */
  border: 2px solid rgba(0,0,0,0.13);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.06);
}
.term-bar {
  background: #F5F2ED;           /* Кремовая полоса сверху */
  padding: 12px 18px;
  border-bottom: 1px solid rgba(0,0,0,0.07);
}
.term-body {
  padding: 24px 28px;
  font-family: monospace;
  font-size: 16px;               /* Крупнее чем на тёмной теме! */
  line-height: 1.75;
  color: #1B1B1B;                /* Тёмный текст на светлом */
}
```

Цветовая схема syntax highlighting для light:
```css
.term-body .prompt  { color: var(--green); }   /* $ или You: */
.term-body .command { color: var(--blue); }    /* Команды */
.term-body .highlight { color: var(--claude); } /* Акцент */
.term-body .success { color: var(--green); }   /* ✓ */
.term-body .dimmed  { color: #999; }           /* Второстепенное */
```

## Code-блоки (не терминалы)

Та же логика — тёплый cream фон вместо тёмного:
```css
.code {
  background: #FAF8F5;
  border: 1.5px solid rgba(0,0,0,0.13);
  border-radius: 14px;
  font-size: 16px;
  color: #1B1B1B;
}
/* Syntax: используй цвета из палитры темы */
.code .keyword  { color: var(--purple); }
.code .string   { color: var(--green); }
.code .number   { color: var(--claude); }
.code .function { color: var(--blue); }
.code .comment  { color: #8A8A8A; }
```

## Когда применять

- **Всегда** на светлых темах — терминалы должны интегрироваться, а не выпадать
- На тёмных темах — тёмные терминалы нормально (тот же уровень яркости)

## Контекст

- **Сессия:** 2026-02-06
- **Фидбек:** "терминалы слишком выделяются и всё мелко"
- **Решение:** Warm light terminals + увеличение шрифтов на 20%
