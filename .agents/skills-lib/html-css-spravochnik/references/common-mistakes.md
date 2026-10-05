# Common Mistakes — Подробные примеры

Детальные примеры кода для типичных ошибок из SKILL.md (раздел 6, ошибки 7-10).

---

## Ошибка 7: Не используют CSS Grid/Flexbox

**Проблема:** Layouts через `float` и `position: absolute` из 2005 года.

```css
/* Старый подход (не используйте!) */
.card {
  float: left;
  width: 33.33%;
}
.clearfix::after {
  content: "";
  display: table;
  clear: both;
}
```

**Решение - Flexbox для одномерных layouts:**
```css
/* Навигация, ряд цен */
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

**Решение - Grid для двумерных layouts:**
```css
/* Галереи, карточки туров */
.tour-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}
```

**Примеры:** `assets/templates/responsive-grid.css`

---

## Ошибка 8: console.log в production

**Проблема:**
```javascript
async function loadPrices() {
  const data = await fetch('/api/prices').then(r => r.json());
  console.log('Debug info:', data); // Забыли убрать!
  return data;
}
```

**Почему плохо:**
- Замедляет код
- Показывает внутреннюю логику в консоли браузера
- Непрофессионально

**Решение - автоматическая проверка:**
```bash
node scripts/validate.js --js script.js

# Вывод:
# ❌ Remove console.log before production (line 45)
```

**Или использовать:**
```javascript
const DEBUG = false; // В production = false

function debug(...args) {
  if (DEBUG) console.log(...args);
}

debug('Это не попадёт в production');
```

---

## Ошибка 9: Нет loading состояний

**Проблема:**
Пользователь кликает "Отправить заявку" -> ничего не происходит визуально -> кликает ещё раз -> дубли заявок.

**Решение:**
```javascript
const button = document.querySelector('.submit-btn');

button.addEventListener('click', async () => {
  // 1. Показываем loading
  button.textContent = 'Отправка...';
  button.disabled = true;
  button.classList.add('loading');

  try {
    // 2. Отправляем запрос
    await fetch('/api/submit', {
      method: 'POST',
      body: JSON.stringify(formData)
    });

    // 3. Успех
    button.textContent = 'Отправлено ✓';
    button.classList.remove('loading');
    button.classList.add('success');
  } catch (error) {
    // 4. Ошибка
    button.textContent = 'Ошибка. Попробуйте снова';
    button.disabled = false;
    button.classList.remove('loading');
    button.classList.add('error');
  }
});
```

**CSS для loading:**
```css
.submit-btn.loading {
  cursor: wait;
  opacity: 0.6;
}
.submit-btn.loading::after {
  content: '';
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  animation: spin 0.6s linear infinite;
}
```

---

## Ошибка 10: Игнорируют Performance

**Проблема:** Сайт грузится 10+ секунд. Клиенты уходят.

**Решение - Lighthouse audit:**
```bash
# Chrome DevTools
# 1. Откройте сайт
# 2. F12 → Lighthouse tab
# 3. Generate report
# 4. Следуйте рекомендациям
```

**Типичные проблемы и решения:**

| Проблема | Решение | Выигрыш |
|----------|---------|---------|
| Большие изображения | `image-optimizer.js` | -80% размер |
| Неминифицированный CSS/JS | `minify.js` | -70% размер |
| Blocking scripts | `<script defer>` или `async` | -2s загрузка |
| Нет кеширования | Netlify/Vercel авто-кеш | -50% повторная загрузка |
| Нет lazy load | `loading="lazy"` на img | -40% initial load |

**Цель:** Lighthouse score > 90 (Performance, Accessibility, Best Practices, SEO)

**Детали:** `references/performance-optimization.md`
