#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тепловая карта клиентов - визуализация географии туристов по номерам телефонов.

Функции:
- Определение страны по номеру телефона (phonenumbers)
- Статистика по странам (топ-10, динамика)
- Интерактивная карта (Folium)
- Экспорт в HTML/PNG/JSON/CSV
- Интеграция с profiles.json
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Any, Tuple
import hashlib

sys.stdout.reconfigure(encoding='utf-8')

# Попытка импорта библиотек
try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
    from phonenumbers.phonenumberutil import NumberParseException
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    print("[!] Библиотека phonenumbers не установлена. pip install phonenumbers")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("[!] Библиотека pandas не установлена. pip install pandas")

try:
    import folium
    from folium.plugins import HeatMap, MarkerCluster
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("[!] Библиотека folium не установлена. pip install folium")

try:
    from branca.colormap import linear
    BRANCA_AVAILABLE = True
except ImportError:
    BRANCA_AVAILABLE = False

# Опциональные библиотеки для PNG экспорта
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Пути по умолчанию
CONTACTS_FILE = Path("D:/Downloads/Chats/_база/json/contacts.json")
PROFILES_FILE = Path("D:/Downloads/Chats/_база/json/profiles.json")
OUTPUT_DIR = Path("D:/Downloads/Chats/_аналитика/heatmaps")
CACHE_FILE = Path("D:/Downloads/Chats/_база/json/phone_country_cache.json")

# Центр карты по умолчанию (Дубай)
DEFAULT_CENTER = [25.2048, 55.2708]
DEFAULT_ZOOM = 2

# Координаты стран для choropleth
COUNTRY_COORDINATES = {
    "Russia": {"lat": 61.52, "lon": 105.32, "name_ru": "Россия"},
    "Kazakhstan": {"lat": 48.02, "lon": 66.92, "name_ru": "Казахстан"},
    "Ukraine": {"lat": 48.38, "lon": 31.17, "name_ru": "Украина"},
    "Belarus": {"lat": 53.71, "lon": 27.95, "name_ru": "Беларусь"},
    "Uzbekistan": {"lat": 41.38, "lon": 64.59, "name_ru": "Узбекистан"},
    "Azerbaijan": {"lat": 40.14, "lon": 47.58, "name_ru": "Азербайджан"},
    "Armenia": {"lat": 40.07, "lon": 45.04, "name_ru": "Армения"},
    "Georgia": {"lat": 42.32, "lon": 43.36, "name_ru": "Грузия"},
    "Turkmenistan": {"lat": 38.97, "lon": 59.56, "name_ru": "Туркменистан"},
    "Tajikistan": {"lat": 38.86, "lon": 71.28, "name_ru": "Таджикистан"},
    "Kyrgyzstan": {"lat": 41.20, "lon": 74.77, "name_ru": "Киргизия"},
    "Moldova": {"lat": 47.41, "lon": 28.37, "name_ru": "Молдова"},
    "United Arab Emirates": {"lat": 23.42, "lon": 53.85, "name_ru": "ОАЭ"},
    "Germany": {"lat": 51.17, "lon": 10.45, "name_ru": "Германия"},
    "United Kingdom": {"lat": 55.38, "lon": -3.44, "name_ru": "Великобритания"},
    "United States": {"lat": 37.09, "lon": -95.71, "name_ru": "США"},
    "France": {"lat": 46.23, "lon": 2.21, "name_ru": "Франция"},
    "Italy": {"lat": 41.87, "lon": 12.57, "name_ru": "Италия"},
    "Spain": {"lat": 40.46, "lon": -3.75, "name_ru": "Испания"},
    "Turkey": {"lat": 38.96, "lon": 35.24, "name_ru": "Турция"},
    "Israel": {"lat": 31.05, "lon": 34.85, "name_ru": "Израиль"},
    "India": {"lat": 20.59, "lon": 78.96, "name_ru": "Индия"},
    "China": {"lat": 35.86, "lon": 104.20, "name_ru": "Китай"},
    "Saudi Arabia": {"lat": 23.89, "lon": 45.08, "name_ru": "Саудовская Аравия"},
    "Iran": {"lat": 32.43, "lon": 53.69, "name_ru": "Иран"},
    "Pakistan": {"lat": 30.38, "lon": 69.35, "name_ru": "Пакистан"},
    "Egypt": {"lat": 26.82, "lon": 30.80, "name_ru": "Египет"},
    "Poland": {"lat": 51.92, "lon": 19.15, "name_ru": "Польша"},
    "Czech Republic": {"lat": 49.82, "lon": 15.47, "name_ru": "Чехия"},
    "Latvia": {"lat": 56.88, "lon": 24.60, "name_ru": "Латвия"},
    "Lithuania": {"lat": 55.17, "lon": 23.88, "name_ru": "Литва"},
    "Estonia": {"lat": 58.60, "lon": 25.01, "name_ru": "Эстония"},
    "Finland": {"lat": 61.92, "lon": 25.75, "name_ru": "Финляндия"},
    "Sweden": {"lat": 60.13, "lon": 18.64, "name_ru": "Швеция"},
    "Norway": {"lat": 60.47, "lon": 8.47, "name_ru": "Норвегия"},
    "Netherlands": {"lat": 52.13, "lon": 5.29, "name_ru": "Нидерланды"},
    "Belgium": {"lat": 50.50, "lon": 4.47, "name_ru": "Бельгия"},
    "Switzerland": {"lat": 46.82, "lon": 8.23, "name_ru": "Швейцария"},
    "Austria": {"lat": 47.52, "lon": 14.55, "name_ru": "Австрия"},
    "Canada": {"lat": 56.13, "lon": -106.35, "name_ru": "Канада"},
    "Australia": {"lat": -25.27, "lon": 133.78, "name_ru": "Австралия"},
    "Japan": {"lat": 36.20, "lon": 138.25, "name_ru": "Япония"},
    "South Korea": {"lat": 35.91, "lon": 127.77, "name_ru": "Южная Корея"},
    "Brazil": {"lat": -14.24, "lon": -51.93, "name_ru": "Бразилия"},
    "Argentina": {"lat": -38.42, "lon": -63.62, "name_ru": "Аргентина"},
    "Mexico": {"lat": 23.63, "lon": -102.55, "name_ru": "Мексика"},
}

# ISO коды стран для GeoJSON
COUNTRY_ISO_CODES = {
    "Russia": "RUS",
    "Kazakhstan": "KAZ",
    "Ukraine": "UKR",
    "Belarus": "BLR",
    "Uzbekistan": "UZB",
    "Azerbaijan": "AZE",
    "Armenia": "ARM",
    "Georgia": "GEO",
    "Turkmenistan": "TKM",
    "Tajikistan": "TJK",
    "Kyrgyzstan": "KGZ",
    "Moldova": "MDA",
    "United Arab Emirates": "ARE",
    "Germany": "DEU",
    "United Kingdom": "GBR",
    "United States": "USA",
    "France": "FRA",
    "Italy": "ITA",
    "Spain": "ESP",
    "Turkey": "TUR",
    "Israel": "ISR",
    "India": "IND",
    "China": "CHN",
    "Saudi Arabia": "SAU",
    "Iran": "IRN",
    "Pakistan": "PAK",
    "Egypt": "EGY",
    "Poland": "POL",
    "Czech Republic": "CZE",
    "Latvia": "LVA",
    "Lithuania": "LTU",
    "Estonia": "EST",
    "Finland": "FIN",
    "Sweden": "SWE",
    "Norway": "NOR",
    "Netherlands": "NLD",
    "Belgium": "BEL",
    "Switzerland": "CHE",
    "Austria": "AUT",
    "Canada": "CAN",
    "Australia": "AUS",
    "Japan": "JPN",
    "South Korea": "KOR",
    "Brazil": "BRA",
    "Argentina": "ARG",
    "Mexico": "MEX",
}

# ═══════════════════════════════════════════════════════════════
# КЛАСС КЭШИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════

class PhoneCountryCache:
    """Кэш для результатов определения страны по номеру телефона."""

    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self.cache: Dict[str, Dict] = {}
        self.load()

    def load(self):
        """Загрузка кэша из файла."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"[+] Загружен кэш: {len(self.cache)} записей")
            except Exception as e:
                print(f"[!] Ошибка загрузки кэша: {e}")
                self.cache = {}

    def save(self):
        """Сохранение кэша в файл."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def get(self, phone: str) -> Optional[Dict]:
        """Получение данных из кэша."""
        # Нормализуем номер для ключа
        key = self._normalize_key(phone)
        return self.cache.get(key)

    def set(self, phone: str, data: Dict):
        """Сохранение данных в кэш."""
        key = self._normalize_key(phone)
        self.cache[key] = data

    def _normalize_key(self, phone: str) -> str:
        """Нормализация номера для использования как ключа."""
        # Убираем все кроме цифр и +
        return re.sub(r'[^\d+]', '', phone)


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ОПРЕДЕЛЕНИЯ СТРАНЫ
# ═══════════════════════════════════════════════════════════════

def parse_phone_number(phone: str, default_region: str = "RU") -> Optional[Dict]:
    """
    Парсинг номера телефона и определение страны/региона.

    Returns:
        Dict с полями: country, country_code, region, carrier, timezones
        или None если не удалось распарсить
    """
    if not PHONENUMBERS_AVAILABLE:
        return None

    if not phone:
        return None

    # Нормализация номера
    phone_clean = re.sub(r'[^\d+]', '', str(phone))

    # Добавляем + если нет
    if not phone_clean.startswith('+'):
        # Пробуем угадать формат
        if phone_clean.startswith('7') and len(phone_clean) == 11:
            phone_clean = '+' + phone_clean
        elif phone_clean.startswith('8') and len(phone_clean) == 11:
            phone_clean = '+7' + phone_clean[1:]
        elif phone_clean.startswith('971'):
            phone_clean = '+' + phone_clean
        else:
            phone_clean = '+' + phone_clean

    try:
        parsed = phonenumbers.parse(phone_clean, default_region)

        if not phonenumbers.is_valid_number(parsed):
            # Пробуем без региона по умолчанию
            parsed = phonenumbers.parse(phone_clean, None)
            if not phonenumbers.is_valid_number(parsed):
                return None

        # Получаем информацию
        country_code = parsed.country_code
        country_name = geocoder.country_name_for_number(parsed, "en")
        region = geocoder.description_for_number(parsed, "ru") or \
                 geocoder.description_for_number(parsed, "en")
        phone_carrier = carrier.name_for_number(parsed, "ru") or \
                        carrier.name_for_number(parsed, "en")
        tz = timezone.time_zones_for_number(parsed)

        return {
            "country": country_name,
            "country_code": country_code,
            "region": region,
            "carrier": phone_carrier,
            "timezones": list(tz) if tz else [],
            "formatted": phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            ),
            "e164": phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
        }

    except NumberParseException as e:
        return None
    except Exception as e:
        return None


def get_country_from_phone(phone: str, cache: PhoneCountryCache = None) -> Optional[Dict]:
    """
    Определение страны по номеру телефона с использованием кэша.
    """
    if not phone:
        return None

    # Проверяем кэш
    if cache:
        cached = cache.get(phone)
        if cached:
            return cached

    # Парсим номер
    result = parse_phone_number(phone)

    # Сохраняем в кэш
    if result and cache:
        cache.set(phone, result)

    return result


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def load_contacts(filepath: Path) -> List[Dict]:
    """Загрузка контактов из JSON файла."""
    if not filepath.exists():
        print(f"[!] Файл контактов не найден: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get('contacts', [])


def load_profiles(filepath: Path) -> List[Dict]:
    """Загрузка профилей из JSON файла."""
    if not filepath.exists():
        print(f"[!] Файл профилей не найден: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get('profiles', [])


def extract_phones_from_contacts(contacts: List[Dict]) -> List[Tuple[str, Dict]]:
    """
    Извлечение номеров телефонов из контактов.

    Returns:
        List of (phone, contact_data) tuples
    """
    phones = []

    for contact in contacts:
        phone = contact.get('phone') or contact.get('jid', '').split('@')[0]

        if phone:
            # Убираем @s.whatsapp.net и подобное
            phone = phone.split('@')[0]

            # Добавляем только если похоже на номер
            if re.match(r'^\+?\d{10,15}$', re.sub(r'[^\d+]', '', phone)):
                phones.append((phone, contact))

    return phones


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ СТАТИСТИКИ
# ═══════════════════════════════════════════════════════════════

def calculate_country_statistics(
    phones_data: List[Tuple[str, Dict, Dict]],
    contacts: List[Dict] = None
) -> Dict:
    """
    Расчет статистики по странам.

    Args:
        phones_data: List of (phone, contact, country_info) tuples
        contacts: Original contacts list for additional analysis

    Returns:
        Dict со статистикой
    """
    country_counts = Counter()
    region_counts = defaultdict(Counter)
    monthly_counts = defaultdict(Counter)
    country_contacts = defaultdict(list)

    for phone, contact, country_info in phones_data:
        if not country_info:
            country_counts["Unknown"] += 1
            country_contacts["Unknown"].append(contact)
            continue

        country = country_info.get('country', 'Unknown')
        region = country_info.get('region', '')

        country_counts[country] += 1
        country_contacts[country].append(contact)

        if region:
            region_counts[country][region] += 1

        # Анализ по месяцам (если есть дата первого контакта)
        first_contact = contact.get('first_contact_date') or \
                       contact.get('created_at') or \
                       contact.get('first_message_date')

        if first_contact:
            try:
                if isinstance(first_contact, str):
                    # Пробуем разные форматы
                    for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%Y-%m-%dT%H:%M:%S']:
                        try:
                            dt = datetime.strptime(first_contact[:10], fmt[:len(first_contact[:10])])
                            month_key = dt.strftime('%Y-%m')
                            monthly_counts[month_key][country] += 1
                            break
                        except:
                            continue
            except:
                pass

    # Формируем результат
    total = sum(country_counts.values())

    statistics = {
        "total_contacts": total,
        "countries_count": len([c for c in country_counts if c != "Unknown"]),
        "by_country": dict(country_counts.most_common()),
        "top_10": dict(country_counts.most_common(10)),
        "by_region": {
            country: dict(regions.most_common(10))
            for country, regions in region_counts.items()
        },
        "by_month": {
            month: dict(countries)
            for month, countries in sorted(monthly_counts.items())
        },
        "percentages": {
            country: round(count / total * 100, 2)
            for country, count in country_counts.items()
        } if total > 0 else {},
        "country_contacts": {
            country: [c.get('name', c.get('phone', 'Unknown')) for c in contacts_list[:5]]
            for country, contacts_list in country_contacts.items()
        }
    }

    return statistics


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ВИЗУАЛИЗАЦИИ
# ═══════════════════════════════════════════════════════════════

def create_interactive_map(
    statistics: Dict,
    output_file: Path,
    title: str = "Тепловая карта клиентов"
) -> Optional[Path]:
    """
    Создание интерактивной карты с Folium.

    Args:
        statistics: Статистика по странам
        output_file: Путь к выходному HTML файлу
        title: Заголовок карты

    Returns:
        Path к созданному файлу или None
    """
    if not FOLIUM_AVAILABLE:
        print("[!] Folium не установлен, карта не будет создана")
        return None

    # Создаем карту
    m = folium.Map(
        location=DEFAULT_CENTER,
        zoom_start=DEFAULT_ZOOM,
        tiles='CartoDB positron'
    )

    # Добавляем заголовок
    title_html = f'''
    <div style="position: fixed;
                top: 10px; left: 50px; width: 300px;
                background-color: white;
                border: 2px solid #ddd;
                z-index: 9999;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
        <h4 style="margin: 0 0 10px 0;">{title}</h4>
        <p style="margin: 0; font-size: 12px;">
            Всего клиентов: {statistics.get("total_contacts", 0)}<br>
            Стран: {statistics.get("countries_count", 0)}
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Подготовка данных для тепловой карты
    heat_data = []
    max_count = max(statistics.get('by_country', {}).values()) if statistics.get('by_country') else 1

    for country, count in statistics.get('by_country', {}).items():
        if country == "Unknown":
            continue

        coords = COUNTRY_COORDINATES.get(country)
        if coords:
            # Вес пропорционален количеству
            weight = count / max_count
            heat_data.append([coords['lat'], coords['lon'], weight])

    # Добавляем тепловую карту
    if heat_data:
        HeatMap(
            heat_data,
            min_opacity=0.3,
            max_val=1.0,
            radius=30,
            blur=20,
            gradient={
                0.2: 'blue',
                0.4: 'lime',
                0.6: 'yellow',
                0.8: 'orange',
                1.0: 'red'
            }
        ).add_to(m)

    # Добавляем маркеры с кластеризацией
    marker_cluster = MarkerCluster(name="Клиенты по странам").add_to(m)

    for country, count in statistics.get('by_country', {}).items():
        if country == "Unknown":
            continue

        coords = COUNTRY_COORDINATES.get(country)
        if coords:
            name_ru = coords.get('name_ru', country)
            percentage = statistics.get('percentages', {}).get(country, 0)

            # Размер маркера пропорционален количеству
            radius = min(30, max(8, count * 2))

            # Цвет зависит от количества
            if count >= 50:
                color = 'red'
            elif count >= 20:
                color = 'orange'
            elif count >= 10:
                color = 'yellow'
            else:
                color = 'green'

            # Popup с информацией
            popup_html = f"""
            <div style="width: 200px;">
                <h4>{name_ru}</h4>
                <p><b>Клиентов:</b> {count}</p>
                <p><b>Доля:</b> {percentage:.1f}%</p>
            </div>
            """

            folium.CircleMarker(
                location=[coords['lat'], coords['lon']],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{name_ru}: {count}",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(marker_cluster)

    # Добавляем легенду
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 50px;
                background-color: white;
                border: 2px solid #ddd;
                z-index: 9999;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
        <h5 style="margin: 0 0 10px 0;">Легенда</h5>
        <div><span style="color: red;">●</span> 50+ клиентов</div>
        <div><span style="color: orange;">●</span> 20-49 клиентов</div>
        <div><span style="color: #c5c500;">●</span> 10-19 клиентов</div>
        <div><span style="color: green;">●</span> 1-9 клиентов</div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Добавляем контроль слоев
    folium.LayerControl().add_to(m)

    # Сохраняем
    output_file.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(output_file))

    print(f"[+] Карта сохранена: {output_file}")
    return output_file


def create_choropleth_map(
    statistics: Dict,
    output_file: Path,
    title: str = "Choropleth карта клиентов"
) -> Optional[Path]:
    """
    Создание Choropleth карты (закрашенные страны).
    """
    if not FOLIUM_AVAILABLE:
        return None

    # URL GeoJSON с границами стран
    geo_json_url = "https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/world-countries.json"

    # Создаем карту
    m = folium.Map(
        location=DEFAULT_CENTER,
        zoom_start=DEFAULT_ZOOM,
        tiles='CartoDB positron'
    )

    # Подготовка данных для choropleth
    # Конвертируем названия стран в ISO коды
    country_data = {}
    for country, count in statistics.get('by_country', {}).items():
        iso_code = COUNTRY_ISO_CODES.get(country)
        if iso_code:
            country_data[iso_code] = count

    if country_data:
        try:
            # Создаем DataFrame для Folium
            if PANDAS_AVAILABLE:
                df = pd.DataFrame(
                    list(country_data.items()),
                    columns=['country', 'clients']
                )

                folium.Choropleth(
                    geo_data=geo_json_url,
                    name='choropleth',
                    data=df,
                    columns=['country', 'clients'],
                    key_on='feature.id',
                    fill_color='YlOrRd',
                    fill_opacity=0.7,
                    line_opacity=0.2,
                    legend_name='Количество клиентов'
                ).add_to(m)
        except Exception as e:
            print(f"[!] Ошибка создания choropleth: {e}")

    # Добавляем заголовок
    title_html = f'''
    <div style="position: fixed;
                top: 10px; left: 50px; width: 250px;
                background-color: white;
                border: 2px solid #ddd;
                z-index: 9999;
                padding: 10px;
                border-radius: 5px;">
        <h4 style="margin: 0;">{title}</h4>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    folium.LayerControl().add_to(m)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(output_file))

    print(f"[+] Choropleth карта сохранена: {output_file}")
    return output_file


def create_static_png(html_file: Path, png_file: Path) -> Optional[Path]:
    """
    Создание статичного PNG из HTML карты с помощью Selenium.
    """
    if not SELENIUM_AVAILABLE:
        print("[!] Selenium не установлен, PNG не будет создан")
        print("    pip install selenium")
        return None

    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f'file:///{html_file.absolute()}')

        # Даем карте загрузиться
        time.sleep(3)

        png_file.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(png_file))
        driver.quit()

        print(f"[+] PNG сохранен: {png_file}")
        return png_file

    except Exception as e:
        print(f"[!] Ошибка создания PNG: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ЭКСПОРТА
# ═══════════════════════════════════════════════════════════════

def export_to_json(statistics: Dict, output_file: Path) -> Path:
    """Экспорт статистики в JSON для дашборда."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    export_data = {
        "generated_at": datetime.now().isoformat(),
        "statistics": statistics,
        "visualization": {
            "chart_type": "geo_heatmap",
            "recommended_colors": ["#ffffcc", "#ffeda0", "#fed976", "#feb24c",
                                   "#fd8d3c", "#fc4e2a", "#e31a1c", "#bd0026"]
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"[+] JSON сохранен: {output_file}")
    return output_file


def export_to_csv(statistics: Dict, output_file: Path) -> Path:
    """Экспорт статистики в CSV для аналитики."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if PANDAS_AVAILABLE:
        # Основная таблица по странам
        countries_data = []
        for country, count in statistics.get('by_country', {}).items():
            coords = COUNTRY_COORDINATES.get(country, {})
            countries_data.append({
                'country': country,
                'country_ru': coords.get('name_ru', country),
                'clients': count,
                'percentage': statistics.get('percentages', {}).get(country, 0),
                'lat': coords.get('lat', ''),
                'lon': coords.get('lon', '')
            })

        df = pd.DataFrame(countries_data)
        df = df.sort_values('clients', ascending=False)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"[+] CSV сохранен: {output_file}")
    else:
        # Простой CSV без pandas
        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write("country,country_ru,clients,percentage,lat,lon\n")
            for country, count in sorted(
                statistics.get('by_country', {}).items(),
                key=lambda x: x[1],
                reverse=True
            ):
                coords = COUNTRY_COORDINATES.get(country, {})
                name_ru = coords.get('name_ru', country)
                pct = statistics.get('percentages', {}).get(country, 0)
                lat = coords.get('lat', '')
                lon = coords.get('lon', '')
                f.write(f'"{country}","{name_ru}",{count},{pct},{lat},{lon}\n')

        print(f"[+] CSV сохранен: {output_file}")

    return output_file


def export_monthly_csv(statistics: Dict, output_file: Path) -> Path:
    """Экспорт помесячной динамики в CSV."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    monthly_data = statistics.get('by_month', {})

    if not monthly_data:
        print("[!] Нет данных по месяцам для экспорта")
        return output_file

    # Получаем все уникальные страны
    all_countries = set()
    for month_data in monthly_data.values():
        all_countries.update(month_data.keys())
    all_countries = sorted(all_countries)

    with open(output_file, 'w', encoding='utf-8-sig') as f:
        # Заголовок
        f.write("month," + ",".join(all_countries) + ",total\n")

        # Данные по месяцам
        for month in sorted(monthly_data.keys()):
            month_counts = monthly_data[month]
            row = [month]
            total = 0
            for country in all_countries:
                count = month_counts.get(country, 0)
                row.append(str(count))
                total += count
            row.append(str(total))
            f.write(",".join(row) + "\n")

    print(f"[+] Помесячный CSV сохранен: {output_file}")
    return output_file


# ═══════════════════════════════════════════════════════════════
# ИНТЕГРАЦИЯ С PROFILES.JSON
# ═══════════════════════════════════════════════════════════════

def enrich_profiles_with_country(
    profiles_file: Path,
    contacts: List[Dict],
    cache: PhoneCountryCache,
    output_file: Path = None
) -> Dict:
    """
    Обогащение профилей информацией о стране/регионе.

    Args:
        profiles_file: Путь к файлу profiles.json
        contacts: Список контактов с телефонами
        cache: Кэш определения стран
        output_file: Путь к выходному файлу (если не указан, перезаписывает исходный)

    Returns:
        Dict с обновленными профилями
    """
    profiles_data = {}

    if profiles_file.exists():
        with open(profiles_file, 'r', encoding='utf-8') as f:
            profiles_data = json.load(f)

    profiles = profiles_data.get('profiles', [])

    # Создаем маппинг contact_id -> phone
    contact_phones = {}
    for contact in contacts:
        contact_id = contact.get('contact_id') or contact.get('id')
        phone = contact.get('phone') or contact.get('jid', '').split('@')[0]
        if contact_id and phone:
            contact_phones[contact_id] = phone

    # Обогащаем профили
    enriched_count = 0

    for profile in profiles:
        contact_id = profile.get('contact_id')
        phone = contact_phones.get(contact_id)

        if phone:
            country_info = get_country_from_phone(phone, cache)

            if country_info:
                # Добавляем/обновляем информацию о географии
                if 'geography' not in profile:
                    profile['geography'] = {}

                profile['geography'].update({
                    'country': country_info.get('country'),
                    'country_code': country_info.get('country_code'),
                    'region': country_info.get('region'),
                    'timezones': country_info.get('timezones', []),
                    'phone_carrier': country_info.get('carrier'),
                    'enriched_at': datetime.now().isoformat()
                })

                # Также добавляем в biography для совместимости
                if 'biography' in profile and not profile['biography'].get('country'):
                    coords = COUNTRY_COORDINATES.get(country_info.get('country'), {})
                    profile['biography']['country'] = coords.get('name_ru', country_info.get('country'))

                enriched_count += 1

    # Сохраняем
    output_path = output_file or profiles_file
    profiles_data['profiles'] = profiles
    profiles_data['metadata'] = profiles_data.get('metadata', {})
    profiles_data['metadata']['geography_enriched_at'] = datetime.now().isoformat()
    profiles_data['metadata']['geography_enriched_count'] = enriched_count

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(profiles_data, f, ensure_ascii=False, indent=2)

    print(f"[+] Обогащено профилей: {enriched_count}")
    print(f"[+] Сохранено в: {output_path}")

    return profiles_data


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════

def generate_client_heatmap(
    contacts_file: Path = CONTACTS_FILE,
    output_dir: Path = OUTPUT_DIR,
    enrich_profiles: bool = True,
    create_png: bool = False
) -> Dict:
    """
    Генерация тепловой карты клиентов.

    Args:
        contacts_file: Путь к файлу контактов
        output_dir: Директория для выходных файлов
        enrich_profiles: Обогащать ли profiles.json
        create_png: Создавать ли PNG версию карты

    Returns:
        Dict со статистикой и путями к файлам
    """
    print("=" * 60)
    print("ТЕПЛОВАЯ КАРТА КЛИЕНТОВ")
    print("=" * 60)

    if not PHONENUMBERS_AVAILABLE:
        print("[!] ОШИБКА: Библиотека phonenumbers обязательна")
        print("    pip install phonenumbers")
        return {"error": "phonenumbers not installed"}

    # Загружаем кэш
    print(f"\n[1] Загрузка кэша...")
    cache = PhoneCountryCache(CACHE_FILE)

    # Загружаем контакты
    print(f"\n[2] Загрузка контактов из {contacts_file}")
    contacts = load_contacts(contacts_file)
    print(f"    Загружено контактов: {len(contacts)}")

    # Извлекаем телефоны
    print(f"\n[3] Извлечение номеров телефонов...")
    phones = extract_phones_from_contacts(contacts)
    print(f"    Найдено номеров: {len(phones)}")

    # Определяем страны
    print(f"\n[4] Определение стран по номерам телефонов...")
    phones_data = []
    countries_found = Counter()

    for phone, contact in phones:
        country_info = get_country_from_phone(phone, cache)
        phones_data.append((phone, contact, country_info))

        if country_info:
            countries_found[country_info.get('country', 'Unknown')] += 1
        else:
            countries_found['Unknown'] += 1

    # Сохраняем кэш
    cache.save()
    print(f"    Определено: {len([p for p in phones_data if p[2]])} из {len(phones)}")

    # Рассчитываем статистику
    print(f"\n[5] Расчет статистики...")
    statistics = calculate_country_statistics(phones_data, contacts)

    # Вывод топ-10
    print(f"\n    ТОП-10 СТРАН:")
    for i, (country, count) in enumerate(statistics.get('top_10', {}).items(), 1):
        coords = COUNTRY_COORDINATES.get(country, {})
        name_ru = coords.get('name_ru', country)
        pct = statistics.get('percentages', {}).get(country, 0)
        print(f"    {i:2}. {name_ru}: {count} ({pct:.1f}%)")

    # Создаем выходные файлы
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    result = {
        "statistics": statistics,
        "files": {}
    }

    # HTML интерактивная карта
    print(f"\n[6] Создание интерактивной карты...")
    html_file = output_dir / f"heatmap_{timestamp}.html"
    if create_interactive_map(statistics, html_file):
        result["files"]["html"] = str(html_file)

    # Также создаем постоянную версию
    html_latest = output_dir / "heatmap_latest.html"
    create_interactive_map(statistics, html_latest)

    # Choropleth карта
    print(f"\n[7] Создание choropleth карты...")
    choropleth_file = output_dir / f"choropleth_{timestamp}.html"
    if create_choropleth_map(statistics, choropleth_file):
        result["files"]["choropleth"] = str(choropleth_file)

    # PNG (опционально)
    if create_png and SELENIUM_AVAILABLE:
        print(f"\n[8] Создание PNG...")
        png_file = output_dir / f"heatmap_{timestamp}.png"
        if create_static_png(html_file, png_file):
            result["files"]["png"] = str(png_file)

    # JSON для дашборда
    print(f"\n[9] Экспорт JSON...")
    json_file = output_dir / f"statistics_{timestamp}.json"
    export_to_json(statistics, json_file)
    result["files"]["json"] = str(json_file)

    # CSV для аналитики
    print(f"\n[10] Экспорт CSV...")
    csv_file = output_dir / f"countries_{timestamp}.csv"
    export_to_csv(statistics, csv_file)
    result["files"]["csv"] = str(csv_file)

    # Помесячный CSV
    monthly_csv = output_dir / f"monthly_{timestamp}.csv"
    export_monthly_csv(statistics, monthly_csv)
    result["files"]["monthly_csv"] = str(monthly_csv)

    # Обогащение профилей
    if enrich_profiles and PROFILES_FILE.exists():
        print(f"\n[11] Обогащение profiles.json...")
        enrich_profiles_with_country(PROFILES_FILE, contacts, cache)

    # Итоговая статистика
    print("\n" + "=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    print(f"Всего контактов:     {statistics.get('total_contacts', 0)}")
    print(f"Определено стран:    {statistics.get('countries_count', 0)}")
    print(f"Неизвестных:         {statistics.get('by_country', {}).get('Unknown', 0)}")
    print(f"\nФайлы сохранены в: {output_dir}")
    print("=" * 60)

    return result


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Генерация тепловой карты клиентов по номерам телефонов"
    )
    parser.add_argument(
        "--contacts", "-c",
        default=str(CONTACTS_FILE),
        help=f"Путь к файлу контактов (default: {CONTACTS_FILE})"
    )
    parser.add_argument(
        "--output", "-o",
        default=str(OUTPUT_DIR),
        help=f"Директория для выходных файлов (default: {OUTPUT_DIR})"
    )
    parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="Не обогащать profiles.json"
    )
    parser.add_argument(
        "--png",
        action="store_true",
        help="Создать PNG версию карты (требует Selenium)"
    )
    parser.add_argument(
        "--phone", "-p",
        help="Определить страну для одного номера телефона"
    )

    args = parser.parse_args()

    # Режим проверки одного номера
    if args.phone:
        if not PHONENUMBERS_AVAILABLE:
            print("[!] phonenumbers не установлен")
            return

        result = parse_phone_number(args.phone)
        if result:
            print(f"Номер: {result.get('formatted')}")
            print(f"Страна: {result.get('country')}")
            print(f"Регион: {result.get('region')}")
            print(f"Оператор: {result.get('carrier')}")
            print(f"Часовые пояса: {', '.join(result.get('timezones', []))}")
        else:
            print(f"[!] Не удалось определить страну для номера: {args.phone}")
        return

    # Генерация карты
    generate_client_heatmap(
        contacts_file=Path(args.contacts),
        output_dir=Path(args.output),
        enrich_profiles=not args.no_enrich,
        create_png=args.png
    )


if __name__ == "__main__":
    main()
