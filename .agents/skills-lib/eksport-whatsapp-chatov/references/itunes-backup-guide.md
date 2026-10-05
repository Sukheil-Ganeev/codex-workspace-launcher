# Экспорт из iTunes бэкапа — подробное руководство

Массовый экспорт ВСЕХ чатов WhatsApp из резервной копии iPhone через iTunes/Finder.

---

## Реальный опыт (26.01.2026)

С помощью Claude Code был выполнен массовый экспорт:

| Метрика | WhatsApp | WA Business | ИТОГО |
|---------|----------|-------------|-------|
| **Чатов** | 1,063 | 1,987 | **3,050** |
| **Сообщений** | 485,639 | 401,583 | **887,222** |
| **Медиа** | 233,129 | 179,632 | **412,761** |
| **Не найдено** | 20 | 15 | **35** (0.008%) |

## Где хранится бэкап iTunes

```
C:\Users\[USER]\AppData\Roaming\Apple Computer\MobileSync\Backup\[DEVICE_ID]\
├── Manifest.db          # Индекс всех файлов (SQLite)
├── Manifest.plist       # Метаданные бэкапа
├── Info.plist           # Информация об устройстве
├── Status.plist         # Статус бэкапа
├── 00/ ... ff/          # Папки с файлами (по первым 2 символам хэша)
│   └── [SHA1_HASH]      # Файлы без расширений
```

## Структура данных WhatsApp в бэкапе

**Ключевые файлы:**

| Файл | Domain | Описание |
|------|--------|----------|
| `ChatStorage.sqlite` | `AppDomainGroup-group.net.whatsapp.WhatsApp.shared` | База чатов и сообщений |
| `ContactsV2.sqlite` | то же | Контакты из адресной книги |
| `Message/Media/*` | то же | Медиафайлы |

**Таблицы в ChatStorage.sqlite:**

| Таблица | Содержимое |
|---------|------------|
| `ZWACHATSESSION` | Чаты (Z_PK, ZCONTACTJID, ZPARTNERNAME) |
| `ZWAMESSAGE` | Сообщения (ZMESSAGEDATE, ZTEXT, ZISFROMME, ZGROUPMEMBER) |
| `ZWAMEDIAITEM` | Медиа (ZMEDIALOCALPATH, ZMEDIAURL) |
| `ZWAPROFILEPUSHNAME` | Имена из профилей WhatsApp |
| `ZWAGROUPMEMBER` | Участники групп (ZMEMBERJID) |

## Три источника имён контактов

1. **ContactsV2.sqlite** → `ZWAADDRESSBOOKCONTACT.ZFULLNAME` (адресная книга)
2. **ChatStorage.sqlite** → `ZWACHATSESSION.ZPARTNERNAME` (имя чата)
3. **ChatStorage.sqlite** → `ZWAPROFILEPUSHNAME.ZPUSHNAME` (профиль WhatsApp)

**Приоритет:** Адресная книга → Имя чата → Профиль → Номер телефона

## Связь медиафайлов

```
ChatStorage.ZMEDIALOCALPATH:  Media/JID/a/b/file.opus
                                    ↓ добавляем "Message/"
Manifest.db.relativePath:     Message/Media/JID/a/b/file.opus
                                    ↓ получаем fileID
fileID (SHA1):                147e61ac155853828d38...
                                    ↓ первые 2 символа
Путь в бэкапе:                14/147e61ac155853828d38...
```

## Имена в групповых чатах

Проблема: `ZFROMJID` в групповых чатах содержит ID группы, а не отправителя.

Решение: Использовать `ZGROUPMEMBER` → `ZWAGROUPMEMBER.ZMEMBERJID`:

```python
SELECT m.*, gm.ZMEMBERJID
FROM ZWAMESSAGE m
LEFT JOIN ZWAGROUPMEMBER gm ON m.ZGROUPMEMBER = gm.Z_PK
WHERE m.ZCHATSESSION = ?
```

## Структура результата

```
D:/Downloads/экспорт чатов с ватсапа/
├── CLAUDE.md                    # Описание экспорта
├── changelog.md                 # История изменений
├── _СТАТИСТИКА.txt              # Итоговая статистика
├── ChatStorage.sqlite           # Копия базы данных
├── ContactsV2.sqlite            # Копия контактов
│
├── Аббас_971585211777/          # Личный чат (имя из адресной книги)
│   ├── chat.txt
│   └── media/
│       ├── 123_photo.jpg
│       └── 456_voice.opus
│
├── Ямина (мама)_971545245585/   # Имя из имени чата
│   ├── chat.txt
│   └── media/
│
├── Семья 🕺🏼🕺🏼🕺🏼_971522911765-1546491/  # Групповой чат
│   ├── chat.txt                 # С именами участников!
│   └── media/
│
└── B2B - Marsel VIP DXB_971507705321-1571721/
    ├── chat.txt
    └── media/
```

## Формат chat.txt (экспортированный)

```
============================================================
ЧАТ: [Имя чата]
JID: [jid]@s.whatsapp.net или @g.us
Сообщений: [число]
Экспорт: DD.MM.YYYY HH:MM:SS
[ИСПРАВЛЕНО: имена участников группы]  # только для групп
============================================================

[DD.MM.YYYY HH:MM:SS] [Отправитель]:
  [текст сообщения]
  [медиа] media/filename или (медиа не сохранено в бэкапе)
```
