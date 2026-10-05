"""
Universal Image Downloader
Скачивание изображений с бесплатных стоков: Unsplash, Pexels, Pixabay

Автор: Claude Code
Версия: 1.0
"""

import requests
import os
import json
from typing import Optional, List, Dict
from pathlib import Path


class ImageDownloader:
    """Универсальный загрузчик изображений с бесплатных стоков"""

    def __init__(
        self,
        unsplash_key: Optional[str] = None,
        pexels_key: Optional[str] = None,
        pixabay_key: Optional[str] = None,
        output_dir: str = "./images"
    ):
        self.unsplash_key = unsplash_key
        self.pexels_key = pexels_key
        self.pixabay_key = pixabay_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # API endpoints
        self.apis = {
            "unsplash": {
                "search": "https://api.unsplash.com/search/photos",
                "random": "https://api.unsplash.com/photos/random",
            },
            "pexels": {
                "search": "https://api.pexels.com/v1/search",
                "curated": "https://api.pexels.com/v1/curated",
            },
            "pixabay": {
                "search": "https://pixabay.com/api/",
            }
        }

    # ==================== UNSPLASH ====================

    def search_unsplash(self, query: str, per_page: int = 10, page: int = 1) -> List[Dict]:
        """
        Поиск изображений на Unsplash

        Args:
            query: Поисковый запрос
            per_page: Количество результатов (макс 30)
            page: Номер страницы

        Returns:
            Список изображений с URL и метаданными
        """
        if not self.unsplash_key:
            raise ValueError("Unsplash API key not set")

        response = requests.get(
            self.apis["unsplash"]["search"],
            params={
                "query": query,
                "per_page": min(per_page, 30),
                "page": page,
                "client_id": self.unsplash_key
            }
        )

        if response.status_code != 200:
            print(f"Unsplash API error: {response.status_code}")
            return []

        data = response.json()
        results = []

        for photo in data.get("results", []):
            results.append({
                "id": photo["id"],
                "source": "unsplash",
                "description": photo.get("description") or photo.get("alt_description", ""),
                "photographer": photo["user"]["name"],
                "urls": {
                    "raw": photo["urls"]["raw"],
                    "full": photo["urls"]["full"],
                    "regular": photo["urls"]["regular"],  # 1080px
                    "small": photo["urls"]["small"],      # 400px
                    "thumb": photo["urls"]["thumb"],      # 200px
                },
                "width": photo["width"],
                "height": photo["height"],
            })

        return results

    # ==================== PEXELS ====================

    def search_pexels(self, query: str, per_page: int = 10, page: int = 1) -> List[Dict]:
        """
        Поиск изображений на Pexels

        Args:
            query: Поисковый запрос
            per_page: Количество результатов (макс 80)
            page: Номер страницы

        Returns:
            Список изображений с URL и метаданными
        """
        if not self.pexels_key:
            raise ValueError("Pexels API key not set")

        response = requests.get(
            self.apis["pexels"]["search"],
            params={
                "query": query,
                "per_page": min(per_page, 80),
                "page": page,
            },
            headers={"Authorization": self.pexels_key}
        )

        if response.status_code != 200:
            print(f"Pexels API error: {response.status_code}")
            return []

        data = response.json()
        results = []

        for photo in data.get("photos", []):
            results.append({
                "id": photo["id"],
                "source": "pexels",
                "description": photo.get("alt", ""),
                "photographer": photo["photographer"],
                "urls": {
                    "original": photo["src"]["original"],
                    "large2x": photo["src"]["large2x"],   # 940px x 2
                    "large": photo["src"]["large"],       # 940px
                    "medium": photo["src"]["medium"],     # 350px
                    "small": photo["src"]["small"],       # 130px
                    "portrait": photo["src"]["portrait"], # 800x1200
                    "landscape": photo["src"]["landscape"], # 1200x627
                },
                "width": photo["width"],
                "height": photo["height"],
            })

        return results

    # ==================== PIXABAY ====================

    def search_pixabay(self, query: str, per_page: int = 10, page: int = 1) -> List[Dict]:
        """
        Поиск изображений на Pixabay

        Args:
            query: Поисковый запрос
            per_page: Количество результатов (макс 200)
            page: Номер страницы

        Returns:
            Список изображений с URL и метаданными
        """
        if not self.pixabay_key:
            raise ValueError("Pixabay API key not set")

        response = requests.get(
            self.apis["pixabay"]["search"],
            params={
                "key": self.pixabay_key,
                "q": query,
                "per_page": min(per_page, 200),
                "page": page,
                "image_type": "photo",
                "safesearch": "true",
            }
        )

        if response.status_code != 200:
            print(f"Pixabay API error: {response.status_code}")
            return []

        data = response.json()
        results = []

        for photo in data.get("hits", []):
            results.append({
                "id": photo["id"],
                "source": "pixabay",
                "description": photo.get("tags", ""),
                "photographer": photo["user"],
                "urls": {
                    "large": photo["largeImageURL"],      # 1280px
                    "web": photo["webformatURL"],         # 640px
                    "preview": photo["previewURL"],       # 150px
                },
                "width": photo["imageWidth"],
                "height": photo["imageHeight"],
            })

        return results

    # ==================== UNIFIED SEARCH ====================

    def search_all(self, query: str, per_page: int = 5) -> List[Dict]:
        """
        Поиск по всем доступным источникам

        Args:
            query: Поисковый запрос
            per_page: Количество результатов с каждого источника

        Returns:
            Объединённый список изображений
        """
        results = []

        if self.unsplash_key:
            try:
                results.extend(self.search_unsplash(query, per_page))
                print(f"[Unsplash] Found {len(results)} images")
            except Exception as e:
                print(f"[Unsplash] Error: {e}")

        if self.pexels_key:
            try:
                pexels_results = self.search_pexels(query, per_page)
                results.extend(pexels_results)
                print(f"[Pexels] Found {len(pexels_results)} images")
            except Exception as e:
                print(f"[Pexels] Error: {e}")

        if self.pixabay_key:
            try:
                pixabay_results = self.search_pixabay(query, per_page)
                results.extend(pixabay_results)
                print(f"[Pixabay] Found {len(pixabay_results)} images")
            except Exception as e:
                print(f"[Pixabay] Error: {e}")

        return results

    # ==================== DOWNLOAD ====================

    def download_image(
        self,
        url: str,
        filename: str,
        size: str = "regular"
    ) -> Optional[str]:
        """
        Скачивание изображения по URL

        Args:
            url: URL изображения
            filename: Имя файла для сохранения
            size: Размер (для некоторых API)

        Returns:
            Путь к сохранённому файлу или None
        """
        try:
            response = requests.get(url, stream=True, timeout=30)

            if response.status_code != 200:
                print(f"Download failed: {response.status_code}")
                return None

            # Определяем расширение
            content_type = response.headers.get("content-type", "")
            if "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            elif "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"
            else:
                ext = ".jpg"  # default

            # Добавляем расширение если нет
            if not filename.endswith(ext) and "." not in filename:
                filename = filename + ext

            filepath = self.output_dir / filename

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"Download error: {e}")
            return None

    def search_and_download(
        self,
        query: str,
        filename: str,
        source: str = "all",
        size: str = "regular"
    ) -> Optional[str]:
        """
        Поиск и скачивание первого подходящего изображения

        Args:
            query: Поисковый запрос
            filename: Имя файла для сохранения
            source: Источник (unsplash, pexels, pixabay, all)
            size: Размер изображения

        Returns:
            Путь к сохранённому файлу или None
        """
        results = []

        if source == "all":
            results = self.search_all(query, per_page=3)
        elif source == "unsplash" and self.unsplash_key:
            results = self.search_unsplash(query, per_page=3)
        elif source == "pexels" and self.pexels_key:
            results = self.search_pexels(query, per_page=3)
        elif source == "pixabay" and self.pixabay_key:
            results = self.search_pixabay(query, per_page=3)

        if not results:
            print(f"No images found for: {query}")
            return None

        # Берём первый результат
        image = results[0]

        # Выбираем URL в зависимости от размера и источника
        url = None
        if image["source"] == "unsplash":
            size_map = {"thumb": "thumb", "small": "small", "regular": "regular", "full": "full", "raw": "raw"}
            url = image["urls"].get(size_map.get(size, "regular"))
        elif image["source"] == "pexels":
            size_map = {"thumb": "small", "small": "medium", "regular": "large", "full": "large2x", "raw": "original"}
            url = image["urls"].get(size_map.get(size, "large"))
        elif image["source"] == "pixabay":
            size_map = {"thumb": "preview", "small": "preview", "regular": "web", "full": "large", "raw": "large"}
            url = image["urls"].get(size_map.get(size, "large"))

        if not url:
            url = list(image["urls"].values())[0]

        return self.download_image(url, filename)


# ==================== CLI ====================

def main():
    """Пример использования"""
    import argparse

    parser = argparse.ArgumentParser(description="Download images from free stock APIs")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-o", "--output", default="downloaded_image", help="Output filename")
    parser.add_argument("-s", "--source", default="all", choices=["unsplash", "pexels", "pixabay", "all"])
    parser.add_argument("--size", default="regular", choices=["thumb", "small", "regular", "full", "raw"])
    parser.add_argument("--dir", default="./images", help="Output directory")

    args = parser.parse_args()

    # Загружаем ключи из переменных окружения
    downloader = ImageDownloader(
        unsplash_key=os.environ.get("UNSPLASH_ACCESS_KEY"),
        pexels_key=os.environ.get("PEXELS_API_KEY"),
        pixabay_key=os.environ.get("PIXABAY_API_KEY"),
        output_dir=args.dir
    )

    result = downloader.search_and_download(
        query=args.query,
        filename=args.output,
        source=args.source,
        size=args.size
    )

    if result:
        print(f"\nSuccess! Image saved to: {result}")
    else:
        print("\nFailed to download image")


if __name__ == "__main__":
    main()
