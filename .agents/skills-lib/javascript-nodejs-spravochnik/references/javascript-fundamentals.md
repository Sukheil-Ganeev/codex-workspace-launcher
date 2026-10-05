# JavaScript Fundamentals

Справочник по основным концепциям ES6+ JavaScript с примерами для туристического бизнеса (экскурсии, бронирования, клиенты).

---

## 1. ES6+ Синтаксис: let, const, Destructuring, Spread/Rest

### let и const

Используйте `const` по умолчанию (неизменяемые переменные), `let` только при необходимости переприсваивания.

```javascript
// const - для значений, которые не меняются
const businessName = 'Dubai Tours & Adventures';
const maxToursPerDay = 5;

// let - для значений, которые меняются
let bookingsToday = 0;
let totalRevenue = 0;

bookingsToday++;
totalRevenue += 500;
```

### Деструктуризация объектов

Экстракция свойств объекта в отдельные переменные:

```javascript
// Туристический заказ
const booking = {
  id: 'TOUR-001',
  customerName: 'Ahmed Al-Mansouri',
  tourType: 'desert-safari',
  price: 250,
  date: '2026-02-15',
  participants: 4
};

// Классический способ
const id = booking.id;
const name = booking.customerName;
const participants = booking.participants;

// Деструктуризация - лучше
const { id, customerName, price, participants } = booking;

// С переименованием
const { customerName: name, tourType: type } = booking;

// С значениями по умолчанию
const { status = 'pending', notes = 'No notes' } = booking;
```

### Деструктуризация массивов

```javascript
const tours = ['Desert Safari', 'City Tour', 'Yacht Cruise'];

// Классический способ
const firstTour = tours[0];
const secondTour = tours[1];

// Деструктуризация
const [first, second, third] = tours;

// Пропуск элементов
const [primary, , tertiary] = tours;

// Rest оператор (rest of elements)
const [mainTour, ...otherTours] = tours;
console.log(mainTour);      // 'Desert Safari'
console.log(otherTours);    // ['City Tour', 'Yacht Cruise']
```

### Spread оператор

Раскрытие массива/объекта:

```javascript
// Массивы
const baseTours = ['Desert Safari', 'City Tour'];
const premiumTours = ['Yacht Cruise', 'Private Jet'];
const allTours = [...baseTours, ...premiumTours];

// Объекты
const customerInfo = {
  name: 'Fatima Al-Hashmi',
  email: 'fatima@example.com'
};

const bookingData = {
  ...customerInfo,
  tourId: 'TOUR-002',
  date: '2026-02-20',
  paid: true
};
// Result: { name: 'Fatima...', email: '...', tourId: '...', date: '...', paid: true }

// Копирование с переопределением
const updatedBooking = {
  ...bookingData,
  paid: false,
  notes: 'Payment pending'
};
```

---

## 2. Arrow Functions и контекст `this`

### Arrow Functions синтаксис

```javascript
// Обычная функция
function calculateTourPrice(basePrice, discount) {
  return basePrice - discount;
}

// Arrow function - одна строка
const calculateTourPrice = (basePrice, discount) => basePrice - discount;

// Arrow function - несколько строк
const calculateTourPrice = (basePrice, discount) => {
  const discountAmount = basePrice * (discount / 100);
  return basePrice - discountAmount;
};

// Без параметров
const getTodayDate = () => new Date().toISOString().split('T')[0];

// Один параметр (скобки опциональны)
const isExpensiveTour = price => price > 500;
const isExpensiveTour = (price) => price > 500;
```

### this в arrow functions

Arrow functions не имеют своего `this` - используют `this` из родительского контекста:

```javascript
// Проблема с обычными функциями
const businessManager = {
  name: 'Marcel (Car Rentals)',
  yearsInBusiness: 15,

  getInfo: function() {
    console.log(this.name); // ✓ Works

    setTimeout(function() {
      console.log(this.name); // ✗ undefined (this = window/global)
    }, 1000);
  }
};

// Решение 1: arrow function
const businessManager = {
  name: 'Marcel (Car Rentals)',
  yearsInBusiness: 15,

  getInfo: function() {
    console.log(this.name); // 'Marcel (Car Rentals)'

    setTimeout(() => {
      console.log(this.name); // ✓ 'Marcel (Car Rentals)'
    }, 1000);
  }
};

// Решение 2: стрелочный метод (ES2022+)
const businessManager = {
  name: 'Marcel (Car Rentals)',
  yearsInBusiness: 15,

  getInfo: () => {
    console.log(this.name); // ✓ Works в контексте класса
  }
};
```

---

## 3. Async/Await и Promises

### Promises - основы

```javascript
// Создание Promise
const fetchTourDetails = (tourId) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (tourId) {
        resolve({ id: tourId, name: 'Desert Safari', price: 250 });
      } else {
        reject('Invalid tour ID');
      }
    }, 1000);
  });
};

// Использование .then/.catch
fetchTourDetails('TOUR-001')
  .then(tour => console.log('Tour:', tour))
  .catch(error => console.error('Error:', error));
```

### Async/Await - современный подход

```javascript
// Функция возвращает Promise
async function bookTour(tourId, customerId) {
  try {
    // Ждём результат (как synchronous код выглядит)
    const tour = await fetchTourDetails(tourId);
    const customer = await fetchCustomerInfo(customerId);

    const booking = {
      tourId: tour.id,
      customerId: customer.id,
      price: tour.price,
      bookedAt: new Date(),
      status: 'confirmed'
    };

    const savedBooking = await saveBookingToDatabase(booking);
    return savedBooking;

  } catch (error) {
    console.error('Booking failed:', error);
    throw error;
  }
}

// Вызов async функции
bookTour('TOUR-001', 'CUST-042')
  .then(booking => console.log('Booked:', booking))
  .catch(error => console.error('Error:', error));
```

### Promise.all - параллельные операции

```javascript
// Получить данные о нескольких экскурсиях одновременно
async function getAvailableTours() {
  try {
    const promises = [
      fetchTourDetails('TOUR-001'),
      fetchTourDetails('TOUR-002'),
      fetchTourDetails('TOUR-003')
    ];

    const tours = await Promise.all(promises);
    return tours;

  } catch (error) {
    console.error('Failed to fetch tours:', error);
  }
}
```

---

## 4. Modules (import/export)

### Named exports

```javascript
// tours.js
export const calculateDiscount = (price, percentOff) => {
  return price * (1 - percentOff / 100);
};

export const tourTypes = ['Desert Safari', 'City Tour', 'Yacht Cruise'];

export function formatTourDate(date) {
  return new Date(date).toLocaleDateString('en-US');
}

// main.js - Импорт
import { calculateDiscount, tourTypes, formatTourDate } from './tours.js';

const discountedPrice = calculateDiscount(250, 10);
console.log(tourTypes);
console.log(formatTourDate('2026-02-15'));
```

### Default export

```javascript
// BookingService.js
export default class BookingService {
  constructor(apiUrl) {
    this.apiUrl = apiUrl;
  }

  async createBooking(tourId, customerId) {
    // Implementation
  }
}

// app.js
import BookingService from './BookingService.js';

const bookingService = new BookingService('https://api.tours.ae');
```

### Переименование при импорте

```javascript
import { calculateDiscount as applyDiscount } from './tours.js';
import BookingService as BookService from './BookingService.js';

const newPrice = applyDiscount(300, 15);
```

---

## 5. Array Methods: map, filter, reduce, find

### map - преобразование каждого элемента

```javascript
const bookings = [
  { id: 1, tourName: 'Desert Safari', price: 250 },
  { id: 2, tourName: 'City Tour', price: 150 },
  { id: 3, tourName: 'Yacht Cruise', price: 400 }
];

// Получить только названия
const tourNames = bookings.map(b => b.tourName);
// ['Desert Safari', 'City Tour', 'Yacht Cruise']

// Применить скидку 10%
const discountedPrices = bookings.map(b => ({
  ...b,
  originalPrice: b.price,
  price: b.price * 0.9
}));
```

### filter - выбор элементов по условию

```javascript
// Экскурсии дороже 300 AED
const expensiveTours = bookings.filter(b => b.price > 300);

// Только города (из более полного набора)
const allTours = [
  { name: 'Desert Safari', type: 'adventure' },
  { name: 'City Tour', type: 'cultural' },
  { name: 'Mountain Hike', type: 'adventure' }
];

const culturalTours = allTours.filter(t => t.type === 'cultural');
```

### reduce - агрегация в одно значение

```javascript
// Общая сумма всех заказов
const bookings = [
  { price: 250, participants: 4 },
  { price: 150, participants: 2 },
  { price: 400, participants: 6 }
];

const totalRevenue = bookings.reduce((sum, booking) => {
  return sum + booking.price;
}, 0);
// 800

// Подсчёт всех участников
const totalParticipants = bookings.reduce((count, booking) => {
  return count + booking.participants;
}, 0);
// 12

// Группировка по типу
const bookingsByMonth = bookings.reduce((acc, booking) => {
  const month = new Date(booking.date).getMonth();
  if (!acc[month]) acc[month] = [];
  acc[month].push(booking);
  return acc;
}, {});
```

### find - найти первый элемент

```javascript
// Найти бронирование по ID
const bookingId = 'BK-042';
const booking = bookings.find(b => b.id === bookingId);

// Найти премиум экскурсию
const premiumTour = allTours.find(t => t.price > 500);

// Найти, или вернуть null
const customerTour = bookings.find(b => b.customerId === 'CUST-015') || null;
```

---

## 6. Template Literals

### Основной синтаксис

```javascript
const customerName = 'Ahmed Al-Mansouri';
const tourType = 'Desert Safari';
const price = 250;

// Старый способ (конкатенация)
const message = 'Welcome ' + customerName + '! Your ' + tourType + ' tour costs ' + price + ' AED.';

// Template literal (backticks)
const message = `Welcome ${customerName}! Your ${tourType} tour costs ${price} AED.`;
```

### Многострочные строки

```javascript
const tourDescription = `
  🏜️ DESERT SAFARI ADVENTURE
  ───────────────────────────
  Experience the breathtaking beauty of Arabian dunes.

  Includes:
  - 4x4 Jeep ride
  - Camel riding
  - BBQ dinner
  - Sunset photography

  Duration: 6 hours
  Price: 250 AED per person
`;

// Без template literal - не так красиво:
const message = '🏜️ DESERT SAFARI ADVENTURE\n───────────────────────────\n...';
```

### Выражения в template literals

```javascript
const basePrice = 200;
const discountPercent = 15;

const priceInfo = `
  Base price: ${basePrice} AED
  Discount: ${discountPercent}%
  Final price: ${basePrice * (1 - discountPercent / 100)} AED
  Total for 4 people: ${basePrice * 4 * (1 - discountPercent / 100)} AED
`;

// С функциями
const getTourDuration = (tourType) => tourType === 'safari' ? 6 : 4;

const bookingSummary = `
  Tour: ${tourType}
  Duration: ${getTourDuration(tourType)} hours
  Participants: ${participants}
`;
```

---

## 7. Optional Chaining (?.) и Nullish Coalescing (??)

### Optional Chaining (?.)

Безопасный доступ к вложенным свойствам:

```javascript
const customer = {
  name: 'Fatima Al-Hashmi',
  address: {
    city: 'Dubai',
    street: 'Sheikh Zayed Road'
  }
  // phone не определено
};

// Старый способ (с проверкой)
if (customer && customer.phone && customer.phone.mobile) {
  console.log(customer.phone.mobile);
}

// С optional chaining
console.log(customer?.phone?.mobile); // undefined (без ошибки!)
console.log(customer?.address?.city); // 'Dubai'

// С методами
const booking = {
  getId: () => 'BK-042'
};

booking?.getId?.();           // 'BK-042'
booking?.updateStatus?.();    // undefined (метод не существует, но ошибки нет)

// С массивами
const bookings = [
  { id: 1, status: 'confirmed' },
  { id: 2, status: 'pending' }
];

console.log(bookings?.[0]?.status); // 'confirmed'
console.log(bookings?.[10]?.status); // undefined
```

### Nullish Coalescing (??)

Использование значения по умолчанию, если переменная null или undefined:

```javascript
let comments = '';
let notes = null;
let feedback;

// || оператор (проблема: пустая строка тоже считается falsy)
const comment1 = comments || 'No comments'; // 'No comments' (но comments была '')
const comment2 = notes || 'No notes'; // 'No notes' ✓

// ?? оператор (лучше: только для null/undefined)
const comment1 = comments ?? 'No comments'; // '' (сохраняет пустую строку!)
const comment2 = notes ?? 'No notes'; // 'No notes' ✓
const comment3 = feedback ?? 'Not provided'; // 'Not provided' ✓

// С объектами
const booking = {
  customerName: 'Ahmed',
  specialRequests: null
};

const requests = booking?.specialRequests ?? 'No special requests';
// 'No special requests'
```

---

## 8. Common Mistakes (Частые ошибки)

### 1. Изменение const объектов

```javascript
// ✗ ОШИБКА: const НЕ означает неизменяемость
const tour = { name: 'Safari', price: 250 };
tour.price = 300; // ✓ Это работает!
// tour = {}; // ✗ Это НЕ работает (переприсваивание)

// ✓ ПРАВИЛЬНО: используйте Object.freeze для неизменяемости
const tour = Object.freeze({
  name: 'Safari',
  price: 250
});
// tour.price = 300; // ✗ Ошибка в strict mode
```

### 2. this в callback функциях

```javascript
// ✗ ОШИБКА: неправильный контекст
const tourManager = {
  name: 'Paramount Yachts',
  bookings: [],

  addBooking: function(booking) {
    setTimeout(function() {
      this.bookings.push(booking); // ✗ this = undefined/window
    }, 1000);
  }
};

// ✓ ПРАВИЛЬНО: arrow function
const tourManager = {
  name: 'Paramount Yachts',
  bookings: [],

  addBooking: function(booking) {
    setTimeout(() => {
      this.bookings.push(booking); // ✓ this = tourManager
    }, 1000);
  }
};
```

### 3. Забывают return в map/filter

```javascript
// ✗ ОШИБКА: забыли скобки, нет return
const prices = bookings.map(b => {
  b.price * 1.1; // Не возвращается!
}); // [undefined, undefined, ...]

// ✓ ПРАВИЛЬНО: один return
const prices = bookings.map(b => b.price * 1.1);

// ✓ ИЛИ: явные скобки и return
const prices = bookings.map(b => {
  return b.price * 1.1;
});
```

### 4. Ошибки с async/await

```javascript
// ✗ ОШИБКА: забыли await
async function getTourInfo() {
  const tour = fetchTourDetails('TOUR-001'); // Promise, не объект!
  console.log(tour.price); // undefined
}

// ✓ ПРАВИЛЬНО: используйте await
async function getTourInfo() {
  const tour = await fetchTourDetails('TOUR-001');
  console.log(tour.price); // ✓ 250
}

// ✗ ОШИБКА: ловушка с Promise.all
const [tour1, tour2, tour3] = await Promise.all([
  fetchTourDetails('TOUR-001'),
  fetchTourDetails('TOUR-002'),
  fetchTourDetails('TOUR-003')
  // Если одна ошибётся, вся операция сломается!
]);

// ✓ ПРАВИЛЬНО: используйте Promise.allSettled для устойчивости
const results = await Promise.allSettled([
  fetchTourDetails('TOUR-001'),
  fetchTourDetails('TOUR-002')
]);
// results[0] = { status: 'fulfilled', value: {...} }
// results[1] = { status: 'rejected', reason: 'Error...' }
```

### 5. Мутация исходных данных

```javascript
// ✗ ОШИБКА: изменяем исходный массив
const bookings = [
  { id: 1, price: 250 },
  { id: 2, price: 150 }
];

const expensive = bookings.sort((a, b) => b.price - a.price);
// bookings теперь тоже отсортирован! ✗

// ✓ ПРАВИЛЬНО: создайте копию
const expensive = [...bookings].sort((a, b) => b.price - a.price);
// bookings остался неизменённым ✓

// ✓ ИЛИ: используйте spread при изменении объектов
const updatedBooking = {
  ...booking,
  status: 'confirmed'
}; // booking не изменился
```

### 6. Забывают обработку ошибок

```javascript
// ✗ ОШИБКА: без обработки ошибок
async function bookTour() {
  const result = await fetchTourDetails('INVALID-ID');
  console.log(result.name); // Крешится если ошибка!
}

// ✓ ПРАВИЛЬНО: всегда используйте try-catch
async function bookTour() {
  try {
    const result = await fetchTourDetails('INVALID-ID');
    console.log(result.name);
  } catch (error) {
    console.error('Booking error:', error.message);
  }
}
```

---

## Практический пример: Система бронирования

```javascript
// tours.js
export const tours = [
  { id: 'T-001', name: 'Desert Safari', price: 250, type: 'adventure' },
  { id: 'T-002', name: 'City Tour', price: 150, type: 'cultural' },
  { id: 'T-003', name: 'Yacht Cruise', price: 400, type: 'luxury' }
];

export const calculateTotal = (tourIds, discount = 0) => {
  const total = tourIds.reduce((sum, id) => {
    const tour = tours.find(t => t.id === id);
    return sum + (tour?.price ?? 0);
  }, 0);

  return total * (1 - discount / 100);
};

// bookingService.js
import { calculateTotal, tours } from './tours.js';

export class BookingService {
  constructor() {
    this.bookings = [];
  }

  async createBooking(tourIds, customerInfo) {
    try {
      const { name, email, phone } = customerInfo;
      const totalPrice = calculateTotal(tourIds);

      const booking = {
        id: `BK-${Date.now()}`,
        customerName: name,
        email,
        phone,
        tourIds,
        totalPrice,
        status: 'confirmed',
        createdAt: new Date().toISOString()
      };

      this.bookings.push(booking);
      return booking;

    } catch (error) {
      console.error('Booking error:', error);
      throw error;
    }
  }

  getBookingsByStatus(status) {
    return this.bookings.filter(b => b.status === status);
  }

  getTotalRevenue() {
    return this.bookings
      .filter(b => b.status === 'confirmed')
      .reduce((sum, b) => sum + b.totalPrice, 0);
  }
}

// main.js
import { BookingService } from './bookingService.js';

const service = new BookingService();

(async () => {
  const booking = await service.createBooking(
    ['T-001', 'T-002'],
    {
      name: 'Ahmed Al-Mansouri',
      email: 'ahmed@example.com',
      phone: '+971501234567'
    }
  );

  console.log(`Booking created: ${booking.id}`);
  console.log(`Total: ${booking.totalPrice} AED`);
  console.log(`Revenue today: ${service.getTotalRevenue()} AED`);
})();
```

---

**Последнее обновление:** February 2026
