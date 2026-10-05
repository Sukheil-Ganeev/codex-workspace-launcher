#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тепловая карта активности - визуализация сообщений по времени.

Функции:
- Матрица: час (0-23) x день недели (Пн-Вс)
- Подсчёт сообщений в каждой ячейке
- Визуализация: Seaborn heatmap, Plotly interactive, HTML standalone
- Фильтры: по контакту, периоду, входящие/исходящие
- GitHub-style calendar (год)
- Лучшее время для контакта
- Экспорт: PNG, HTML, JSON
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Any, Tuple
import calendar
import locale

sys.stdout.reconfigure(encoding='utf-8')

# Попытка установить русскую локаль
try:
    locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    except:
        pass

# Импорт библиотек визуализации
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("[!] NumPy не установлен. pip install numpy")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("[!] Pandas не установлен. pip install pandas")

try:
    import matplotlib
    matplotlib.use('Agg')  # Для работы без GUI
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[!] Matplotlib не установлен. pip install matplotlib")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    print("[!] Seaborn не установлен. pip install seaborn")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("[!] Plotly не установлен. pip install plotly")

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Пути по умолчанию
CHATS_DIR = Path("D:/Downloads/Chats")
OUTPUT_DIR = Path("D:/Downloads/Chats/_аналитика/activity_heatmaps")

# Дни недели
WEEKDAYS_RU = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
WEEKDAYS_EN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# Часы для отображения
HOURS = [f"{h:02d}:00" for h in range(24)]
HOURS_SHORT = [str(h) for h in range(24)]

# Цветовые схемы
COLOR_SCHEMES = {
    'default': 'YlOrRd',
    'green': 'Greens',
    'blue': 'Blues',
    'purple': 'Purples',
    'github': 'Greens',
    'hot': 'hot',
    'viridis': 'viridis'
}

# Месяцы для GitHub-style calendar
MONTHS_RU = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
             'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']


# ═══════════════════════════════════════════════════════════════
# ПАРСИНГ СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════════════

class MessageParser:
    """Парсер сообщений из различных форматов."""

    # Паттерны WhatsApp
    WHATSAPP_PATTERNS = [
        # Формат: DD.MM.YYYY, HH:MM - Sender: Message
        re.compile(r'^(\d{1,2}\.\d{1,2}\.\d{2,4}),?\s*(\d{1,2}:\d{2})\s*[-–]\s*([^:]+):\s*(.*)$'),
        # Формат: [DD.MM.YYYY, HH:MM:SS] Sender: Message
        re.compile(r'^\[(\d{1,2}\.\d{1,2}\.\d{2,4}),?\s*(\d{1,2}:\d{2}(?::\d{2})?)\]\s*([^:]+):\s*(.*)$'),
        # Формат: DD/MM/YYYY, HH:MM - Sender: Message
        re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2})\s*[-–]\s*([^:]+):\s*(.*)$'),
        # Формат: YYYY-MM-DD HH:MM:SS - Sender: Message
        re.compile(r'^(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–]\s*([^:]+):\s*(.*)$'),
    ]

    # Системные сообщения
    SYSTEM_PATTERNS = [
        re.compile(r'создал.* группу', re.I),
        re.compile(r'добавил.* участник', re.I),
        re.compile(r'изменил.* тему', re.I),
        re.compile(r'присоединился', re.I),
        re.compile(r'вышел из группы', re.I),
        re.compile(r'удалил.* участник', re.I),
        re.compile(r'messages and calls are end-to-end encrypted', re.I),
        re.compile(r'сообщения защищены', re.I),
    ]

    @classmethod
    def parse_file(cls, filepath: Path, contact_filter: str = None,
                   direction_filter: str = None, my_names: List[str] = None) -> List[Dict]:
        """
        Парсинг файла чата.

        Args:
            filepath: Путь к файлу чата
            contact_filter: Фильтр по имени контакта
            direction_filter: 'incoming', 'outgoing', или None (все)
            my_names: Список имён пользователя (для определения исходящих)

        Returns:
            List сообщений с датой, временем, отправителем
        """
        messages = []
        my_names = my_names or ['Вы', 'You', 'Me', 'Я']

        if not filepath.exists():
            return messages

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='cp1251') as f:
                    content = f.read()
            except:
                return messages

        lines = content.split('\n')
        current_message = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Пробуем распарсить как новое сообщение
            parsed = cls._parse_line(line)

            if parsed:
                # Сохраняем предыдущее сообщение
                if current_message:
                    # Применяем фильтры
                    if cls._apply_filters(current_message, contact_filter,
                                          direction_filter, my_names):
                        messages.append(current_message)

                current_message = parsed
            elif current_message:
                # Продолжение предыдущего сообщения
                current_message['text'] += '\n' + line

        # Добавляем последнее сообщение
        if current_message and cls._apply_filters(current_message, contact_filter,
                                                   direction_filter, my_names):
            messages.append(current_message)

        return messages

    @classmethod
    def _parse_line(cls, line: str) -> Optional[Dict]:
        """Парсинг одной строки."""
        for pattern in cls.WHATSAPP_PATTERNS:
            match = pattern.match(line)
            if match:
                date_str, time_str, sender, text = match.groups()

                # Пропускаем системные сообщения
                for sys_pattern in cls.SYSTEM_PATTERNS:
                    if sys_pattern.search(text) or sys_pattern.search(sender):
                        return None

                # Парсим дату
                dt = cls._parse_datetime(date_str, time_str)
                if dt:
                    return {
                        'datetime': dt,
                        'date': dt.date(),
                        'time': dt.time(),
                        'hour': dt.hour,
                        'weekday': dt.weekday(),  # 0=Пн, 6=Вс
                        'sender': sender.strip(),
                        'text': text.strip(),
                        'year': dt.year,
                        'month': dt.month,
                        'day': dt.day
                    }
        return None

    @classmethod
    def _parse_datetime(cls, date_str: str, time_str: str) -> Optional[datetime]:
        """Парсинг даты и времени."""
        # Форматы даты
        date_formats = [
            '%d.%m.%Y', '%d.%m.%y',
            '%d/%m/%Y', '%d/%m/%y',
            '%Y-%m-%d'
        ]

        # Форматы времени
        time_formats = ['%H:%M', '%H:%M:%S']

        for date_fmt in date_formats:
            for time_fmt in time_formats:
                try:
                    dt_str = f"{date_str} {time_str}"
                    fmt = f"{date_fmt} {time_fmt}"
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue
        return None

    @classmethod
    def _apply_filters(cls, message: Dict, contact_filter: str,
                       direction_filter: str, my_names: List[str]) -> bool:
        """Применение фильтров к сообщению."""
        # Фильтр по контакту
        if contact_filter:
            if contact_filter.lower() not in message['sender'].lower():
                return False

        # Фильтр по направлению
        if direction_filter:
            is_outgoing = any(name.lower() in message['sender'].lower()
                            for name in my_names)

            if direction_filter == 'outgoing' and not is_outgoing:
                return False
            if direction_filter == 'incoming' and is_outgoing:
                return False

        return True


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ АКТИВНОСТИ
# ═══════════════════════════════════════════════════════════════

class ActivityAnalyzer:
    """Анализатор активности сообщений."""

    def __init__(self, messages: List[Dict]):
        self.messages = messages
        self.matrix = None
        self.daily_counts = None
        self.stats = {}

    def build_hour_weekday_matrix(self) -> 'np.ndarray':
        """
        Построение матрицы час x день недели.

        Returns:
            numpy array 24x7 (часы x дни)
        """
        if not NUMPY_AVAILABLE:
            # Fallback без numpy
            matrix = [[0] * 7 for _ in range(24)]
            for msg in self.messages:
                hour = msg['hour']
                weekday = msg['weekday']
                matrix[hour][weekday] += 1
            self.matrix = matrix
            return matrix

        matrix = np.zeros((24, 7), dtype=int)

        for msg in self.messages:
            hour = msg['hour']
            weekday = msg['weekday']
            matrix[hour, weekday] += 1

        self.matrix = matrix
        return matrix

    def build_daily_counts(self) -> Dict[str, int]:
        """
        Построение подсчёта по дням для GitHub-style calendar.

        Returns:
            Dict[date_str, count]
        """
        daily = Counter()

        for msg in self.messages:
            date_str = msg['date'].isoformat()
            daily[date_str] += 1

        self.daily_counts = dict(daily)
        return self.daily_counts

    def calculate_statistics(self) -> Dict:
        """Расчёт статистики активности."""
        if not self.messages:
            return {}

        if self.matrix is None:
            self.build_hour_weekday_matrix()

        if self.daily_counts is None:
            self.build_daily_counts()

        # Определяем пиковые значения
        if NUMPY_AVAILABLE and isinstance(self.matrix, np.ndarray):
            peak_hour, peak_weekday = np.unravel_index(
                np.argmax(self.matrix), self.matrix.shape
            )
            total = np.sum(self.matrix)
            hourly_totals = np.sum(self.matrix, axis=1)
            weekday_totals = np.sum(self.matrix, axis=0)
        else:
            # Fallback
            max_val = 0
            peak_hour, peak_weekday = 0, 0
            total = 0
            hourly_totals = [0] * 24
            weekday_totals = [0] * 7

            for h in range(24):
                for w in range(7):
                    val = self.matrix[h][w]
                    total += val
                    hourly_totals[h] += val
                    weekday_totals[w] += val
                    if val > max_val:
                        max_val = val
                        peak_hour, peak_weekday = h, w

        # Лучшие часы
        if NUMPY_AVAILABLE:
            top_hours_idx = np.argsort(hourly_totals)[::-1][:3]
            top_hours = [(int(h), int(hourly_totals[h])) for h in top_hours_idx]
        else:
            indexed = [(i, v) for i, v in enumerate(hourly_totals)]
            indexed.sort(key=lambda x: x[1], reverse=True)
            top_hours = [(i, v) for i, v in indexed[:3]]

        # Лучшие дни недели
        if NUMPY_AVAILABLE:
            top_weekdays_idx = np.argsort(weekday_totals)[::-1][:3]
            top_weekdays = [(WEEKDAYS_RU[int(w)], int(weekday_totals[w]))
                           for w in top_weekdays_idx]
        else:
            indexed = [(i, v) for i, v in enumerate(weekday_totals)]
            indexed.sort(key=lambda x: x[1], reverse=True)
            top_weekdays = [(WEEKDAYS_RU[i], v) for i, v in indexed[:3]]

        # Определяем лучшее время для контакта
        best_contact_time = self._find_best_contact_time()

        # Статистика по дням
        if self.daily_counts:
            dates = sorted(self.daily_counts.keys())
            avg_daily = total / len(self.daily_counts) if self.daily_counts else 0
            max_daily = max(self.daily_counts.values()) if self.daily_counts else 0
            max_daily_date = max(self.daily_counts, key=self.daily_counts.get) if self.daily_counts else None
        else:
            dates = []
            avg_daily = 0
            max_daily = 0
            max_daily_date = None

        self.stats = {
            'total_messages': int(total),
            'peak_hour': int(peak_hour),
            'peak_weekday': WEEKDAYS_RU[int(peak_weekday)],
            'peak_weekday_index': int(peak_weekday),
            'peak_count': int(self.matrix[peak_hour][peak_weekday] if not NUMPY_AVAILABLE
                             else self.matrix[peak_hour, peak_weekday]),
            'top_hours': top_hours,
            'top_weekdays': top_weekdays,
            'best_contact_time': best_contact_time,
            'avg_daily': round(avg_daily, 1),
            'max_daily': int(max_daily),
            'max_daily_date': max_daily_date,
            'date_range': {
                'start': dates[0] if dates else None,
                'end': dates[-1] if dates else None
            },
            'total_days': len(self.daily_counts) if self.daily_counts else 0,
            'hourly_distribution': [int(h) for h in hourly_totals] if not NUMPY_AVAILABLE
                                   else hourly_totals.tolist(),
            'weekday_distribution': [int(w) for w in weekday_totals] if not NUMPY_AVAILABLE
                                    else weekday_totals.tolist()
        }

        return self.stats

    def _find_best_contact_time(self) -> Dict:
        """Определение лучшего времени для контакта."""
        if self.matrix is None:
            return {}

        # Ищем топ-3 комбинации час+день с максимальной активностью
        combinations = []

        for h in range(24):
            for w in range(7):
                if NUMPY_AVAILABLE and isinstance(self.matrix, np.ndarray):
                    count = int(self.matrix[h, w])
                else:
                    count = self.matrix[h][w]
                combinations.append({
                    'hour': h,
                    'weekday': w,
                    'weekday_name': WEEKDAYS_RU[w],
                    'count': count,
                    'time_range': f"{h:02d}:00-{h:02d}:59"
                })

        # Сортируем по убыванию
        combinations.sort(key=lambda x: x['count'], reverse=True)

        # Топ-5 лучших временных слотов
        top_slots = combinations[:5]

        # Рабочие часы (9-18) vs нерабочие
        work_hours_count = 0
        off_hours_count = 0

        for h in range(24):
            if NUMPY_AVAILABLE and isinstance(self.matrix, np.ndarray):
                row_sum = int(np.sum(self.matrix[h, :]))
            else:
                row_sum = sum(self.matrix[h])

            if 9 <= h < 18:
                work_hours_count += row_sum
            else:
                off_hours_count += row_sum

        # Будни vs выходные
        weekday_count = 0
        weekend_count = 0

        for w in range(7):
            if NUMPY_AVAILABLE and isinstance(self.matrix, np.ndarray):
                col_sum = int(np.sum(self.matrix[:, w]))
            else:
                col_sum = sum(self.matrix[h][w] for h in range(24))

            if w < 5:
                weekday_count += col_sum
            else:
                weekend_count += col_sum

        return {
            'top_slots': top_slots,
            'work_hours_count': work_hours_count,
            'off_hours_count': off_hours_count,
            'work_hours_percentage': round(work_hours_count / (work_hours_count + off_hours_count) * 100, 1)
                if (work_hours_count + off_hours_count) > 0 else 0,
            'weekday_count': weekday_count,
            'weekend_count': weekend_count,
            'weekday_percentage': round(weekday_count / (weekday_count + weekend_count) * 100, 1)
                if (weekday_count + weekend_count) > 0 else 0,
            'recommendation': self._generate_recommendation(top_slots)
        }

    def _generate_recommendation(self, top_slots: List[Dict]) -> str:
        """Генерация рекомендации по времени контакта."""
        if not top_slots:
            return "Недостаточно данных"

        best = top_slots[0]
        return f"Лучшее время: {best['weekday_name']} {best['time_range']} ({best['count']} сообщений)"


# ═══════════════════════════════════════════════════════════════
# ВИЗУАЛИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

class HeatmapVisualizer:
    """Визуализатор тепловых карт."""

    def __init__(self, analyzer: ActivityAnalyzer):
        self.analyzer = analyzer
        self.matrix = analyzer.matrix
        self.daily_counts = analyzer.daily_counts
        self.stats = analyzer.stats

    def create_seaborn_heatmap(self, output_file: Path,
                                title: str = "Активность сообщений",
                                colormap: str = 'YlOrRd',
                                figsize: Tuple[int, int] = (14, 8)) -> Optional[Path]:
        """
        Создание статичной тепловой карты с Seaborn.

        Args:
            output_file: Путь к PNG файлу
            title: Заголовок
            colormap: Цветовая схема
            figsize: Размер фигуры

        Returns:
            Path к созданному файлу или None
        """
        if not SEABORN_AVAILABLE or not MATPLOTLIB_AVAILABLE:
            print("[!] Seaborn/Matplotlib не установлен")
            return None

        if self.matrix is None:
            print("[!] Матрица не построена")
            return None

        # Создаем DataFrame
        if PANDAS_AVAILABLE:
            df = pd.DataFrame(
                self.matrix if NUMPY_AVAILABLE else [row[:] for row in self.matrix],
                index=HOURS_SHORT,
                columns=WEEKDAYS_RU
            )
        else:
            print("[!] Pandas требуется для Seaborn heatmap")
            return None

        # Создаем фигуру
        fig, ax = plt.subplots(figsize=figsize)

        # Heatmap
        sns.heatmap(
            df,
            annot=True,
            fmt='d',
            cmap=colormap,
            linewidths=0.5,
            linecolor='white',
            cbar_kws={'label': 'Количество сообщений'},
            ax=ax
        )

        # Заголовок и подписи
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('День недели', fontsize=12)
        ax.set_ylabel('Час', fontsize=12)

        # Добавляем статистику
        stats_text = f"Всего: {self.stats.get('total_messages', 0)} | "
        stats_text += f"Пик: {WEEKDAYS_RU[self.stats.get('peak_weekday_index', 0)]} "
        stats_text += f"{self.stats.get('peak_hour', 0)}:00"

        fig.text(0.5, 0.02, stats_text, ha='center', fontsize=10, style='italic')

        # Сохраняем
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(str(output_file), dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()

        print(f"[+] Seaborn heatmap сохранен: {output_file}")
        return output_file

    def create_plotly_heatmap(self, output_file: Path,
                               title: str = "Активность сообщений",
                               colorscale: str = 'YlOrRd') -> Optional[Path]:
        """
        Создание интерактивной тепловой карты с Plotly.

        Args:
            output_file: Путь к HTML файлу
            title: Заголовок
            colorscale: Цветовая схема

        Returns:
            Path к созданному файлу или None
        """
        if not PLOTLY_AVAILABLE:
            print("[!] Plotly не установлен")
            return None

        if self.matrix is None:
            print("[!] Матрица не построена")
            return None

        # Подготовка данных
        if NUMPY_AVAILABLE and isinstance(self.matrix, np.ndarray):
            z_data = self.matrix.tolist()
        else:
            z_data = [row[:] for row in self.matrix]

        # Создаем heatmap
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=WEEKDAYS_RU,
            y=HOURS_SHORT,
            colorscale=colorscale,
            hoverongaps=False,
            hovertemplate='День: %{x}<br>Час: %{y}:00<br>Сообщений: %{z}<extra></extra>',
            colorbar=dict(
                title='Сообщений',
                titleside='right'
            )
        ))

        # Добавляем аннотации с числами
        annotations = []
        for i, hour in enumerate(HOURS_SHORT):
            for j, day in enumerate(WEEKDAYS_RU):
                val = z_data[i][j]
                if val > 0:
                    # Цвет текста в зависимости от значения
                    max_val = max(max(row) for row in z_data)
                    text_color = 'white' if val > max_val * 0.5 else 'black'

                    annotations.append(dict(
                        x=day,
                        y=hour,
                        text=str(val),
                        showarrow=False,
                        font=dict(color=text_color, size=10)
                    ))

        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=20)
            ),
            xaxis=dict(
                title='День недели',
                side='bottom'
            ),
            yaxis=dict(
                title='Час',
                autorange='reversed'  # 0 сверху, 23 снизу
            ),
            annotations=annotations,
            width=900,
            height=700
        )

        # Сохраняем
        output_file.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_file), include_plotlyjs=True, full_html=True)

        print(f"[+] Plotly heatmap сохранен: {output_file}")
        return output_file

    def create_github_calendar(self, output_file: Path,
                                year: int = None,
                                title: str = "Активность за год") -> Optional[Path]:
        """
        Создание GitHub-style contribution calendar.

        Args:
            output_file: Путь к HTML файлу
            year: Год для отображения (None = последний год данных)
            title: Заголовок

        Returns:
            Path к созданному файлу или None
        """
        if not PLOTLY_AVAILABLE:
            print("[!] Plotly не установлен")
            return None

        if not self.daily_counts:
            print("[!] Дневные подсчёты не построены")
            return None

        # Определяем год
        if year is None:
            dates = [datetime.fromisoformat(d) for d in self.daily_counts.keys()]
            if dates:
                year = max(d.year for d in dates)
            else:
                year = datetime.now().year

        # Строим календарь для года
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)

        # Создаем матрицу 53 недели x 7 дней
        weeks = []
        current_date = start_date

        # Начинаем с понедельника недели, содержащей 1 января
        while current_date.weekday() != 0:
            current_date -= timedelta(days=1)

        week_data = []
        week_num = 0

        while current_date <= end_date or len(week_data) > 0:
            date_str = current_date.strftime('%Y-%m-%d')
            count = self.daily_counts.get(date_str, 0)

            week_data.append({
                'date': current_date,
                'count': count,
                'weekday': current_date.weekday()
            })

            if len(week_data) == 7:
                weeks.append(week_data)
                week_data = []
                week_num += 1

            current_date += timedelta(days=1)

            if current_date.year > year and len(week_data) == 0:
                break

        # Добавляем остаток
        if week_data:
            weeks.append(week_data)

        # Создаем матрицу для Plotly
        z_data = [[None] * len(weeks) for _ in range(7)]
        hover_text = [['' for _ in range(len(weeks))] for _ in range(7)]

        for week_idx, week in enumerate(weeks):
            for day_data in week:
                weekday = day_data['weekday']
                count = day_data['count']
                date = day_data['date']

                if date.year == year:
                    z_data[weekday][week_idx] = count
                    hover_text[weekday][week_idx] = f"{date.strftime('%d.%m.%Y')}: {count} сообщений"

        # Находим максимальное значение
        max_count = max(max(row) for row in z_data if any(v is not None for v in row)) if any(
            any(v is not None for v in row) for row in z_data
        ) else 1

        # Создаем heatmap
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            y=WEEKDAYS_RU,
            colorscale=[
                [0, '#ebedf0'],       # 0
                [0.25, '#9be9a8'],    # low
                [0.5, '#40c463'],     # medium
                [0.75, '#30a14e'],    # high
                [1, '#216e39']        # max
            ],
            zmin=0,
            zmax=max_count,
            hoverinfo='text',
            text=hover_text,
            showscale=True,
            colorbar=dict(
                title='Сообщений',
                titleside='right',
                tickvals=[0, max_count // 4, max_count // 2, max_count * 3 // 4, max_count],
            ),
            xgap=2,
            ygap=2
        ))

        # Добавляем метки месяцев
        month_positions = []
        current_month = None

        for week_idx, week in enumerate(weeks):
            for day_data in week:
                if day_data['date'].year == year:
                    month = day_data['date'].month
                    if month != current_month:
                        month_positions.append({
                            'week': week_idx,
                            'month': month
                        })
                        current_month = month
                    break

        # Аннотации месяцев
        month_annotations = []
        for mp in month_positions:
            month_annotations.append(dict(
                x=mp['week'],
                y=-1,
                text=MONTHS_RU[mp['month'] - 1],
                showarrow=False,
                font=dict(size=10),
                xanchor='left'
            ))

        fig.update_layout(
            title=dict(
                text=f"{title} ({year})",
                x=0.5,
                font=dict(size=18)
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                autorange='reversed'
            ),
            annotations=month_annotations,
            width=1200,
            height=250,
            margin=dict(t=50, l=50, r=50, b=50)
        )

        # Сохраняем
        output_file.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_file), include_plotlyjs=True, full_html=True)

        print(f"[+] GitHub calendar сохранен: {output_file}")
        return output_file

    def create_combined_dashboard(self, output_file: Path,
                                   title: str = "Дашборд активности") -> Optional[Path]:
        """
        Создание комбинированного дашборда с несколькими графиками.
        """
        if not PLOTLY_AVAILABLE:
            print("[!] Plotly не установлен")
            return None

        # Создаем subplot
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Тепловая карта: Час x День',
                'Распределение по часам',
                'Распределение по дням недели',
                'Топ-5 временных слотов',
                'Активность за последние 30 дней',
                'Статистика'
            ),
            specs=[
                [{"type": "heatmap"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "bar", "colspan": 2}, None]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )

        # 1. Heatmap
        if NUMPY_AVAILABLE and isinstance(self.matrix, np.ndarray):
            z_data = self.matrix.tolist()
        else:
            z_data = [row[:] for row in self.matrix]

        fig.add_trace(go.Heatmap(
            z=z_data,
            x=WEEKDAYS_RU,
            y=HOURS_SHORT,
            colorscale='YlOrRd',
            showscale=True,
            colorbar=dict(x=0.45, len=0.3, y=0.85)
        ), row=1, col=1)

        # 2. Распределение по часам
        hourly = self.stats.get('hourly_distribution', [0] * 24)
        fig.add_trace(go.Bar(
            x=HOURS_SHORT,
            y=hourly,
            marker_color='steelblue',
            name='По часам'
        ), row=1, col=2)

        # 3. Распределение по дням недели
        weekday_dist = self.stats.get('weekday_distribution', [0] * 7)
        fig.add_trace(go.Bar(
            x=WEEKDAYS_RU,
            y=weekday_dist,
            marker_color='coral',
            name='По дням'
        ), row=2, col=1)

        # 4. Топ-5 временных слотов
        best_time = self.stats.get('best_contact_time', {})
        top_slots = best_time.get('top_slots', [])[:5]

        if top_slots:
            labels = [f"{s['weekday_name']} {s['hour']:02d}:00" for s in top_slots]
            values = [s['count'] for s in top_slots]

            fig.add_trace(go.Bar(
                x=labels,
                y=values,
                marker_color='mediumseagreen',
                name='Топ слоты'
            ), row=2, col=2)

        # 5. Последние 30 дней
        if self.daily_counts:
            sorted_dates = sorted(self.daily_counts.keys())[-30:]
            daily_values = [self.daily_counts.get(d, 0) for d in sorted_dates]
            short_dates = [d[5:] for d in sorted_dates]  # MM-DD

            fig.add_trace(go.Bar(
                x=short_dates,
                y=daily_values,
                marker_color='mediumpurple',
                name='По дням'
            ), row=3, col=1)

        # Настройки layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=24)
            ),
            showlegend=False,
            height=1000,
            width=1200
        )

        # Сохраняем
        output_file.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_file), include_plotlyjs=True, full_html=True)

        print(f"[+] Dashboard сохранен: {output_file}")
        return output_file

    def create_standalone_html(self, output_file: Path,
                                title: str = "Анализ активности") -> Optional[Path]:
        """
        Создание standalone HTML страницы со всеми визуализациями.
        """
        if not PLOTLY_AVAILABLE:
            print("[!] Plotly не установлен")
            return None

        # Генерируем HTML компоненты
        html_content = self._generate_standalone_html(title)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"[+] Standalone HTML сохранен: {output_file}")
        return output_file

    def _generate_standalone_html(self, title: str) -> str:
        """Генерация HTML контента."""
        # Подготовка данных для heatmap
        if NUMPY_AVAILABLE and isinstance(self.matrix, np.ndarray):
            z_data = self.matrix.tolist()
        else:
            z_data = [row[:] for row in self.matrix]

        # Статистика
        stats = self.stats
        best_time = stats.get('best_contact_time', {})

        html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
            font-size: 0.9em;
        }}
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .chart-title {{
            font-size: 1.3em;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .recommendation {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .recommendation h3 {{
            font-size: 1.5em;
            margin-bottom: 10px;
        }}
        .recommendation p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .top-slots {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .slot-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .slot-time {{
            font-weight: bold;
            color: #333;
        }}
        .slot-count {{
            color: #667eea;
            font-size: 1.2em;
        }}
        footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>

        <!-- Статистика -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_messages', 0):,}</div>
                <div class="stat-label">Всего сообщений</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_days', 0)}</div>
                <div class="stat-label">Дней активности</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('avg_daily', 0)}</div>
                <div class="stat-label">Среднее в день</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('peak_hour', 0)}:00</div>
                <div class="stat-label">Пиковый час</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('peak_weekday', 'Пн')}</div>
                <div class="stat-label">Самый активный день</div>
            </div>
        </div>

        <!-- Рекомендация -->
        <div class="recommendation">
            <h3>Лучшее время для контакта</h3>
            <p>{best_time.get('recommendation', 'Анализируем данные...')}</p>
            <div class="top-slots">
'''

        # Добавляем топ слоты
        for slot in best_time.get('top_slots', [])[:5]:
            html += f'''
                <div class="slot-card">
                    <div class="slot-time">{slot['weekday_name']} {slot['hour']:02d}:00</div>
                    <div class="slot-count">{slot['count']} сообщений</div>
                </div>
'''

        html += '''
            </div>
        </div>

        <!-- Тепловая карта -->
        <div class="chart-container">
            <div class="chart-title">Активность по часам и дням недели</div>
            <div id="heatmap"></div>
        </div>

        <!-- Распределение по часам -->
        <div class="chart-container">
            <div class="chart-title">Распределение по часам</div>
            <div id="hourly"></div>
        </div>

        <!-- Распределение по дням -->
        <div class="chart-container">
            <div class="chart-title">Распределение по дням недели</div>
            <div id="weekday"></div>
        </div>

        <footer>
            <p>Создано: ''' + datetime.now().strftime('%d.%m.%Y %H:%M') + '''</p>
        </footer>
    </div>

    <script>
        // Данные
        const zData = ''' + json.dumps(z_data) + ''';
        const weekdays = ''' + json.dumps(WEEKDAYS_RU) + ''';
        const hours = ''' + json.dumps(HOURS_SHORT) + ''';
        const hourlyDist = ''' + json.dumps(stats.get('hourly_distribution', [0]*24)) + ''';
        const weekdayDist = ''' + json.dumps(stats.get('weekday_distribution', [0]*7)) + ''';

        // Heatmap
        Plotly.newPlot('heatmap', [{
            z: zData,
            x: weekdays,
            y: hours,
            type: 'heatmap',
            colorscale: 'YlOrRd',
            hovertemplate: 'День: %{x}<br>Час: %{y}:00<br>Сообщений: %{z}<extra></extra>'
        }], {
            margin: {t: 30, l: 50, r: 30, b: 50},
            yaxis: {autorange: 'reversed'}
        }, {responsive: true});

        // Hourly
        Plotly.newPlot('hourly', [{
            x: hours,
            y: hourlyDist,
            type: 'bar',
            marker: {color: '#667eea'}
        }], {
            margin: {t: 30, l: 50, r: 30, b: 50},
            xaxis: {title: 'Час'},
            yaxis: {title: 'Сообщений'}
        }, {responsive: true});

        // Weekday
        Plotly.newPlot('weekday', [{
            x: weekdays,
            y: weekdayDist,
            type: 'bar',
            marker: {color: '#764ba2'}
        }], {
            margin: {t: 30, l: 50, r: 30, b: 50},
            xaxis: {title: 'День недели'},
            yaxis: {title: 'Сообщений'}
        }, {responsive: true});
    </script>
</body>
</html>'''

        return html


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

def export_to_json(analyzer: ActivityAnalyzer, output_file: Path) -> Path:
    """Экспорт статистики в JSON."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Подготовка матрицы
    if NUMPY_AVAILABLE and isinstance(analyzer.matrix, np.ndarray):
        matrix_data = analyzer.matrix.tolist()
    else:
        matrix_data = [row[:] for row in analyzer.matrix] if analyzer.matrix else []

    export_data = {
        'generated_at': datetime.now().isoformat(),
        'statistics': analyzer.stats,
        'matrix': {
            'hours': HOURS_SHORT,
            'weekdays': WEEKDAYS_RU,
            'data': matrix_data
        },
        'daily_counts': analyzer.daily_counts or {},
        'visualization': {
            'recommended_colors': ['#ffffcc', '#ffeda0', '#fed976', '#feb24c',
                                   '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026'],
            'github_colors': ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"[+] JSON сохранен: {output_file}")
    return output_file


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════

def generate_activity_heatmap(
    chat_files: List[Path] = None,
    chats_dir: Path = CHATS_DIR,
    output_dir: Path = OUTPUT_DIR,
    contact_filter: str = None,
    direction_filter: str = None,
    date_from: str = None,
    date_to: str = None,
    my_names: List[str] = None,
    year: int = None,
    colormap: str = 'YlOrRd'
) -> Dict:
    """
    Генерация тепловой карты активности.

    Args:
        chat_files: Список файлов чатов (если None, ищет в chats_dir)
        chats_dir: Директория с чатами
        output_dir: Директория для выходных файлов
        contact_filter: Фильтр по имени контакта
        direction_filter: 'incoming', 'outgoing', или None
        date_from: Начальная дата (YYYY-MM-DD)
        date_to: Конечная дата (YYYY-MM-DD)
        my_names: Список имён пользователя
        year: Год для GitHub calendar
        colormap: Цветовая схема

    Returns:
        Dict со статистикой и путями к файлам
    """
    print("=" * 60)
    print("ТЕПЛОВАЯ КАРТА АКТИВНОСТИ")
    print("=" * 60)

    # Находим файлы чатов
    if chat_files is None:
        chat_files = []
        if chats_dir.exists():
            chat_files = list(chats_dir.glob("**/*.txt"))
            # Исключаем служебные файлы
            chat_files = [f for f in chat_files if not f.name.startswith('_')]

    print(f"\n[1] Найдено файлов чатов: {len(chat_files)}")

    if not chat_files:
        print("[!] Файлы чатов не найдены")
        return {"error": "No chat files found"}

    # Парсим сообщения
    print(f"\n[2] Парсинг сообщений...")
    all_messages = []

    for filepath in chat_files:
        messages = MessageParser.parse_file(
            filepath,
            contact_filter=contact_filter,
            direction_filter=direction_filter,
            my_names=my_names
        )
        all_messages.extend(messages)

    print(f"    Всего сообщений: {len(all_messages)}")

    if not all_messages:
        print("[!] Сообщения не найдены")
        return {"error": "No messages found"}

    # Фильтрация по дате
    if date_from or date_to:
        print(f"\n[3] Фильтрация по дате...")
        filtered = []

        date_from_dt = datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None
        date_to_dt = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None

        for msg in all_messages:
            msg_date = msg['date']
            if date_from_dt and msg_date < date_from_dt:
                continue
            if date_to_dt and msg_date > date_to_dt:
                continue
            filtered.append(msg)

        all_messages = filtered
        print(f"    После фильтрации: {len(all_messages)}")

    # Анализ
    print(f"\n[4] Анализ активности...")
    analyzer = ActivityAnalyzer(all_messages)
    analyzer.build_hour_weekday_matrix()
    analyzer.build_daily_counts()
    stats = analyzer.calculate_statistics()

    # Вывод статистики
    print(f"\n    СТАТИСТИКА:")
    print(f"    Всего сообщений: {stats.get('total_messages', 0)}")
    print(f"    Дней активности: {stats.get('total_days', 0)}")
    print(f"    Среднее в день: {stats.get('avg_daily', 0)}")
    print(f"    Пиковый час: {stats.get('peak_hour', 0)}:00")
    print(f"    Самый активный день: {stats.get('peak_weekday', '')}")

    best_time = stats.get('best_contact_time', {})
    print(f"\n    ЛУЧШЕЕ ВРЕМЯ ДЛЯ КОНТАКТА:")
    print(f"    {best_time.get('recommendation', 'N/A')}")
    print(f"    Рабочие часы: {best_time.get('work_hours_percentage', 0)}%")
    print(f"    Будни: {best_time.get('weekday_percentage', 0)}%")

    # Создаем выходные файлы
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    result = {
        "statistics": stats,
        "files": {}
    }

    # Визуализация
    visualizer = HeatmapVisualizer(analyzer)

    # 1. Seaborn heatmap (PNG)
    print(f"\n[5] Создание визуализаций...")
    if SEABORN_AVAILABLE:
        png_file = output_dir / f"heatmap_{timestamp}.png"
        if visualizer.create_seaborn_heatmap(png_file, colormap=colormap):
            result["files"]["png"] = str(png_file)

    # 2. Plotly heatmap (HTML)
    if PLOTLY_AVAILABLE:
        plotly_file = output_dir / f"heatmap_interactive_{timestamp}.html"
        if visualizer.create_plotly_heatmap(plotly_file, colorscale=colormap):
            result["files"]["plotly_html"] = str(plotly_file)

    # 3. GitHub calendar
    if PLOTLY_AVAILABLE:
        github_file = output_dir / f"github_calendar_{timestamp}.html"
        if visualizer.create_github_calendar(github_file, year=year):
            result["files"]["github_html"] = str(github_file)

    # 4. Dashboard
    if PLOTLY_AVAILABLE:
        dashboard_file = output_dir / f"dashboard_{timestamp}.html"
        if visualizer.create_combined_dashboard(dashboard_file):
            result["files"]["dashboard_html"] = str(dashboard_file)

    # 5. Standalone HTML
    if PLOTLY_AVAILABLE:
        standalone_file = output_dir / f"activity_report_{timestamp}.html"
        if visualizer.create_standalone_html(standalone_file):
            result["files"]["standalone_html"] = str(standalone_file)

        # Также создаем latest версию
        latest_file = output_dir / "activity_report_latest.html"
        visualizer.create_standalone_html(latest_file)

    # 6. JSON экспорт
    print(f"\n[6] Экспорт JSON...")
    json_file = output_dir / f"activity_stats_{timestamp}.json"
    export_to_json(analyzer, json_file)
    result["files"]["json"] = str(json_file)

    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    print(f"Всего сообщений: {stats.get('total_messages', 0)}")
    print(f"Период: {stats.get('date_range', {}).get('start', 'N/A')} - "
          f"{stats.get('date_range', {}).get('end', 'N/A')}")
    print(f"\nФайлы сохранены в: {output_dir}")
    print("=" * 60)

    return result


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Генерация тепловой карты активности сообщений"
    )
    parser.add_argument(
        "--chats", "-c",
        default=str(CHATS_DIR),
        help=f"Директория с чатами (default: {CHATS_DIR})"
    )
    parser.add_argument(
        "--output", "-o",
        default=str(OUTPUT_DIR),
        help=f"Директория для выходных файлов (default: {OUTPUT_DIR})"
    )
    parser.add_argument(
        "--contact",
        help="Фильтр по имени контакта"
    )
    parser.add_argument(
        "--direction",
        choices=['incoming', 'outgoing'],
        help="Фильтр по направлению (incoming/outgoing)"
    )
    parser.add_argument(
        "--from",
        dest="date_from",
        help="Начальная дата (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--to",
        dest="date_to",
        help="Конечная дата (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--year", "-y",
        type=int,
        help="Год для GitHub calendar"
    )
    parser.add_argument(
        "--color",
        default="YlOrRd",
        choices=list(COLOR_SCHEMES.keys()),
        help="Цветовая схема (default: YlOrRd)"
    )
    parser.add_argument(
        "--my-names",
        nargs='+',
        default=['Вы', 'You', 'Me', 'Я'],
        help="Имена пользователя для определения исходящих"
    )
    parser.add_argument(
        "--file", "-f",
        help="Анализировать конкретный файл чата"
    )

    args = parser.parse_args()

    # Определяем файлы чатов
    chat_files = None
    if args.file:
        chat_files = [Path(args.file)]

    # Генерация
    generate_activity_heatmap(
        chat_files=chat_files,
        chats_dir=Path(args.chats),
        output_dir=Path(args.output),
        contact_filter=args.contact,
        direction_filter=args.direction,
        date_from=args.date_from,
        date_to=args.date_to,
        my_names=args.my_names,
        year=args.year,
        colormap=COLOR_SCHEMES.get(args.color, args.color)
    )


if __name__ == "__main__":
    main()
