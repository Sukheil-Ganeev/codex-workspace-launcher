# Templates - HTML/CSS Шаблоны

Готовые HTML/CSS шаблоны для быстрого старта.

## Файлы

1. **landing-page.html** - Базовый лендинг с hero, features, CTA
2. **tour-card.html** - Карточка тура с hover эффектами  
3. **contact-form.html** - Контактная форма с HTML5 validation
4. **price-calculator.html** - Калькулятор с live расчётом
5. **booking-form.html** - Форма бронирования с date picker
6. **gallery.html** - Галерея с grid layout и lazy loading
7. **google-maps-integration.html** - Карта с маркерами
8. **sheets-api-integration.html** - Прайс-лист с Google Sheets API
9. **base-styles.css** - Базовые стили (CSS variables, reset)
10. **responsive-grid.css** - Адаптивная сетка

## Использование

### Плейсхолдеры для замены:

- {{TOUR_NAME}} - название тура
- {{TOUR_DESCRIPTION}} - описание
- {{PRICE}} - цена
- {{WEBHOOK_URL}} - URL вебхука
- {{API_KEY}} - Google API ключ

### Пример:

```bash
# Скопировать шаблон
cp landing-page.html my-tour.html

# Заменить плейсхолдеры
sed -i 's/{{TOUR_NAME}}/Desert Safari/g' my-tour.html
```
