# Парсинг цепочек сообщений (Reply-to)

## Зачем это нужно

Reply-to парсинг позволяет восстановить логическую структуру диалога из плоского списка сообщений. В WhatsApp экспорте цитаты отображаются с символом `>` в начале строки, что позволяет понять, на какое сообщение отвечает пользователь.

**Применения:**
- Восстановление контекста переписки
- Анализ дискуссий и веток обсуждений
- Отслеживание ответов на конкретные вопросы
- Построение дерева диалога для визуализации
- Определение "потерянных" вопросов без ответов

---

## Формат reply в WhatsApp экспорте

При экспорте чата WhatsApp цитируемые сообщения отображаются с префиксом `>`:

```
[15.01.25, 14:30] Клиент: > Тур стоит 500$
> на двоих?

Да, на двоих
```

Здесь клиент цитирует сообщение "Тур стоит 500$" и задает уточняющий вопрос "на двоих?", на который получает ответ "Да, на двоих".

---

## Regex паттерны

### Базовые регулярки для цитат

```javascript
// Цитата в начале сообщения (одна или несколько строк)
const quoteRegex = /^>\s*(.+?)(?:\n|$)/gm;

// Полная структура reply: цитата + ответ
const replyPattern = /^((?:>\s*.+\n)+)(.+)$/s;

// Извлечение оригинального текста из цитаты
function extractQuote(message) {
  const match = message.match(/^>\s*(.+)/m);
  return match ? match[1].trim() : null;
}
```

### Многострочные цитаты

```javascript
// Извлечь все строки цитаты
function extractAllQuoteLines(message) {
  const lines = message.split('\n');
  const quotes = [];

  for (const line of lines) {
    const match = line.match(/^>\s*(.+)/);
    if (match) {
      quotes.push(match[1].trim());
    } else if (quotes.length > 0) {
      // Конец цитаты
      break;
    }
  }

  return quotes.join(' ');
}
```

### Извлечение ответа (без цитаты)

```javascript
// Получить текст ответа без цитируемой части
function extractReplyText(message) {
  const lines = message.split('\n');
  const replyLines = [];
  let quotePassed = false;

  for (const line of lines) {
    if (line.startsWith('>')) {
      quotePassed = true;
      continue;
    }
    if (quotePassed || !line.startsWith('>')) {
      const trimmed = line.trim();
      if (trimmed) replyLines.push(trimmed);
    }
  }

  return replyLines.join(' ');
}
```

---

## JSON схема треда

```json
{
  "thread": {
    "root_message_id": "msg_001",
    "messages": [
      {
        "id": "msg_001",
        "text": "Тур стоит 500$",
        "replies": ["msg_002", "msg_005"]
      },
      {
        "id": "msg_002",
        "text": "на двоих?",
        "reply_to": "msg_001",
        "replies": ["msg_003"]
      },
      {
        "id": "msg_003",
        "text": "Да, на двоих",
        "reply_to": "msg_002"
      }
    ]
  }
}
```

### Расширенная схема с метаданными

```json
{
  "thread": {
    "id": "thread_20250115_001",
    "root_message_id": "msg_001",
    "depth": 3,
    "total_messages": 5,
    "participants": ["agent", "client"],
    "started_at": "2025-01-15T10:00:00",
    "ended_at": "2025-01-15T10:15:00",
    "messages": [
      {
        "id": "msg_001",
        "timestamp": "2025-01-15T10:00:00",
        "sender": "agent",
        "text": "Тур стоит 500$",
        "reply_to": null,
        "replies": ["msg_002"],
        "depth": 0,
        "is_root": true,
        "has_unanswered_question": false
      },
      {
        "id": "msg_002",
        "timestamp": "2025-01-15T10:05:00",
        "sender": "client",
        "text": "на двоих?",
        "quoted_text": "Тур стоит 500$",
        "reply_to": "msg_001",
        "replies": ["msg_003"],
        "depth": 1,
        "is_root": false,
        "is_question": true
      },
      {
        "id": "msg_003",
        "timestamp": "2025-01-15T10:06:00",
        "sender": "agent",
        "text": "Да, на двоих",
        "reply_to": "msg_002",
        "replies": [],
        "depth": 2,
        "is_root": false,
        "is_answer": true
      }
    ]
  }
}
```

---

## Алгоритм связывания (linkReplies)

### Базовая функция

```javascript
/**
 * Связывает сообщения по цитатам
 * @param {Array} messages - массив сообщений с полями: id, text, timestamp
 * @returns {Array} - сообщения с добавленными полями reply_to
 */
function linkReplies(messages) {
  return messages.map(msg => {
    const quote = extractQuote(msg.text);
    if (quote) {
      // Поиск оригинального сообщения по тексту цитаты
      const original = messages.find(m =>
        m.text.includes(quote) && m.timestamp < msg.timestamp
      );
      if (original) {
        msg.reply_to = original.id;
      }
    }
    return msg;
  });
}
```

### Улучшенная версия с fuzzy matching

```javascript
/**
 * Улучшенное связывание с нечетким поиском
 */
function linkRepliesAdvanced(messages) {
  return messages.map(msg => {
    const quote = extractQuote(msg.text);
    if (!quote) return msg;

    // Нормализация для сравнения
    const normalizedQuote = normalizeText(quote);

    // Поиск лучшего совпадения
    let bestMatch = null;
    let bestScore = 0;

    for (const candidate of messages) {
      // Пропускаем сообщения после текущего
      if (candidate.timestamp >= msg.timestamp) continue;

      const normalizedText = normalizeText(candidate.text);
      const score = calculateSimilarity(normalizedQuote, normalizedText);

      if (score > bestScore && score > 0.7) {
        bestScore = score;
        bestMatch = candidate;
      }
    }

    if (bestMatch) {
      msg.reply_to = bestMatch.id;
      msg.quoted_text = quote;
      msg.match_confidence = bestScore;
    }

    return msg;
  });
}

/**
 * Нормализация текста для сравнения
 */
function normalizeText(text) {
  return text
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .replace(/[^\wа-яё\s]/gi, '')
    .trim();
}

/**
 * Расчет схожести строк (Jaccard index)
 */
function calculateSimilarity(str1, str2) {
  const words1 = new Set(str1.split(' '));
  const words2 = new Set(str2.split(' '));

  const intersection = [...words1].filter(w => words2.has(w)).length;
  const union = new Set([...words1, ...words2]).size;

  return union > 0 ? intersection / union : 0;
}
```

### Построение дерева ответов

```javascript
/**
 * Строит дерево ответов из связанных сообщений
 */
function buildReplyTree(messages) {
  const linkedMessages = linkRepliesAdvanced(messages);

  // Создаем карту id -> message
  const messageMap = new Map(linkedMessages.map(m => [m.id, {...m, replies: []}]));

  // Связываем replies
  for (const msg of linkedMessages) {
    if (msg.reply_to) {
      const parent = messageMap.get(msg.reply_to);
      if (parent) {
        parent.replies.push(msg.id);
      }
    }
  }

  // Находим корневые сообщения
  const roots = linkedMessages
    .filter(m => !m.reply_to)
    .map(m => messageMap.get(m.id));

  return {
    roots,
    all: [...messageMap.values()],
    orphans: linkedMessages.filter(m => m.reply_to && !messageMap.has(m.reply_to))
  };
}
```

---

## Примеры цепочек сообщений

### Пример 1: Простая цепочка вопрос-ответ

**Исходный экспорт:**
```
[15.01.25, 10:00] Агент: Тур в Дубай на 3 ночи - 800$
[15.01.25, 10:05] Клиент: > Тур в Дубай на 3 ночи - 800$
Это на одного или на двоих?
[15.01.25, 10:06] Агент: > Это на одного или на двоих?
На двоих, включая перелёт
```

**Результат парсинга:**
```json
{
  "thread": {
    "messages": [
      {
        "id": "1",
        "text": "Тур в Дубай на 3 ночи - 800$",
        "reply_to": null,
        "replies": ["2"]
      },
      {
        "id": "2",
        "text": "Это на одного или на двоих?",
        "quoted_text": "Тур в Дубай на 3 ночи - 800$",
        "reply_to": "1",
        "replies": ["3"]
      },
      {
        "id": "3",
        "text": "На двоих, включая перелёт",
        "quoted_text": "Это на одного или на двоих?",
        "reply_to": "2",
        "replies": []
      }
    ]
  }
}
```

### Пример 2: Ветвящийся диалог

**Исходный экспорт:**
```
[15.01.25, 10:00] Агент: Предлагаю два варианта:
1. Отель Marina - 500$
2. Отель Palm - 700$
[15.01.25, 10:10] Клиент: > 1. Отель Marina - 500$
Есть вид на море?
[15.01.25, 10:11] Клиент: > 2. Отель Palm - 700$
А этот далеко от пляжа?
[15.01.25, 10:15] Агент: > Есть вид на море?
Да, номера с видом на марину
[15.01.25, 10:16] Агент: > А этот далеко от пляжа?
Прямо на пляже!
```

**Результат парсинга:**
```json
{
  "thread": {
    "messages": [
      {
        "id": "1",
        "text": "Предлагаю два варианта:\n1. Отель Marina - 500$\n2. Отель Palm - 700$",
        "replies": ["2", "3"]
      },
      {
        "id": "2",
        "text": "Есть вид на море?",
        "quoted_text": "1. Отель Marina - 500$",
        "reply_to": "1",
        "replies": ["4"]
      },
      {
        "id": "3",
        "text": "А этот далеко от пляжа?",
        "quoted_text": "2. Отель Palm - 700$",
        "reply_to": "1",
        "replies": ["5"]
      },
      {
        "id": "4",
        "text": "Да, номера с видом на марину",
        "reply_to": "2",
        "replies": []
      },
      {
        "id": "5",
        "text": "Прямо на пляже!",
        "reply_to": "3",
        "replies": []
      }
    ]
  }
}
```

### Пример 3: Многострочная цитата

**Исходный экспорт:**
```
[15.01.25, 10:00] Агент: Детали тура:
- Отель 5*
- Завтраки включены
- Трансфер
[15.01.25, 10:10] Клиент: > Детали тура:
> - Отель 5*
> - Завтраки включены
> - Трансфер
А обеды можно добавить?
```

**Извлечение:**
```javascript
const quote = extractAllQuoteLines(message);
// Результат: "Детали тура: - Отель 5* - Завтраки включены - Трансфер"
```

---

## Вспомогательные функции

### Поиск неотвеченных вопросов

```javascript
/**
 * Находит вопросы без ответов в цепочке
 */
function findUnansweredQuestions(messages) {
  const linkedMessages = linkRepliesAdvanced(messages);
  const repliedTo = new Set(linkedMessages.map(m => m.reply_to).filter(Boolean));

  return linkedMessages.filter(msg => {
    // Это вопрос?
    const isQuestion = msg.text.includes('?') ||
      /(?:сколько|как|где|когда|почему|можно)/i.test(msg.text);

    // На него есть ответ?
    const hasReply = repliedTo.has(msg.id);

    return isQuestion && !hasReply;
  });
}
```

### Статистика по тредам

```javascript
/**
 * Собирает статистику по цепочкам ответов
 */
function getThreadStats(messages) {
  const tree = buildReplyTree(messages);

  return {
    total_threads: tree.roots.length,
    total_messages: messages.length,
    avg_thread_depth: calculateAvgDepth(tree.roots),
    max_thread_depth: calculateMaxDepth(tree.roots),
    orphan_messages: tree.orphans.length,
    messages_with_replies: tree.all.filter(m => m.replies.length > 0).length,
    messages_without_replies: tree.all.filter(m => m.replies.length === 0).length
  };
}

function calculateMaxDepth(roots, messageMap) {
  let maxDepth = 0;

  function traverse(msgId, depth) {
    maxDepth = Math.max(maxDepth, depth);
    const msg = messageMap?.get(msgId) || roots.find(r => r.id === msgId);
    if (msg && msg.replies) {
      for (const replyId of msg.replies) {
        traverse(replyId, depth + 1);
      }
    }
  }

  for (const root of roots) {
    traverse(root.id, 0);
  }

  return maxDepth;
}
```

---

## Интеграция с основным парсером

```javascript
class WhatsAppReplyParser {
  constructor(messages) {
    this.messages = messages;
    this.linked = null;
    this.tree = null;
  }

  parse() {
    this.linked = linkRepliesAdvanced(this.messages);
    this.tree = buildReplyTree(this.messages);
    return this;
  }

  getThread(messageId) {
    // Получить всю цепочку от корня до указанного сообщения
    const chain = [];
    let current = this.linked.find(m => m.id === messageId);

    while (current) {
      chain.unshift(current);
      current = current.reply_to
        ? this.linked.find(m => m.id === current.reply_to)
        : null;
    }

    return chain;
  }

  getUnanswered() {
    return findUnansweredQuestions(this.messages);
  }

  getStats() {
    return getThreadStats(this.messages);
  }

  toJSON() {
    return {
      messages: this.linked,
      threads: this.tree.roots.map(r => r.id),
      stats: this.getStats()
    };
  }
}
```

---

## См. также

- `regex-cheatsheet.md` - Базовые регулярные выражения
- `entities-dictionary.md` - Словарь сущностей для парсинга
- `SKILL.md` - Основная документация скилла
