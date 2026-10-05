# Python скрипт экспорта WhatsApp из iTunes бэкапа

Полный скрипт для массового экспорта чатов, сообщений и медиафайлов из резервной копии iPhone.

---

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Экспорт WhatsApp из iTunes бэкапа iPhone
"""

import sqlite3
import os
import shutil
from datetime import datetime, timedelta

BACKUP_PATH = r"C:/Users/londo/AppData/Roaming/Apple Computer/MobileSync/Backup/[DEVICE_ID]"
MANIFEST_DB = os.path.join(BACKUP_PATH, "Manifest.db")

def apple_timestamp_to_datetime(timestamp):
    """Apple Core Data timestamp → datetime"""
    if not timestamp:
        return None
    return datetime(2001, 1, 1) + timedelta(seconds=timestamp)

def get_file_path_in_backup(file_id):
    """fileID → путь в бэкапе"""
    return os.path.join(BACKUP_PATH, file_id[:2], file_id)

def build_media_index(manifest_conn, domain):
    """Индекс медиафайлов из Manifest.db"""
    cursor = manifest_conn.cursor()
    cursor.execute("""
        SELECT fileID, relativePath FROM Files
        WHERE domain = ? AND relativePath LIKE 'Message/Media/%'
    """, (domain,))

    media_index = {}
    for file_id, rel_path in cursor.fetchall():
        if rel_path.startswith("Message/"):
            media_index[rel_path[8:]] = file_id  # Убираем "Message/"
    return media_index

def load_contacts(contacts_db_path):
    """Загрузка имён из адресной книги"""
    contacts = {}
    conn = sqlite3.connect(contacts_db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ZWHATSAPPID, ZFULLNAME FROM ZWAADDRESSBOOKCONTACT
        WHERE ZWHATSAPPID IS NOT NULL AND ZFULLNAME IS NOT NULL
    """)
    for jid, name in cursor.fetchall():
        contacts[jid] = name.strip()
    conn.close()
    return contacts

def export_chats(chat_db_path, output_dir, media_index, contacts):
    """Экспорт всех чатов"""
    conn = sqlite3.connect(chat_db_path)
    cursor = conn.cursor()

    # Получаем все чаты
    cursor.execute("""
        SELECT Z_PK, ZCONTACTJID, ZPARTNERNAME
        FROM ZWACHATSESSION WHERE ZCONTACTJID IS NOT NULL
    """)

    for chat_pk, jid, partner_name in cursor.fetchall():
        # Определяем имя
        name = contacts.get(jid) or partner_name or jid.split('@')[0]

        # Создаём папку
        chat_folder = os.path.join(output_dir, f"{name}_{jid.split('@')[0][:20]}")
        os.makedirs(chat_folder, exist_ok=True)
        media_folder = os.path.join(chat_folder, "media")
        os.makedirs(media_folder, exist_ok=True)

        # Получаем сообщения с участниками групп
        msg_cursor = conn.cursor()
        msg_cursor.execute("""
            SELECT m.ZMESSAGEDATE, m.ZISFROMME, m.ZTEXT,
                   gm.ZMEMBERJID, mi.ZMEDIALOCALPATH
            FROM ZWAMESSAGE m
            LEFT JOIN ZWAGROUPMEMBER gm ON m.ZGROUPMEMBER = gm.Z_PK
            LEFT JOIN ZWAMEDIAITEM mi ON m.ZMEDIAITEM = mi.Z_PK
            WHERE m.ZCHATSESSION = ?
            ORDER BY m.ZMESSAGEDATE
        """, (chat_pk,))

        # Записываем чат
        with open(os.path.join(chat_folder, "chat.txt"), 'w', encoding='utf-8') as f:
            f.write(f"ЧАТ: {name}\nJID: {jid}\n{'='*50}\n\n")

            for msg_date, is_from_me, text, member_jid, media_path in msg_cursor:
                dt = apple_timestamp_to_datetime(msg_date)
                date_str = dt.strftime("%d.%m.%Y %H:%M:%S") if dt else "???"

                # Определяем отправителя
                if is_from_me:
                    sender = "Я"
                elif member_jid:
                    sender = contacts.get(member_jid) or member_jid.split('@')[0]
                else:
                    sender = name

                f.write(f"[{date_str}] {sender}:\n")
                if text:
                    f.write(f"  {text}\n")

                # Копируем медиа
                if media_path and media_path in media_index:
                    file_id = media_index[media_path]
                    src = get_file_path_in_backup(file_id)
                    if os.path.exists(src):
                        dst = os.path.join(media_folder, os.path.basename(media_path))
                        shutil.copy2(src, dst)
                        f.write(f"  [медиа] media/{os.path.basename(media_path)}\n")

                f.write("\n")

    conn.close()
```
