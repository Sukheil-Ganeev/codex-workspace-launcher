# CRM Dashboard - Простой CRM дашборд

SPA приложение для управления заявками с клиентов (React или Vanilla JS).

## Описание

Минималистичный CRM для отслеживания заявок на туры. Данные хранятся в Google Sheets, интерфейс - SPA на Netlify.

**Идеально для:** внутреннего использования, учёта заявок, статистики продаж.

## Структура проекта

```
crm-dashboard/
├── index.html                    # Дашборд интерфейс
├── app.js                        # Логика приложения
├── style.css                     # Стили
├── netlify.toml                  # Конфигурация с SPA routing
└── netlify/functions/
    ├── get-leads.js              # Получение заявок из Google Sheets
    └── update-lead.js            # Обновление статуса заявки
```

## Возможности

- Просмотр всех заявок
- Фильтрация по статусу (новая, в работе, закрыта)
- Изменение статуса заявки
- Добавление комментариев
- Базовая статистика

## Шаг 1: Настройка Google Sheets

### Структура таблицы "Leads"

| ID | Дата | Имя | Телефон | Email | Тур | Статус | Комментарий |
|----|------|-----|---------|-------|-----|--------|-------------|
| 1 | 2024-01-15 | Иван | +971501234567 | ivan@mail.ru | Сафари | Новая | |
| 2 | 2024-01-16 | Мария | +971509876543 | maria@mail.com | Бурдж Халифа | В работе | Перезвонить завтра |

1. Создайте Google Sheet
2. Сделайте публичной для просмотра
3. Получите Sheet ID

## Шаг 2: Создайте файлы

### index.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CRM - Управление заявками</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <header>
      <h1>📊 CRM Dashboard</h1>
      <div class="stats">
        <div class="stat-card">
          <div class="stat-number" id="totalLeads">0</div>
          <div class="stat-label">Всего заявок</div>
        </div>
        <div class="stat-card">
          <div class="stat-number" id="newLeads">0</div>
          <div class="stat-label">Новые</div>
        </div>
        <div class="stat-card">
          <div class="stat-number" id="inProgressLeads">0</div>
          <div class="stat-label">В работе</div>
        </div>
      </div>
    </header>

    <div class="filters">
      <button class="filter-btn active" data-status="all">Все</button>
      <button class="filter-btn" data-status="Новая">Новые</button>
      <button class="filter-btn" data-status="В работе">В работе</button>
      <button class="filter-btn" data-status="Закрыта">Закрытые</button>
    </div>

    <div id="leadsContainer" class="leads-container">
      <div class="loading">Загрузка заявок...</div>
    </div>
  </div>

  <script src="app.js"></script>
</body>
</html>
```

### app.js

```javascript
let allLeads = [];
let currentFilter = 'all';

// Загрузка заявок
async function loadLeads() {
  try {
    const response = await fetch('/.netlify/functions/get-leads');
    const result = await response.json();

    if (result.success) {
      allLeads = result.data;
      updateStats();
      displayLeads(currentFilter);
    } else {
      showError('Ошибка загрузки: ' + result.message);
    }
  } catch (error) {
    showError('Не удалось загрузить заявки: ' + error.message);
  }
}

// Обновление статистики
function updateStats() {
  document.getElementById('totalLeads').textContent = allLeads.length;
  document.getElementById('newLeads').textContent =
    allLeads.filter(l => l.Статус === 'Новая').length;
  document.getElementById('inProgressLeads').textContent =
    allLeads.filter(l => l.Статус === 'В работе').length;
}

// Отображение заявок
function displayLeads(status) {
  const container = document.getElementById('leadsContainer');

  const filteredLeads = status === 'all'
    ? allLeads
    : allLeads.filter(lead => lead.Статус === status);

  if (filteredLeads.length === 0) {
    container.innerHTML = '<div class="empty">Нет заявок</div>';
    return;
  }

  const html = filteredLeads.map(lead => `
    <div class="lead-card">
      <div class="lead-header">
        <div>
          <h3>${lead.Имя}</h3>
          <span class="lead-date">${lead.Дата}</span>
        </div>
        <span class="lead-status status-${lead.Статус.toLowerCase().replace(' ', '-')}">
          ${lead.Статус}
        </span>
      </div>
      <div class="lead-info">
        <div>📱 ${lead.Телефон}</div>
        <div>✉️ ${lead.Email || 'не указан'}</div>
        <div>🎯 ${lead.Тур}</div>
      </div>
      ${lead.Комментарий ? `<div class="lead-comment">${lead.Комментарий}</div>` : ''}
      <div class="lead-actions">
        <button onclick="changeStatus(${lead.ID}, 'В работе')">В работу</button>
        <button onclick="changeStatus(${lead.ID}, 'Закрыта')">Закрыть</button>
      </div>
    </div>
  `).join('');

  container.innerHTML = html;
}

// Изменение статуса
async function changeStatus(leadId, newStatus) {
  try {
    const response = await fetch('/.netlify/functions/update-lead', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: leadId, status: newStatus })
    });

    if (response.ok) {
      // Обновляем локально
      const lead = allLeads.find(l => l.ID == leadId);
      if (lead) lead.Статус = newStatus;
      updateStats();
      displayLeads(currentFilter);
    }
  } catch (error) {
    alert('Ошибка обновления: ' + error.message);
  }
}

// Фильтрация
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.status;
    displayLeads(currentFilter);
  });
});

function showError(message) {
  document.getElementById('leadsContainer').innerHTML =
    `<div class="error">${message}</div>`;
}

// Автообновление каждые 30 секунд
setInterval(loadLeads, 30000);

// Первоначальная загрузка
loadLeads();
```

### style.css

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f5f7fa;
  color: #333;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  background: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

h1 {
  margin-bottom: 20px;
  color: #1a73e8;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.stat-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #1a73e8;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.filter-btn {
  padding: 10px 20px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  border-color: #1a73e8;
}

.filter-btn.active {
  background: #1a73e8;
  color: white;
  border-color: #1a73e8;
}

.leads-container {
  display: grid;
  gap: 15px;
}

.lead-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.lead-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 15px;
}

.lead-header h3 {
  margin-bottom: 5px;
}

.lead-date {
  font-size: 14px;
  color: #666;
}

.lead-status {
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
}

.status-новая {
  background: #e3f2fd;
  color: #1976d2;
}

.status-в-работе {
  background: #fff3e0;
  color: #f57c00;
}

.status-закрыта {
  background: #e8f5e9;
  color: #388e3c;
}

.lead-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
  font-size: 14px;
}

.lead-comment {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
  margin-bottom: 15px;
}

.lead-actions {
  display: flex;
  gap: 10px;
}

.lead-actions button {
  padding: 8px 16px;
  border: none;
  background: #1a73e8;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.lead-actions button:hover {
  background: #1557b0;
}

.loading, .empty, .error {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
}

.error {
  color: #d32f2f;
}
```

### netlify.toml

```toml
[build]
  publish = "."
  functions = "netlify/functions"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### netlify/functions/get-leads.js

```javascript
exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
  };

  try {
    const apiKey = process.env.GOOGLE_API_KEY;
    const sheetId = process.env.SHEET_ID;
    const range = 'Leads!A:H';

    const url = `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/${range}?key=${apiKey}`;
    const response = await fetch(url);
    const data = await response.json();

    const rows = data.values;
    const headers_row = rows[0];
    const items = rows.slice(1).map(row => {
      const item = {};
      headers_row.forEach((header, index) => {
        item[header] = row[index] || '';
      });
      return item;
    });

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, data: items })
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ success: false, message: error.message })
    };
  }
};
```

## Шаг 3: Deploy

```bash
netlify init
netlify deploy --prod
```

Добавьте Environment Variables:
- `GOOGLE_API_KEY`
- `SHEET_ID`

## Шаг 4: Защита доступа (опционально)

Для защиты дашборда добавьте Basic Auth:

В `netlify.toml`:

```toml
[[headers]]
  for = "/*"
  [headers.values]
    Basic-Auth = "username:password"
```

Или используйте Netlify Identity для полноценной авторизации.

## Расширения

- Добавьте поиск по заявкам
- Экспорт в Excel
- Графики и аналитика
- Добавление новых заявок через интерфейс
- История изменений
- Роли пользователей

## Troubleshooting

**Заявки не загружаются:**
- Проверьте Google Sheets API настройки
- Проверьте формат таблицы
- Проверьте CORS headers
