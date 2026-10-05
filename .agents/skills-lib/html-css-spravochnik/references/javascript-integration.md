# JavaScript Integration Reference

Практическое руководство по интеграции JavaScript с HTML/CSS для создания интерактивных веб-приложений.

---

## 1. DOM Manipulation

### Выбор элементов

```javascript
// Один элемент (первый найденный)
const button = document.querySelector('.book-button');
const header = document.querySelector('#main-header');

// Все совпадающие элементы (NodeList)
const cards = document.querySelectorAll('.tour-card');
const inputs = document.querySelectorAll('input[required]');

// Перебор элементов
cards.forEach(card => {
  card.addEventListener('click', handleCardClick);
});

// Преобразование в массив для методов массивов
const cardArray = Array.from(cards);
const titles = cardArray.map(card => card.querySelector('h3').textContent);
```

### Изменение контента и стилей

```javascript
// Текстовый контент
button.textContent = 'Забронировать';
button.innerHTML = '<span>🎟️</span> Купить билет';

// CSS классы
button.classList.add('active');
button.classList.remove('disabled');
button.classList.toggle('expanded');
button.classList.contains('active'); // true/false

// Inline стили
card.style.backgroundColor = '#f0f0f0';
card.style.transform = 'translateY(-10px)';
card.style.opacity = '0.8';

// Атрибуты
image.setAttribute('src', 'new-image.jpg');
image.setAttribute('alt', 'Tour photo');
const href = link.getAttribute('href');
```

### Создание и добавление элементов

```javascript
// Создание нового элемента
const newCard = document.createElement('div');
newCard.className = 'tour-card';
newCard.innerHTML = `
  <img src="tour.jpg" alt="Tour">
  <h3>Desert Safari</h3>
  <p class="price">AED 250</p>
`;

// Добавление в DOM
container.appendChild(newCard); // в конец
container.insertBefore(newCard, firstChild); // перед элементом
element.remove(); // удаление элемента

// Замена контента
container.innerHTML = ''; // очистка
cards.forEach(card => container.appendChild(card));
```

---

## 2. Form Validation & Submission

### Базовая валидация

```javascript
const form = document.querySelector('#booking-form');
const emailInput = document.querySelector('#email');
const phoneInput = document.querySelector('#phone');

form.addEventListener('submit', async (e) => {
  e.preventDefault(); // Предотвращаем перезагрузку страницы

  // Сбор данных формы
  const formData = new FormData(form);
  const data = Object.fromEntries(formData);

  // Валидация email
  if (!data.email.includes('@') || !data.email.includes('.')) {
    showError(emailInput, 'Введите корректный email');
    return;
  }

  // Валидация телефона (UAE формат)
  const phoneRegex = /^\+971[0-9]{9}$/;
  if (!phoneRegex.test(data.phone)) {
    showError(phoneInput, 'Формат: +971XXXXXXXXX');
    return;
  }

  // Валидация обязательных полей
  const required = form.querySelectorAll('[required]');
  let isValid = true;

  required.forEach(field => {
    if (!field.value.trim()) {
      showError(field, 'Это поле обязательно');
      isValid = false;
    }
  });

  if (!isValid) return;

  // Отправка данных
  await submitBooking(data);
});

function showError(input, message) {
  const error = document.createElement('span');
  error.className = 'error-message';
  error.textContent = message;

  input.classList.add('input-error');
  input.parentElement.appendChild(error);

  // Убрать ошибку при вводе
  input.addEventListener('input', () => {
    input.classList.remove('input-error');
    error.remove();
  }, { once: true });
}
```

### Real-time валидация

```javascript
// Проверка email при вводе
emailInput.addEventListener('input', (e) => {
  const value = e.target.value;
  const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

  emailInput.classList.toggle('valid', isValid);
  emailInput.classList.toggle('invalid', !isValid && value.length > 0);
});

// Автоформатирование телефона
phoneInput.addEventListener('input', (e) => {
  let value = e.target.value.replace(/\D/g, ''); // только цифры
  if (value.startsWith('971')) {
    value = '+' + value;
  }
  e.target.value = value;
});
```

---

## 3. Fetch API

### Загрузка данных

```javascript
async function fetchTours(category = 'all') {
  const loader = document.querySelector('.loader');
  const container = document.querySelector('.tours-container');

  try {
    // Показать индикатор загрузки
    loader.classList.remove('hidden');

    // Запрос к API
    const response = await fetch(`/api/tours?category=${category}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const tours = await response.json();

    // Отрисовка результатов
    renderTours(tours);

  } catch (error) {
    console.error('Error fetching tours:', error);
    showError('Не удалось загрузить туры. Попробуйте позже.');
  } finally {
    loader.classList.add('hidden');
  }
}

function renderTours(tours) {
  const container = document.querySelector('.tours-container');

  if (tours.length === 0) {
    container.innerHTML = '<p class="no-results">Туры не найдены</p>';
    return;
  }

  container.innerHTML = tours.map(tour => `
    <div class="tour-card" data-id="${tour.id}">
      <img src="${tour.image}" alt="${tour.title}">
      <h3>${tour.title}</h3>
      <p class="price">AED ${tour.price}</p>
      <button class="book-btn" data-tour-id="${tour.id}">
        Забронировать
      </button>
    </div>
  `).join('');
}
```

### Отправка данных (POST)

```javascript
async function submitBooking(bookingData) {
  try {
    const response = await fetch('/api/bookings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bookingData)
    });

    const result = await response.json();

    if (response.ok) {
      showSuccessMessage('Бронирование успешно!');
      form.reset();
    } else {
      throw new Error(result.message);
    }

  } catch (error) {
    showError('Ошибка бронирования: ' + error.message);
  }
}
```

---

## 4. Event Handling

### Основные типы событий

```javascript
// Клик
button.addEventListener('click', (e) => {
  console.log('Button clicked!');
});

// Отправка формы
form.addEventListener('submit', (e) => {
  e.preventDefault();
  // обработка
});

// Ввод текста
input.addEventListener('input', (e) => {
  console.log('Current value:', e.target.value);
});

// Изменение значения
select.addEventListener('change', (e) => {
  filterTours(e.target.value);
});

// Наведение мыши
card.addEventListener('mouseenter', () => {
  card.classList.add('hover');
});

card.addEventListener('mouseleave', () => {
  card.classList.remove('hover');
});
```

### Делегирование событий

Вместо добавления обработчиков на каждый элемент, используем один обработчик на родителе:

```javascript
// ❌ Неэффективно для большого количества элементов
document.querySelectorAll('.book-btn').forEach(btn => {
  btn.addEventListener('click', handleBooking);
});

// ✅ Эффективно: один обработчик на контейнере
document.querySelector('.tours-container').addEventListener('click', (e) => {
  if (e.target.classList.contains('book-btn')) {
    const tourId = e.target.dataset.tourId;
    handleBooking(tourId);
  }
});
```

### Debounce для поиска

Избегаем лишних запросов при быстром вводе:

```javascript
function debounce(func, delay = 300) {
  let timeoutId;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

// Использование
const searchInput = document.querySelector('#search');

const performSearch = debounce(async (query) => {
  if (query.length < 3) return;

  const results = await fetch(`/api/search?q=${query}`);
  const data = await results.json();
  displayResults(data);
}, 300);

searchInput.addEventListener('input', (e) => {
  performSearch(e.target.value);
});
```

### Throttle для scroll событий

Ограничиваем частоту выполнения при скролле:

```javascript
function throttle(func, limit = 100) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Использование
const handleScroll = throttle(() => {
  const scrolled = window.scrollY;
  const header = document.querySelector('header');

  header.classList.toggle('sticky', scrolled > 100);
}, 100);

window.addEventListener('scroll', handleScroll);
```

---

## Практические примеры

### Фильтрация карточек туров

```javascript
const filterButtons = document.querySelectorAll('.filter-btn');
const tourCards = document.querySelectorAll('.tour-card');

filterButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const category = btn.dataset.category;

    // Обновить активную кнопку
    filterButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Фильтровать карточки
    tourCards.forEach(card => {
      const cardCategory = card.dataset.category;
      const shouldShow = category === 'all' || cardCategory === category;

      card.style.display = shouldShow ? 'block' : 'none';
    });
  });
});
```

### Модальное окно бронирования

```javascript
const modal = document.querySelector('.modal');
const openButtons = document.querySelectorAll('.book-btn');
const closeButton = document.querySelector('.modal-close');

openButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const tourId = btn.dataset.tourId;
    openModal(tourId);
  });
});

function openModal(tourId) {
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  loadTourDetails(tourId);
}

function closeModal() {
  modal.classList.remove('active');
  document.body.style.overflow = '';
}

closeButton.addEventListener('click', closeModal);

// Закрытие по клику на фон
modal.addEventListener('click', (e) => {
  if (e.target === modal) {
    closeModal();
  }
});

// Закрытие по Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && modal.classList.contains('active')) {
    closeModal();
  }
});
```

---

**Связанные файлы:**
- `responsive-patterns.md` — адаптивные компоненты
- `best-practices.md` — оптимизация производительности
- `SKILL.md` (строки 1600-1850) — полные примеры интеграции