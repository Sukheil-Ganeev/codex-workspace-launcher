# EXP-079: Test Checklist Slides — фазовая группировка и цветные номера шагов

## Проблема
Слайды с тест-чеклистами выглядели как плоский список пунктов без визуальной иерархии. Сложно понять, к какой фазе относится шаг, и отследить прогресс.

## Решение: Фазовая группировка + цветные номера

### Структура слайда
```html
<div class="slide">
  <h2>Чек-лист тестирования</h2>

  <!-- Фаза 1 -->
  <div class="test-phase">
    <div class="phase-header">
      <span class="phase-number" style="background: linear-gradient(135deg, #F59E0B, #FBBF24);">1</span>
      <h3>Подготовка окружения</h3>
    </div>
    <div class="checklist-items">
      <div class="checklist-item">
        <span class="step-number step-amber">1.1</span>
        <span>Установить зависимости</span>
      </div>
      <div class="checklist-item">
        <span class="step-number step-amber">1.2</span>
        <span>Настроить переменные окружения</span>
      </div>
    </div>
  </div>

  <!-- Фаза 2 -->
  <div class="test-phase">
    <div class="phase-header">
      <span class="phase-number" style="background: linear-gradient(135deg, #3B82F6, #60A5FA);">2</span>
      <h3>Функциональное тестирование</h3>
    </div>
    <!-- ... -->
  </div>
</div>
```

### CSS
```css
.test-phase {
  margin-bottom: 20px;
}

.phase-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.phase-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 800;
  color: #000;
  flex-shrink: 0;
}

.checklist-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 44px; /* выравнивание под текст заголовка */
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  background: rgba(255,255,255,0.03);
  border-radius: 8px;
  border-left: 3px solid transparent;
}

.step-number {
  font-size: 13px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  min-width: 32px;
}

/* Цвета по фазам */
.step-amber { color: #F59E0B; }
.checklist-item:has(.step-amber) { border-left-color: rgba(245,158,11,0.4); }

.step-blue { color: #3B82F6; }
.checklist-item:has(.step-blue) { border-left-color: rgba(59,130,246,0.4); }

.step-green { color: #10B981; }
.checklist-item:has(.step-green) { border-left-color: rgba(16,185,129,0.4); }

.step-purple { color: #8B5CF6; }
.checklist-item:has(.step-purple) { border-left-color: rgba(139,92,246,0.4); }
```

## Цветовая схема фаз

| Фаза | Цвет | Назначение |
|------|-------|-----------|
| 1 | Amber (#F59E0B) | Подготовка / Setup |
| 2 | Blue (#3B82F6) | Основное тестирование |
| 3 | Green (#10B981) | Валидация / Проверка |
| 4 | Purple (#8B5CF6) | Деплой / Финализация |
| 5 | Red (#EF4444) | Откат / Ошибки |

## Ключевые принципы
1. **Фазовая группировка** — шаги объединяются в логические блоки (setup, test, validate, deploy)
2. **Цветные номера фаз** — круглый бейдж с gradient background, цвет = тип фазы
3. **Цветные номера шагов** — дробная нумерация (1.1, 1.2, 2.1), цвет совпадает с фазой
4. **Left border accent** — каждый checklist-item имеет цветную левую рамку по фазе
5. **padding-left: 44px** — выравнивает items под текст заголовка (мимо phase-number)
6. **tabular-nums** — номера шагов одинаковой ширины для ровного выравнивания
7. **:has() селектор** — автоматический цвет border-left по классу step-number (fallback: inline style)

## Когда использовать
- Пошаговые инструкции по тестированию
- Deployment checklists
- Onboarding процедуры
- Любые многофазные процессы с последовательными шагами

## Тэги
#pattern #checklist #test #phases #colors #css
