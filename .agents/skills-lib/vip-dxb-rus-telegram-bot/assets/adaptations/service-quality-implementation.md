# Гайд по внедрению системы контроля качества (Блоки 1040-1050)

## 🎯 Для разработчика бота

Этот документ содержит техническую информацию для внедрения блоков 1040-1050 в Telegram-бот VIP-DXB-RUS.

---

## 📋 Структура базы данных

### Таблица: `tours`

```sql
CREATE TABLE tours (
    id INTEGER PRIMARY KEY,
    tour_name TEXT NOT NULL,
    tour_date DATE NOT NULL,
    tour_start_time TIME,
    tour_end_time TIME,
    client_id INTEGER,
    guide_id INTEGER,
    group_size INTEGER,
    pickup_time TIME,
    status TEXT CHECK(status IN ('Ожидает оплаты', 'Подтвержден', 'На экскурсии', 'Завершен')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица: `guides`

```sql
CREATE TABLE guides (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    rating REAL DEFAULT 0,  -- 0-100
    status TEXT CHECK(status IN ('Platinum', 'Gold', 'Silver', 'Bronze', 'Review')),
    tours_completed INTEGER DEFAULT 0,
    avg_client_rating REAL DEFAULT 0,  -- 0-5
    reports_on_time INTEGER DEFAULT 0,
    total_reports INTEGER DEFAULT 0,
    complaints_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица: `guide_reports`

```sql
CREATE TABLE guide_reports (
    id INTEGER PRIMARY KEY,
    tour_id INTEGER NOT NULL,
    guide_id INTEGER NOT NULL,
    photos TEXT,  -- JSON массив URL фото
    plan_status TEXT CHECK(plan_status IN ('Без отклонений', 'Незначительные изменения', 'Проблемы')),
    actual_start_time TIME,
    actual_end_time TIME,
    client_comments TEXT,
    incidents TEXT,  -- JSON массив инцидентов
    guide_client_assessment INTEGER CHECK(guide_client_assessment BETWEEN 1 AND 5),
    additional_notes TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tour_id) REFERENCES tours(id),
    FOREIGN KEY (guide_id) REFERENCES guides(id)
);
```

### Таблица: `guide_checklists`

```sql
CREATE TABLE guide_checklists (
    id INTEGER PRIMARY KEY,
    tour_id INTEGER NOT NULL,
    guide_id INTEGER NOT NULL,
    car_photos TEXT,  -- JSON массив URL
    car_clean BOOLEAN,
    car_fueled BOOLEAN,
    ac_works BOOLEAN,
    water_available BOOLEAN,
    uniform_ready BOOLEAN,
    badge_ready BOOLEAN,
    materials_ready BOOLEAN,
    route_checked BOOLEAN,
    traffic_checked BOOLEAN,
    status TEXT CHECK(status IN ('Все готово', 'Есть проблема')),
    problem_description TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tour_id) REFERENCES tours(id),
    FOREIGN KEY (guide_id) REFERENCES guides(id)
);
```

### Таблица: `satisfaction_surveys`

```sql
CREATE TABLE satisfaction_surveys (
    id INTEGER PRIMARY KEY,
    tour_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    guide_id INTEGER NOT NULL,
    nps_score INTEGER CHECK(nps_score BETWEEN 0 AND 10),
    overall_rating INTEGER CHECK(overall_rating BETWEEN 1 AND 10),
    guide_rating INTEGER CHECK(guide_rating BETWEEN 1 AND 5),
    guide_comments TEXT,
    transport_rating TEXT CHECK(transport_rating IN ('Отлично', 'Хорошо', 'Удовлетворительно', 'Плохо')),
    organization_rating TEXT CHECK(organization_rating IN ('Четко по расписанию', 'Незначительные задержки', 'Серьезные отклонения')),
    price_quality_rating TEXT CHECK(price_quality_rating IN ('Отлично', 'Приемлемо', 'Завышенная цена')),
    liked_most TEXT,
    improvement_suggestions TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tour_id) REFERENCES tours(id),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (guide_id) REFERENCES guides(id)
);
```

### Таблица: `complaints`

```sql
CREATE TABLE complaints (
    id INTEGER PRIMARY KEY,
    complaint_id TEXT UNIQUE NOT NULL,  -- Формат: CMPL-YYYYMMDD-XXXX
    tour_id INTEGER,
    client_id INTEGER,
    complaint_type TEXT NOT NULL,
    description TEXT NOT NULL,
    photos TEXT,  -- JSON массив URL
    is_anonymous BOOLEAN DEFAULT FALSE,
    priority TEXT CHECK(priority IN ('Критический', 'Высокий', 'Средний', 'Низкий')),
    status TEXT CHECK(status IN ('Получена', 'Назначена', 'В обработке', 'Требует информации', 'Решается', 'Решена', 'Закрыта')),
    assigned_to INTEGER,  -- manager_id
    sla_deadline TIMESTAMP,
    resolution_description TEXT,
    compensation_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (tour_id) REFERENCES tours(id),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);
```

### Таблица: `complaint_comments`

```sql
CREATE TABLE complaint_comments (
    id INTEGER PRIMARY KEY,
    complaint_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    author_type TEXT CHECK(author_type IN ('client', 'manager', 'system')),
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id)
);
```

### Таблица: `partners`

```sql
CREATE TABLE partners (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT CHECK(category IN ('ресторан', 'отель', 'яхт-клуб', 'другое')),
    rating REAL DEFAULT 0,  -- 0-5
    tours_count INTEGER DEFAULT 0,
    complaints_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Логика расчета рейтинга гида

### Функция `calculate_guide_rating(guide_id)`

```python
from datetime import datetime, timedelta

def calculate_guide_rating(guide_id: int) -> float:
    """
    Рассчитывает рейтинг гида (0-100) на основе 4 критериев.
    """
    # Период: последние 30 дней
    date_from = datetime.now() - timedelta(days=30)

    # 1. Средняя оценка клиентов (вес 40%)
    client_ratings = db.query("""
        SELECT AVG(guide_rating) as avg_rating
        FROM satisfaction_surveys
        WHERE guide_id = ? AND submitted_at >= ?
    """, (guide_id, date_from))

    avg_client_rating = client_ratings[0]['avg_rating'] or 0  # 0-5
    normalized_client = (avg_client_rating / 5) * 100  # 0-100
    score_clients = normalized_client * 0.4

    # 2. Своевременность отчетов (вес 20%)
    reports = db.query("""
        SELECT
            COUNT(*) as total,
            SUM(CASE
                WHEN submitted_at <= (
                    SELECT tour_end_time + INTERVAL '2 hours'
                    FROM tours WHERE id = guide_reports.tour_id
                ) THEN 1 ELSE 0
            END) as on_time
        FROM guide_reports
        WHERE guide_id = ? AND submitted_at >= ?
    """, (guide_id, date_from))

    total = reports[0]['total'] or 1
    on_time = reports[0]['on_time'] or 0
    timeliness = (on_time / total) * 100  # 0-100
    score_timeliness = timeliness * 0.2

    # 3. Отсутствие жалоб (вес 25%)
    complaints = db.query("""
        SELECT COUNT(*) as count
        FROM complaints
        WHERE tour_id IN (
            SELECT id FROM tours WHERE guide_id = ? AND tour_date >= ?
        )
    """, (guide_id, date_from))

    complaints_count = complaints[0]['count']
    if complaints_count == 0:
        score_complaints = 100 * 0.25
    elif complaints_count == 1:
        score_complaints = 80 * 0.25
    else:
        score_complaints = 50 * 0.25

    # 4. Активность (вес 15%)
    tours = db.query("""
        SELECT COUNT(*) as count
        FROM tours
        WHERE guide_id = ? AND tour_date >= ? AND status = 'Завершен'
    """, (guide_id, date_from))

    tours_count = tours[0]['count']
    max_possible = 60  # 2 тура в день × 30 дней
    activity = min((tours_count / max_possible) * 100, 100)  # cap at 100
    score_activity = activity * 0.15

    # ИТОГОВЫЙ РЕЙТИНГ
    total_rating = score_clients + score_timeliness + score_complaints + score_activity

    # Определение статуса
    if total_rating >= 90:
        status = "Platinum"
        bonus_percent = 30
    elif total_rating >= 80:
        status = "Gold"
        bonus_percent = 20
    elif total_rating >= 70:
        status = "Silver"
        bonus_percent = 10
    elif total_rating >= 60:
        status = "Bronze"
        bonus_percent = 0
    else:
        status = "Review"
        bonus_percent = 0

    # Обновление в БД
    db.execute("""
        UPDATE guides
        SET rating = ?, status = ?, avg_client_rating = ?
        WHERE id = ?
    """, (total_rating, status, avg_client_rating, guide_id))

    return total_rating
```

---

## 🤖 Telegram Bot: Структура хендлеров

### Блок 1040: FORM-GUIDE-REPORT

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

# Состояния
PHOTOS, PLAN_STATUS, TIME, COMMENTS, INCIDENTS, ASSESSMENT, NOTES = range(7)

async def guide_report_start(update: Update, context: CallbackContext):
    """Начало отчета гида после тура."""
    query = update.callback_query
    tour_id = context.user_data['current_tour_id']

    # Получить данные тура
    tour = db.get_tour(tour_id)

    message = f"""
🎯 ОТЧЕТ ГИДА ПОСЛЕ ТУРА

🔹 Тур: {tour['tour_name']}
🔹 Дата: {tour['tour_date']}
🔹 Клиент: {tour['client_name']}
🔹 Группа: {tour['group_size']} чел.

📸 1. ФОТО С ТУРИСТАМИ
Загрузите 2-3 фото с группой во время тура (обязательно)
    """

    await query.edit_message_text(message)
    return PHOTOS

async def guide_report_photos(update: Update, context: CallbackContext):
    """Прием фото от гида."""
    photos = update.message.photo

    # Сохранить URL фото
    if 'report_photos' not in context.user_data:
        context.user_data['report_photos'] = []

    context.user_data['report_photos'].append(photos[-1].file_id)

    if len(context.user_data['report_photos']) >= 2:
        # Переход к следующему шагу
        keyboard = [
            [InlineKeyboardButton("Да, без отклонений", callback_data='plan_ok')],
            [InlineKeyboardButton("Были незначительные изменения", callback_data='plan_minor')],
            [InlineKeyboardButton("Были проблемы", callback_data='plan_issues')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "✅ Фото приняты!\n\n2. ВСЕ ЛИ ПРОШЛО ПО ПЛАНУ?",
            reply_markup=reply_markup
        )
        return PLAN_STATUS
    else:
        await update.message.reply_text(
            f"Фото {len(context.user_data['report_photos'])}/2 загружено. Загрузите еще одно."
        )
        return PHOTOS

async def guide_report_submit(update: Update, context: CallbackContext):
    """Сохранение отчета в БД."""
    tour_id = context.user_data['current_tour_id']
    guide_id = update.effective_user.id

    # Сохранить в БД
    db.insert_guide_report({
        'tour_id': tour_id,
        'guide_id': guide_id,
        'photos': json.dumps(context.user_data['report_photos']),
        'plan_status': context.user_data['plan_status'],
        'actual_start_time': context.user_data['actual_start'],
        'actual_end_time': context.user_data['actual_end'],
        'client_comments': context.user_data.get('client_comments', ''),
        'incidents': json.dumps(context.user_data.get('incidents', [])),
        'guide_client_assessment': context.user_data['assessment'],
        'additional_notes': context.user_data.get('notes', '')
    })

    # Проверка проблем → уведомление менеджеру
    if context.user_data['assessment'] <= 2:
        await notify_manager(
            f"⚠️ Гид {update.effective_user.first_name} сообщает о проблемном туре #{tour_id}"
        )

    # Обновить рейтинг гида
    new_rating = calculate_guide_rating(guide_id)

    await update.callback_query.edit_message_text(
        f"✅ Отчет принят! Спасибо.\n\nВаш текущий рейтинг: {new_rating:.1f}/100"
    )

    return ConversationHandler.END
```

### Блок 1041: FORM-GUIDE-CHECKLIST

```python
async def send_checklist_reminder(tour_id: int):
    """Отправка чек-листа гиду за 2 часа до выезда."""
    tour = db.get_tour(tour_id)
    guide_id = tour['guide_id']

    time_remaining = calculate_time_remaining(tour['pickup_time'])

    keyboard = [
        [InlineKeyboardButton("✅ Все готово, выезжаю", callback_data=f'checklist_ready_{tour_id}')],
        [InlineKeyboardButton("⚠️ Есть проблема", callback_data=f'checklist_problem_{tour_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = f"""
🚗 ЧЕК-ЛИСТ ПЕРЕД ВЫЕЗДОМ

Доброе утро! Сегодня у вас тур: {tour['tour_name']}
Время встречи с клиентом: {tour['pickup_time']}

Пожалуйста, подтвердите готовность:

📸 1. ФОТО ТРАНСПОРТА
Загрузите фото чистого авто (внешний вид + салон)
    """

    await bot.send_message(guide_id, message, reply_markup=reply_markup)

    # Установить напоминание за 30 мин
    schedule_reminder(tour_id, minutes=30)

async def checklist_ready(update: Update, context: CallbackContext):
    """Гид подтвердил готовность."""
    query = update.callback_query
    tour_id = int(query.data.split('_')[-1])

    # Сохранить в БД
    db.insert_checklist({
        'tour_id': tour_id,
        'guide_id': update.effective_user.id,
        'status': 'Все готово',
        'submitted_at': datetime.now()
    })

    # Уведомить клиента
    tour = db.get_tour(tour_id)
    await bot.send_message(
        tour['client_id'],
        f"Ваш гид {update.effective_user.first_name} выезжает к вам!"
    )

    # Уведомить менеджера
    await notify_manager(f"✅ Гид готов к туру #{tour_id}")

    await query.edit_message_text("✅ Отлично! Хорошего тура!")
    return ConversationHandler.END
```

### Блок 1046: FORM-SATISFACTION

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

async def send_satisfaction_survey(tour_id: int):
    """Отправка опроса через 2 часа после тура."""
    tour = db.get_tour(tour_id)
    client_id = tour['client_id']

    # Создать кнопки с оценками 1-10
    keyboard = []
    for i in range(1, 11):
        keyboard.append([InlineKeyboardButton(str(i), callback_data=f'nps_{i}_{tour_id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = f"""
⭐ РАССКАЖИТЕ О ВАШЕМ ОПЫТЕ

Здравствуйте, {tour['client_name']}!
Спасибо за участие в туре "{tour['tour_name']}".

Мы ценим ваше мнение и хотим стать лучше. Уделите 2 минуты, чтобы ответить на 8 вопросов.

━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ ОБЩАЯ ОЦЕНКА ТУРА
Оцените ваши впечатления от 1 до 10:
(1 — очень плохо, 10 — превосходно)
    """

    await bot.send_message(client_id, message, reply_markup=reply_markup)

async def handle_nps_score(update: Update, context: CallbackContext):
    """Обработка NPS-оценки."""
    query = update.callback_query
    data = query.data.split('_')
    nps_score = int(data[1])
    tour_id = int(data[2])

    # Сохранить в контекст
    context.user_data['nps_score'] = nps_score
    context.user_data['survey_tour_id'] = tour_id

    # Следующий вопрос (оценка гида)
    keyboard = [
        [InlineKeyboardButton("⭐", callback_data='guide_1')],
        [InlineKeyboardButton("⭐⭐", callback_data='guide_2')],
        [InlineKeyboardButton("⭐⭐⭐", callback_data='guide_3')],
        [InlineKeyboardButton("⭐⭐⭐⭐", callback_data='guide_4')],
        [InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data='guide_5')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    tour = db.get_tour(tour_id)
    await query.edit_message_text(
        f"2️⃣ РАБОТА ГИДА\nКак вы оцениваете работу гида {tour['guide_name']}?",
        reply_markup=reply_markup
    )

async def survey_complete(update: Update, context: CallbackContext):
    """Завершение опроса и обработка."""
    survey_data = {
        'tour_id': context.user_data['survey_tour_id'],
        'client_id': update.effective_user.id,
        'nps_score': context.user_data['nps_score'],
        'overall_rating': context.user_data['overall_rating'],
        'guide_rating': context.user_data['guide_rating'],
        'transport_rating': context.user_data['transport_rating'],
        'organization_rating': context.user_data['organization_rating'],
        'price_quality_rating': context.user_data['price_quality_rating'],
        'liked_most': context.user_data.get('liked_most', ''),
        'improvement_suggestions': context.user_data.get('improvement', ''),
        'submitted_at': datetime.now()
    }

    # Сохранить в БД
    db.insert_satisfaction_survey(survey_data)

    # Обработка по NPS
    nps = context.user_data['nps_score']

    if nps >= 9:
        # ПРОМОУТЕРЫ → Блок 1047
        await send_promoter_response(update, context)
    elif nps >= 7:
        # НЕЙТРАЛЬНЫЕ
        await update.callback_query.edit_message_text(
            "Спасибо за отзыв! Промокод на 10%: THANKS10"
        )
    else:
        # КРИТИКИ → Блок 1048
        await send_detractor_response(update, context)

    # Обновить рейтинг гида
    tour = db.get_tour(context.user_data['survey_tour_id'])
    calculate_guide_rating(tour['guide_id'])

    return ConversationHandler.END
```

### Блок 1047: NPS-PROMOTERS

```python
async def send_promoter_response(update: Update, context: CallbackContext):
    """Ответ промоутерам (NPS 9-10)."""
    keyboard = [
        [InlineKeyboardButton("⭐ Написать отзыв на Google", url="https://g.page/r/...")],
        [InlineKeyboardButton("📸 Отправить фото с тура", callback_data='send_photos')],
        [InlineKeyboardButton("❌ Спасибо, может позже", callback_data='skip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Сгенерировать промокод
    promo_code = generate_promo_code("VIP500", validity_days=60)
    expiry_date = (datetime.now() + timedelta(days=60)).strftime('%d.%m.%Y')

    # Реферальная ссылка
    referral_link = f"https://t.me/vip_dxb_bot?start=ref_{update.effective_user.id}"

    message = f"""
🎉 СПАСИБО ЗА ВЫСОКУЮ ОЦЕНКУ!

{update.effective_user.first_name}, нам очень приятно, что тур вам понравился!

💚 Поделитесь впечатлениями с другими:

📱 ОСТАВЬТЕ ОТЗЫВ НА GOOGLE MAPS
Ваш отзыв поможет другим туристам сделать правильный выбор.

🎁 В БЛАГОДАРНОСТЬ:
Промокод на 500 AED для следующего тура: {promo_code}
(Действителен до {expiry_date})

---

🔗 ПОДЕЛИТЕСЬ С ДРУЗЬЯМИ:
Приведите друга — получите оба скидку 15%!
Ваша персональная реферальная ссылка:
{referral_link}
    """

    await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
```

### Блок 1048: NPS-DETRACTORS

```python
async def send_detractor_response(update: Update, context: CallbackContext):
    """Ответ критикам (NPS 0-6)."""
    # Создать тикет
    complaint_id = generate_complaint_id()

    db.insert_complaint({
        'complaint_id': complaint_id,
        'tour_id': context.user_data['survey_tour_id'],
        'client_id': update.effective_user.id,
        'complaint_type': 'Низкий NPS',
        'description': f"NPS: {context.user_data['nps_score']}/10",
        'priority': 'Высокий',
        'status': 'Получена',
        'sla_deadline': datetime.now() + timedelta(hours=2)
    })

    # Назначить менеджера
    manager = assign_available_manager()

    # Уведомить менеджера
    await notify_manager(
        f"🚨 КРИТИК (NPS {context.user_data['nps_score']})\n"
        f"Клиент: {update.effective_user.first_name}\n"
        f"Обращение: #{complaint_id}\n"
        f"Необходимо связаться в течение 2 часов!"
    )

    keyboard = [
        [InlineKeyboardButton("💬 Написать менеджеру сейчас", callback_data='chat_manager')],
        [InlineKeyboardButton("📞 Заказать звонок", callback_data='request_call')],
        [InlineKeyboardButton("⏳ Жду звонка", callback_data='wait_call')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    promo_code = generate_promo_code("SORRY30", validity_days=90)

    message = f"""
😔 НАМ ЖАЛЬ, ЧТО ВЫ НЕДОВОЛЬНЫ

{update.effective_user.first_name}, ваше мнение очень важно для нас.

Мы хотим исправить ситуацию!

⚡ СРОЧНАЯ ОБРАБОТКА:
Ваше обращение передано менеджеру.
Мы свяжемся с вами в течение 2 часов.

Номер обращения: #{complaint_id}
Менеджер: {manager['name']}

━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 В КАЧЕСТВЕ ИЗВИНЕНИЙ:
Скидка 30% на следующий тур
Промокод: {promo_code}

━━━━━━━━━━━━━━━━━━━━━━━━━

ЧТО МЫ СДЕЛАЕМ:
✅ Разберем вашу ситуацию
✅ Примем меры в отношении ответственных
✅ Предложим решение проблемы
✅ Гарантируем, что это не повторится
    """

    await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
```

### Блок 1049: FORM-COMPLAINT

```python
async def complaint_start(update: Update, context: CallbackContext):
    """Начало подачи жалобы."""
    keyboard = [
        [InlineKeyboardButton("Жалоба на гида", callback_data='type_guide')],
        [InlineKeyboardButton("Жалоба на партнера", callback_data='type_partner')],
        [InlineKeyboardButton("Проблема с транспортом", callback_data='type_transport')],
        [InlineKeyboardButton("Организационные недочеты", callback_data='type_org')],
        [InlineKeyboardButton("Некорректное поведение", callback_data='type_behavior')],
        [InlineKeyboardButton("Предложение по улучшению", callback_data='type_suggestion')],
        [InlineKeyboardButton("Другое", callback_data='type_other')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📢 ЖАЛОБЫ И ПРЕДЛОЖЕНИЯ\n\nВыберите тип обращения:",
        reply_markup=reply_markup
    )

async def complaint_submit(update: Update, context: CallbackContext):
    """Отправка жалобы."""
    # Классификация приоритета
    complaint_type = context.user_data['complaint_type']
    priority = classify_priority(complaint_type)

    # Генерация ID
    complaint_id = generate_complaint_id()  # CMPL-20260201-0001

    # SLA
    sla_hours = {
        'Критический': 1,
        'Высокий': 2,
        'Средний': 12,
        'Низкий': 48
    }[priority]

    # Сохранить в БД
    db.insert_complaint({
        'complaint_id': complaint_id,
        'tour_id': context.user_data.get('tour_id'),
        'client_id': update.effective_user.id if not context.user_data.get('is_anonymous') else None,
        'complaint_type': complaint_type,
        'description': context.user_data['description'],
        'photos': json.dumps(context.user_data.get('photos', [])),
        'is_anonymous': context.user_data.get('is_anonymous', False),
        'priority': priority,
        'status': 'Получена',
        'sla_deadline': datetime.now() + timedelta(hours=sla_hours)
    })

    # Уведомить менеджера
    await notify_manager_complaint(complaint_id, priority)

    # Ответ клиенту
    sla_deadline = (datetime.now() + timedelta(hours=sla_hours)).strftime('%d.%m.%Y %H:%M')

    await update.message.reply_text(
        f"✅ Ваше обращение #{complaint_id} получено.\n"
        f"Статус: Получена\n"
        f"Приоритет: {priority}\n"
        f"Ответим до: {sla_deadline}\n\n"
        f"Используйте /status_{complaint_id} для отслеживания."
    )
```

---

## ⏰ Автоматические задачи (Cron Jobs)

### Расписание

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Обновление рейтингов гидов (каждые 6 часов)
scheduler.add_job(update_all_guide_ratings, 'interval', hours=6)

# Отправка опросов удовлетворенности (каждые 15 минут)
scheduler.add_job(send_pending_surveys, 'interval', minutes=15)

# Напоминания о чек-листах (каждые 5 минут)
scheduler.add_job(send_checklist_reminders, 'interval', minutes=5)

# Проверка SLA жалоб (каждую минуту)
scheduler.add_job(check_complaint_sla, 'interval', minutes=1)

# Ежедневный отчет менеджерам (21:00)
scheduler.add_job(send_daily_report, 'cron', hour=21, minute=0)

# Еженедельный отчет (понедельник, 10:00)
scheduler.add_job(send_weekly_report, 'cron', day_of_week='mon', hour=10, minute=0)

scheduler.start()
```

### Функции

```python
async def send_pending_surveys():
    """Отправка опросов через 2-4 часа после тура."""
    tours = db.query("""
        SELECT * FROM tours
        WHERE status = 'Завершен'
        AND tour_end_time BETWEEN NOW() - INTERVAL '4 hours' AND NOW() - INTERVAL '2 hours'
        AND id NOT IN (SELECT tour_id FROM satisfaction_surveys)
    """)

    for tour in tours:
        await send_satisfaction_survey(tour['id'])

async def send_checklist_reminders():
    """Напоминания гидам о чек-листах."""
    tours = db.query("""
        SELECT * FROM tours
        WHERE tour_date = CURRENT_DATE
        AND pickup_time BETWEEN NOW() + INTERVAL '25 minutes' AND NOW() + INTERVAL '35 minutes'
        AND id NOT IN (SELECT tour_id FROM guide_checklists)
    """)

    for tour in tours:
        await send_checklist_reminder(tour['id'])

async def check_complaint_sla():
    """Проверка превышения SLA для жалоб."""
    overdue = db.query("""
        SELECT * FROM complaints
        WHERE sla_deadline < NOW()
        AND status NOT IN ('Решена', 'Закрыта')
    """)

    for complaint in overdue:
        # Эскалация
        await escalate_complaint(complaint['id'])
```

---

## 📊 Дашборд (Data Studio / Grafana)

### Метрики для отображения

```sql
-- 1. NPS за период
SELECT
    DATE(submitted_at) as date,
    AVG(CASE
        WHEN nps_score >= 9 THEN 100
        WHEN nps_score >= 7 THEN 0
        ELSE -100
    END) / 100 as nps
FROM satisfaction_surveys
WHERE submitted_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY date;

-- 2. ТОП-10 гидов по рейтингу
SELECT
    name,
    rating,
    status,
    tours_completed,
    avg_client_rating
FROM guides
ORDER BY rating DESC
LIMIT 10;

-- 3. Статистика жалоб
SELECT
    status,
    priority,
    COUNT(*) as count,
    AVG(TIMESTAMPDIFF(HOUR, created_at, resolved_at)) as avg_resolution_hours
FROM complaints
GROUP BY status, priority;

-- 4. Динамика удовлетворенности
SELECT
    DATE(submitted_at) as date,
    AVG(overall_rating) as avg_rating,
    COUNT(*) as surveys_count
FROM satisfaction_surveys
GROUP BY date
ORDER BY date DESC;
```

---

## 🔔 Уведомления менеджерам (Блок 1044)

### Telegram-канал для менеджеров

```python
MANAGER_CHANNEL_ID = -1001234567890  # ID закрытого канала

async def notify_manager(message: str, priority: str = "standard"):
    """Отправка уведомления в канал менеджеров."""
    emoji_map = {
        'critical': '🚨',
        'high': '⚠️',
        'standard': 'ℹ️',
        'low': '📝'
    }

    formatted = f"{emoji_map.get(priority, 'ℹ️')} {message}"

    await bot.send_message(MANAGER_CHANNEL_ID, formatted, parse_mode='Markdown')

async def send_daily_report():
    """Ежедневный отчет в 21:00."""
    today = datetime.now().date()

    # Статистика за день
    tours_today = db.count_tours(today)
    avg_rating = db.avg_rating(today)
    complaints_today = db.count_complaints(today)
    nps_today = db.calc_nps(today)

    # Гиды без отчетов
    missing_reports = db.get_missing_reports(today)

    report = f"""
📊 ЕЖЕДНЕВНЫЙ ОТЧЕТ ({today.strftime('%d.%m.%Y')})

🎯 ТУРЫ:
Проведено: {tours_today}
Средняя оценка: {avg_rating:.1f}/5

⭐ NPS: {nps_today:.1f}

⚠️ ПРОБЛЕМЫ:
Жалобы: {complaints_today}
Гиды без отчетов: {len(missing_reports)}

{'📝 Список гидов без отчетов:\n' + '\n'.join([f"- {g['name']}" for g in missing_reports]) if missing_reports else ''}
    """

    await bot.send_message(MANAGER_CHANNEL_ID, report)
```

---

## 📄 Итоговый чек-лист для разработчика

### Бэкенд
- [ ] Создать таблицы БД (tours, guides, guide_reports, satisfaction_surveys, complaints, partners)
- [ ] Реализовать функцию `calculate_guide_rating()`
- [ ] Настроить cron-задачи (опросы, напоминания, SLA)
- [ ] API для интеграции с Google Maps
- [ ] Генерация промокодов (VIP500, SORRY30, THANKS10)

### Telegram Bot
- [ ] Хендлеры для блоков 1040-1050
- [ ] ConversationHandler для форм (отчет гида, опрос, жалоба)
- [ ] Inline-кнопки для выбора оценок (1-5, 0-10)
- [ ] Уведомления менеджерам (критические/ежедневные/еженедельные)
- [ ] Проверка ролей (Турист/Гид/Менеджер/Админ)

### Интеграции
- [ ] Google Sheets / NocoDB (база данных)
- [ ] Google Maps API (отзывы)
- [ ] WhatsApp Business API (уведомления, опционально)
- [ ] AmoCRM (синхронизация клиентов, опционально)

### Аналитика
- [ ] Дашборд в Google Data Studio / Grafana
- [ ] Графики NPS, удовлетворенности, рейтингов
- [ ] Экспорт данных в Excel/CSV

### Тестирование
- [ ] Протестировать все сценарии на тестовой группе (5+ человек)
- [ ] Проверить таймеры и напоминания
- [ ] Валидация данных (фото обязательны, оценки в диапазоне)
- [ ] Обработка ошибок (недоступность БД, таймауты API)

---

**Файл:** `service-quality-implementation.md`
**Версия:** 1.0
**Дата:** 2026-02-01
**Статус:** Готов к разработке
