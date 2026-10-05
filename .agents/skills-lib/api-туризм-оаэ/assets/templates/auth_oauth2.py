"""
OAuth 2.0 Authentication Template
Шаблон для аутентификации через OAuth 2.0

Использование:
    python auth_oauth2.py

Требования:
    pip install requests requests-oauthlib
"""

import os
import json
import time
from typing import Optional, Dict
from dataclasses import dataclass
import requests
from requests_oauthlib import OAuth2Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= OAuth2 Configuration =============

@dataclass
class OAuth2Config:
    """Конфигурация OAuth2"""
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    redirect_uri: str
    scope: list

# Примеры конфигураций популярных сервисов
GOOGLE_CONFIG = OAuth2Config(
    client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
    token_url="https://oauth2.googleapis.com/token",
    redirect_uri="http://localhost:8000/callback",
    scope=["openid", "email", "profile"]
)

BOOKING_CONFIG = OAuth2Config(
    client_id=os.getenv("BOOKING_CLIENT_ID", ""),
    client_secret=os.getenv("BOOKING_CLIENT_SECRET", ""),
    authorization_url="https://account.booking.com/oauth2/authorize",
    token_url="https://account.booking.com/oauth2/token",
    redirect_uri="http://localhost:8000/callback",
    scope=["read:properties", "write:bookings"]
)

# ============= Token Storage =============

class TokenStorage:
    """Хранение токенов (в файле для простоты)"""

    def __init__(self, filepath: str = "oauth_tokens.json"):
        self.filepath = filepath

    def save(self, tokens: Dict):
        with open(self.filepath, "w") as f:
            json.dump(tokens, f)
        logger.info("Tokens saved")

    def load(self) -> Optional[Dict]:
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def delete(self):
        try:
            os.remove(self.filepath)
        except FileNotFoundError:
            pass

# ============= OAuth2 Client =============

class OAuth2Client:
    """Клиент для OAuth 2.0 аутентификации"""

    def __init__(self, config: OAuth2Config, storage: Optional[TokenStorage] = None):
        self.config = config
        self.storage = storage or TokenStorage()
        self.token = self.storage.load()

    def get_authorization_url(self) -> tuple:
        """Получить URL для авторизации пользователя"""
        oauth = OAuth2Session(
            self.config.client_id,
            redirect_uri=self.config.redirect_uri,
            scope=self.config.scope
        )

        authorization_url, state = oauth.authorization_url(
            self.config.authorization_url,
            access_type="offline",  # Для получения refresh_token
            prompt="consent"
        )

        return authorization_url, state

    def fetch_token(self, authorization_response: str) -> Dict:
        """Обменять authorization code на access token"""
        oauth = OAuth2Session(
            self.config.client_id,
            redirect_uri=self.config.redirect_uri
        )

        token = oauth.fetch_token(
            self.config.token_url,
            authorization_response=authorization_response,
            client_secret=self.config.client_secret
        )

        self.token = token
        self.storage.save(token)
        return token

    def refresh_token(self) -> Dict:
        """Обновить access token используя refresh token"""
        if not self.token or "refresh_token" not in self.token:
            raise ValueError("No refresh token available")

        oauth = OAuth2Session(self.config.client_id, token=self.token)

        new_token = oauth.refresh_token(
            self.config.token_url,
            client_id=self.config.client_id,
            client_secret=self.config.client_secret
        )

        self.token = new_token
        self.storage.save(new_token)
        return new_token

    def is_token_expired(self) -> bool:
        """Проверить истёк ли токен"""
        if not self.token:
            return True

        expires_at = self.token.get("expires_at", 0)
        return time.time() > expires_at - 300  # 5 минут до истечения

    def get_access_token(self) -> str:
        """Получить актуальный access token"""
        if self.is_token_expired():
            logger.info("Token expired, refreshing...")
            self.refresh_token()

        return self.token["access_token"]

    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Выполнить запрос с OAuth2 аутентификацией"""
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.get_access_token()}"

        response = requests.request(method, url, headers=headers, **kwargs)

        # Если получили 401, попробовать обновить токен
        if response.status_code == 401:
            logger.info("Got 401, refreshing token...")
            self.refresh_token()
            headers["Authorization"] = f"Bearer {self.get_access_token()}"
            response = requests.request(method, url, headers=headers, **kwargs)

        return response

    def get(self, url: str, **kwargs) -> Dict:
        response = self.make_request("GET", url, **kwargs)
        response.raise_for_status()
        return response.json()

    def post(self, url: str, **kwargs) -> Dict:
        response = self.make_request("POST", url, **kwargs)
        response.raise_for_status()
        return response.json()

# ============= FastAPI Integration =============

def create_oauth_routes(app, client: OAuth2Client, callback_handler=None):
    """Добавить OAuth routes в FastAPI приложение"""
    from fastapi import FastAPI
    from fastapi.responses import RedirectResponse

    @app.get("/login")
    async def login():
        """Перенаправление на страницу авторизации"""
        auth_url, state = client.get_authorization_url()
        return RedirectResponse(auth_url)

    @app.get("/callback")
    async def callback(code: str = None, state: str = None, error: str = None):
        """Обработка callback после авторизации"""
        if error:
            return {"error": error}

        # Собираем полный URL
        from starlette.requests import Request
        # В реальном приложении используйте request.url

        authorization_response = f"http://localhost:8000/callback?code={code}&state={state}"

        token = client.fetch_token(authorization_response)

        if callback_handler:
            return callback_handler(token)

        return {"status": "authenticated", "token_type": token["token_type"]}

    @app.get("/logout")
    async def logout():
        """Выход из системы"""
        client.storage.delete()
        client.token = None
        return {"status": "logged out"}

# ============= Client Credentials Flow =============

class ClientCredentialsClient:
    """OAuth2 Client Credentials Grant (server-to-server)"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: Optional[list] = None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.scope = scope or []
        self.token = None
        self.token_expires_at = 0

    def fetch_token(self) -> str:
        """Получить access token"""
        response = requests.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": " ".join(self.scope)
            }
        )
        response.raise_for_status()

        data = response.json()
        self.token = data["access_token"]
        self.token_expires_at = time.time() + data.get("expires_in", 3600)

        return self.token

    def get_access_token(self) -> str:
        """Получить актуальный access token"""
        if not self.token or time.time() > self.token_expires_at - 300:
            self.fetch_token()
        return self.token

# ============= Usage Example =============

if __name__ == "__main__":
    # Пример: Authorization Code Flow
    print("=== OAuth2 Authorization Code Flow ===\n")

    client = OAuth2Client(GOOGLE_CONFIG)

    # Шаг 1: Получить URL авторизации
    auth_url, state = client.get_authorization_url()
    print(f"1. Откройте в браузере:\n{auth_url}\n")

    # Шаг 2: После авторизации пользователь будет перенаправлен на callback URL
    # В реальном приложении это обрабатывается в FastAPI/Flask

    print("2. После авторизации введите полный redirect URL:")
    # redirect_url = input("> ")
    # token = client.fetch_token(redirect_url)
    # print(f"3. Токен получен: {token['token_type']}")

    # Шаг 3: Использовать токен для запросов
    # user_info = client.get("https://www.googleapis.com/oauth2/v2/userinfo")
    # print(f"User: {user_info['email']}")

    print("\n=== OAuth2 Client Credentials Flow ===\n")

    # Пример: Client Credentials (server-to-server)
    cc_client = ClientCredentialsClient(
        client_id=os.getenv("CLIENT_ID", "test"),
        client_secret=os.getenv("CLIENT_SECRET", "test"),
        token_url="https://auth.example.com/oauth/token",
        scope=["read", "write"]
    )

    # token = cc_client.get_access_token()
    # print(f"Access token: {token[:20]}...")
