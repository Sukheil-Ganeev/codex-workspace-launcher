# JSON Schemas — WhatsApp Parser

**Источник:** SKILL.md, перенесено для экономии места

---

## Message (сообщение)

```json
{
  "message_id": "uuid-v4",
  "jid": "971501234567@s.whatsapp.net",
  "chat_name": "Имя контакта",
  "chat_folder": "Anna_79614598181",
  "source": "whatsapp",
  "datetime": "2026-01-26T10:30:45",
  "date": "2026-01-26",
  "time": "10:30:45",
  "sender": "Имя отправителя",
  "is_from_me": false,
  "is_group": false,
  "text": "Текст сообщения",
  "media": [
    {
      "type": "ФОТО",
      "filename": "IMG_20260126_103045.jpg",
      "path": "media/IMG_20260126_103045.jpg"
    }
  ],
  "location": {
    "lat": 25.197197,
    "lng": 55.274376,
    "url": "https://maps.google.com/?q=25.197197,55.274376"
  },
  "contact_vcf": null,
  "is_forwarded": false,
  "is_deleted": false,
  "reply_to": null,
  "language": "ru",
  "word_count": 5,
  "char_count": 35
}
```

## Contact (контакт)

```json
{
  "contact_id": "uuid",
  "jid": "971501234567@s.whatsapp.net",
  "phone": "+971501234567",
  "name": "Иван",
  "display_name": "Иван Иванов",
  "source": "both",
  "is_group": false,
  "first_message_date": "2024-01-15T10:30:00",
  "last_message_date": "2026-01-26T12:00:00",
  "total_messages": 127,
  "messages_sent": 59,
  "messages_received": 68,
  "language": "ru",
  "country_code": "971"
}
```

## Chat Metadata (метаданные чата)

```json
{
  "chat_id": "uuid-v4",
  "jid": "971501234567@s.whatsapp.net",
  "chat_name": "Марсель Ганеев",
  "chat_folder": "Марсель_971507705321",
  "source": "wa_business",
  "export_date": "2026-01-26T15:30:45",
  "message_count": 1547,
  "first_message": "2024-01-15T10:30:00",
  "last_message": "2026-01-26T12:00:00",
  "duration_days": 742,
  "is_group": false,
  "participants": null,
  "media_stats": {
    "photos": 150,
    "videos": 30,
    "voice": 45,
    "documents": 9
  },
  "parsing_errors": 0,
  "parsed_at": "2026-01-26T18:00:00"
}
```

## Message JSONL (упрощённый формат)

```json
{
  "jid": "971501234567@s.whatsapp.net",
  "chat_name": "Иван",
  "source": "whatsapp|wa_business",
  "chat_folder": "папка_чата",
  "datetime": "2025-01-15T10:30:00",
  "sender": "Иван",
  "is_from_me": false,
  "text": "Привет!",
  "media": [{"type": "photo", "path": "media/img.jpg"}],
  "location": {"lat": "25.2048", "lon": "55.2708"},
  "contact": "John Doe"
}
```

## ExtractedDateTime

```json
{
  "record_id": "uuid",
  "datetime_value": "2026-01-15T10:30:00",
  "date_only": "2026-01-15",
  "time_only": "10:30",
  "context": "arrival|departure|tour_date|payment",
  "confidence": 0.95,
  "original_text": "Прилетаем 15 января в 10:00",
  "timezone": "Asia/Dubai"
}
```

## Session (сессия диалога)

```json
{
  "session_id": "uuid-v4",
  "jid": "971501234567@s.whatsapp.net",
  "chat_name": "Иван Иванов",
  "started_at": "2026-01-15T10:30:00",
  "ended_at": "2026-01-15T12:45:00",
  "duration_minutes": 135,
  "message_count": 24,
  "messages": ["msg_id_1", "msg_id_2", "..."],
  "topic": "yacht_rental",
  "result": "sale",
  "result_confidence": 0.95,
  "entities_mentioned": ["яхта", "50 футов", "4 часа", "2500 AED"],
  "intents": ["PRICE_REQUEST", "AVAILABILITY_REQUEST", "BOOKING_CONFIRM"],
  "reply_chains": [
    {"reply_id": "msg_003", "reply_to_id": "msg_001"}
  ]
}
```

## Payment (платёж)

```json
{
  "payment": {
    "amount": 500,
    "currency": "USD",
    "method": "card",
    "type": "partial",
    "percentage_paid": 50,
    "remaining": 500
  }
}
```

## Hotel Booking (entity)

```json
{
  "entity_type": "hotel_booking",
  "hotel_name": "Atlantis The Palm",
  "city": "Dubai",
  "check_in": "2025-01-15",
  "check_out": "2025-01-20",
  "nights": 5,
  "room_type": "Deluxe Room",
  "guests": {"adults": 2, "children": 1}
}
```

## Contact Graph (граф связей)

```json
{
  "nodes": [{"id": "+971501234567", "name": "Иван", "type": "client"}],
  "edges": [{"source": "+971...", "target": "+971...", "type": "referral", "weight": 3.0}],
  "clusters": [{"id": "cluster_0", "members": ["..."], "nature": "referral_chain"}]
}
```
