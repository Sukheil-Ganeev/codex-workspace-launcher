#!/usr/bin/env python3
"""
YouTube Video Uploader with Resumable Upload
Python helper для загрузки видео на YouTube через Data API v3
Версия: 1.0 (2026-02-05)
"""

import os
import sys
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle

# Scopes для YouTube API
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

class YouTubeUploader:
    def __init__(self, client_secrets_file='client_secret.json', credentials_file='token.pickle'):
        """
        Инициализация YouTube Uploader

        Args:
            client_secrets_file: Путь к client_secret.json
            credentials_file: Путь к сохраненным credentials
        """
        self.client_secrets_file = client_secrets_file
        self.credentials_file = credentials_file
        self.youtube = None
        self._authenticate()

    def _authenticate(self):
        """Аутентификация через OAuth 2.0"""
        credentials = None

        # Проверяем сохраненные credentials
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'rb') as token:
                credentials = pickle.load(token)

        # Если credentials нет или истекли
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                # Обновляем токен
                credentials.refresh(Request())
            else:
                # Запускаем OAuth flow
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, SCOPES)
                credentials = flow.run_local_server(port=0)

            # Сохраняем credentials для следующего использования
            with open(self.credentials_file, 'wb') as token:
                pickle.dump(credentials, token)

        # Создаем YouTube API client
        self.youtube = googleapiclient.discovery.build(
            'youtube', 'v3', credentials=credentials)

    def upload_video(self, video_file, title, description, tags=None, category_id='19',
                    privacy_status='public', notify_subscribers=True):
        """
        Загрузка видео на YouTube

        Args:
            video_file: Путь к видео файлу
            title: Название видео (до 100 символов)
            description: Описание видео (до 5000 символов)
            tags: Список тегов (опционально)
            category_id: ID категории (19 = Travel & Events)
            privacy_status: public, private, unlisted
            notify_subscribers: Уведомлять подписчиков

        Returns:
            dict: Информация о загруженном видео
        """

        # Проверка файла
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Видео файл не найден: {video_file}")

        # Метаданные видео
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
            }
        }

        # Не уведомлять подписчиков если указано
        if not notify_subscribers:
            body['status']['publishAt'] = None

        # Резюмируемая загрузка (chunks)
        media = MediaFileUpload(
            video_file,
            chunksize=10*1024*1024,  # 10 MB chunks
            resumable=True
        )

        # Создаем запрос
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media,
            notifySubscribers=notify_subscribers
        )

        print(f"Загрузка видео: {title}")
        print(f"Файл: {video_file}")
        print(f"Размер: {os.path.getsize(video_file) / (1024*1024):.2f} MB")
        print("-" * 50)

        # Загрузка с прогрессом
        response = None
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"Загружено: {progress}%", end='\r')
            except googleapiclient.errors.HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    # Повторяем при серверных ошибках
                    print(f"\nСерверная ошибка {e.resp.status}, повторяю...")
                    continue
                else:
                    raise

        print("\n" + "-" * 50)
        print(f"✅ Видео успешно загружено!")
        print(f"Video ID: {response['id']}")
        print(f"URL: https://youtube.com/watch?v={response['id']}")

        return response

    def upload_short(self, video_file, title, description, tags=None):
        """
        Загрузка YouTube Short

        ВАЖНО: YouTube автоматически определит Short по:
        - Длительность < 60 секунд
        - Вертикальный формат (9:16 aspect ratio)

        Args:
            video_file: Путь к короткому вертикальному видео
            title: Название Short
            description: Описание (добавьте #Shorts в описание!)
            tags: Список тегов

        Returns:
            dict: Информация о загруженном Short
        """

        # Добавляем #Shorts в описание если нет
        if '#Shorts' not in description and '#shorts' not in description:
            description += '\n\n#Shorts'

        # Добавляем 'Shorts' в теги
        if tags is None:
            tags = []
        if 'Shorts' not in tags:
            tags.append('Shorts')

        return self.upload_video(
            video_file=video_file,
            title=title,
            description=description,
            tags=tags,
            category_id='19',  # Travel & Events
            privacy_status='public'
        )


def main():
    """Пример использования"""

    # Проверка аргументов
    if len(sys.argv) < 4:
        print("Использование:")
        print("  python video-uploader.py <video_file> <title> <description> [tags]")
        print("\nПример:")
        print('  python video-uploader.py dubai_tour.mp4 "Dubai Tour 2026" "Amazing tour description" "dubai,tourism,uae"')
        sys.exit(1)

    video_file = sys.argv[1]
    title = sys.argv[2]
    description = sys.argv[3]
    tags = sys.argv[4].split(',') if len(sys.argv) > 4 else []

    # Создаем uploader
    uploader = YouTubeUploader()

    # Загружаем видео
    result = uploader.upload_video(
        video_file=video_file,
        title=title,
        description=description,
        tags=tags
    )

    print(f"\nВидео ID: {result['id']}")


if __name__ == '__main__':
    main()

# Пример использования в коде:
"""
from video_uploader import YouTubeUploader

uploader = YouTubeUploader()

# Загрузка обычного видео
result = uploader.upload_video(
    video_file='desert_safari.mp4',
    title='Dubai Desert Safari 2026 - Ultimate Experience',
    description='Experience the thrill of Dubai desert! Book now: +971 50 123 4567',
    tags=['Dubai', 'Desert Safari', 'Tourism', 'UAE'],
    privacy_status='public'
)

# Загрузка Short
short_result = uploader.upload_short(
    video_file='burj_khalifa_30s.mp4',
    title='Burj Khalifa View 🏙️ #Shorts',
    description='Amazing view from the top! #Dubai #BurjKhalifa #Shorts',
    tags=['Dubai', 'Burj Khalifa', 'Shorts']
)
"""
