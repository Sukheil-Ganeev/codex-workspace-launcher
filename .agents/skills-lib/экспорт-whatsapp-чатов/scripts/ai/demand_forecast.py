#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ML модель для прогнозирования спроса на туристические услуги.

Функционал:
1. Подготовка данных (агрегация, feature engineering)
2. Модели: Prophet (основная), ARIMA, Simple Moving Average (baseline)
3. Прогнозы на 30/60/90 дней с confidence intervals
4. Визуализация: интерактивные графики Plotly
5. Рекомендации по промо-акциям и ценообразованию

Входные данные:
- D:/Downloads/Chats/_база/json/operations.json
- D:/Downloads/Chats/_база/json/seasonal_analysis.json (опционально)

Выходные данные:
- D:/Downloads/Chats/_база/json/forecast.json
- D:/Downloads/Chats/_база/json/model_metrics.json
- D:/Downloads/Chats/_база/html/forecast_chart.html
"""

import json
import sys
import warnings
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Подавление предупреждений
warnings.filterwarnings('ignore')

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import JSON_DIR, BASE_DIR, ensure_directories
except ImportError:
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    BASE_DIR = Path("D:/Downloads/Chats/_база")

    def ensure_directories():
        JSON_DIR.mkdir(parents=True, exist_ok=True)
        (BASE_DIR / "html").mkdir(parents=True, exist_ok=True)

# HTML директория
HTML_DIR = BASE_DIR / "html"

# ==============================================================================
# ПРАЗДНИКИ И СЕЗОНЫ ОАЭ
# ==============================================================================

# Праздники ОАЭ и РФ (влияют на спрос)
UAE_HOLIDAYS_FIXED = {
    "01-01": ("Новый год", 1.8),           # +80% спрос
    "01-02": ("Новогодние каникулы", 1.7),
    "01-03": ("Новогодние каникулы", 1.6),
    "01-04": ("Новогодние каникулы", 1.5),
    "01-05": ("Новогодние каникулы", 1.4),
    "01-06": ("Новогодние каникулы", 1.3),
    "01-07": ("Рождество РФ", 1.4),
    "02-23": ("23 февраля", 1.2),
    "03-08": ("8 марта", 1.3),
    "05-01": ("Майские праздники", 1.4),
    "05-09": ("День Победы", 1.3),
    "11-04": ("День народного единства", 1.2),
    "12-02": ("Национальный день ОАЭ", 1.3),
    "12-03": ("Национальный день ОАЭ", 1.3),
    "12-31": ("Новый год", 1.6),
}

# Исламские праздники (плавающие даты, примерные)
ISLAMIC_HOLIDAYS = {
    2024: [
        {"name": "Рамадан", "start": "2024-03-10", "end": "2024-04-09", "multiplier": 0.7},
        {"name": "Eid al-Fitr", "start": "2024-04-10", "end": "2024-04-12", "multiplier": 1.3},
        {"name": "Eid al-Adha", "start": "2024-06-16", "end": "2024-06-19", "multiplier": 1.2},
    ],
    2025: [
        {"name": "Рамадан", "start": "2025-02-28", "end": "2025-03-29", "multiplier": 0.7},
        {"name": "Eid al-Fitr", "start": "2025-03-30", "end": "2025-04-01", "multiplier": 1.3},
        {"name": "Eid al-Adha", "start": "2025-06-06", "end": "2025-06-09", "multiplier": 1.2},
    ],
    2026: [
        {"name": "Рамадан", "start": "2026-02-17", "end": "2026-03-19", "multiplier": 0.7},
        {"name": "Eid al-Fitr", "start": "2026-03-20", "end": "2026-03-22", "multiplier": 1.3},
        {"name": "Eid al-Adha", "start": "2026-05-26", "end": "2026-05-29", "multiplier": 1.2},
    ],
}

# Сезонные коэффициенты ОАЭ
SEASON_COEFFICIENTS = {
    1: 1.5,   # Январь - высокий
    2: 1.4,   # Февраль - высокий
    3: 1.3,   # Март - высокий
    4: 1.2,   # Апрель - средний
    5: 0.7,   # Май - низкий (жара)
    6: 0.5,   # Июнь - очень низкий
    7: 0.4,   # Июль - очень низкий
    8: 0.5,   # Август - низкий
    9: 0.7,   # Сентябрь - начало роста
    10: 1.3,  # Октябрь - высокий
    11: 1.5,  # Ноябрь - высокий
    12: 1.6,  # Декабрь - очень высокий
}

# Коэффициенты дней недели (для туризма)
WEEKDAY_COEFFICIENTS = {
    0: 0.9,   # Понедельник
    1: 0.9,   # Вторник
    2: 1.0,   # Среда
    3: 1.1,   # Четверг
    4: 1.3,   # Пятница (выходной в ОАЭ)
    5: 1.4,   # Суббота
    6: 1.2,   # Воскресенье
}

# Категории услуг
SERVICE_CATEGORIES = {
    "tour": "Экскурсии",
    "transfer": "Трансферы",
    "yacht": "Яхты",
    "tickets": "Билеты",
    "car_rental": "Аренда авто",
    "catering": "Кейтеринг",
    "exchange": "Обмен валюты",
    "other": "Прочее",
}


# ==============================================================================
# ЗАГРУЗКА ДАННЫХ
# ==============================================================================

def load_operations(filepath: Path) -> pd.DataFrame:
    """Загрузить операции из JSON в DataFrame."""

    if not filepath.exists():
        print(f"[ПРЕДУПРЕЖДЕНИЕ] Файл операций не найден: {filepath}")
        return pd.DataFrame()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("[ОШИБКА] Операции должны быть списком")
            return pd.DataFrame()

        print(f"Загружено операций: {len(data)}")

        df = pd.DataFrame(data)

        # Преобразование даты
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])

        return df

    except Exception as e:
        print(f"[ОШИБКА] Не удалось загрузить операции: {e}")
        return pd.DataFrame()


def load_seasonal_analysis(filepath: Path) -> dict:
    """Загрузить результаты сезонного анализа."""

    if not filepath.exists():
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ПРЕДУПРЕЖДЕНИЕ] Не удалось загрузить сезонный анализ: {e}")
        return {}


# ==============================================================================
# FEATURE ENGINEERING
# ==============================================================================

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Создание признаков для модели."""

    if df.empty or 'date' not in df.columns:
        return df

    df = df.copy()

    # Базовые временные признаки
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_year'] = df['date'].dt.dayofyear
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
    df['quarter'] = df['date'].dt.quarter

    # Сезон (высокий/низкий)
    df['is_high_season'] = df['month'].apply(lambda m: m in [1, 2, 3, 10, 11, 12])
    df['season_coef'] = df['month'].map(SEASON_COEFFICIENTS)

    # День недели коэффициент
    df['weekday_coef'] = df['day_of_week'].map(WEEKDAY_COEFFICIENTS)

    # Праздники (фиксированные)
    df['holiday_name'] = df['date'].apply(lambda d: get_holiday_name(d))
    df['is_holiday'] = df['holiday_name'].notna()
    df['holiday_coef'] = df['date'].apply(lambda d: get_holiday_coefficient(d))

    # Исламские праздники
    df['islamic_holiday'] = df['date'].apply(lambda d: get_islamic_holiday(d))
    df['is_ramadan'] = df['islamic_holiday'] == 'Рамадан'

    # Выходные
    df['is_weekend'] = df['day_of_week'].isin([4, 5])  # Пятница-Суббота в ОАЭ

    # Начало/конец месяца (зарплаты)
    df['is_month_start'] = df['day'] <= 5
    df['is_month_end'] = df['day'] >= 25

    return df


def get_holiday_name(date: datetime) -> Optional[str]:
    """Получить название праздника для даты."""

    if pd.isna(date):
        return None

    date_key = date.strftime("%m-%d")
    if date_key in UAE_HOLIDAYS_FIXED:
        return UAE_HOLIDAYS_FIXED[date_key][0]

    return None


def get_holiday_coefficient(date: datetime) -> float:
    """Получить коэффициент праздника для даты."""

    if pd.isna(date):
        return 1.0

    date_key = date.strftime("%m-%d")
    if date_key in UAE_HOLIDAYS_FIXED:
        return UAE_HOLIDAYS_FIXED[date_key][1]

    return 1.0


def get_islamic_holiday(date: datetime) -> Optional[str]:
    """Проверить исламский праздник для даты."""

    if pd.isna(date):
        return None

    date_str = date.strftime("%Y-%m-%d")
    year = date.year

    if year in ISLAMIC_HOLIDAYS:
        for holiday in ISLAMIC_HOLIDAYS[year]:
            if holiday["start"] <= date_str <= holiday["end"]:
                return holiday["name"]

    return None


def aggregate_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """Агрегация операций по дням."""

    if df.empty or 'date' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df['date_only'] = df['date'].dt.date

    # Агрегация
    agg_dict = {
        'date': 'count',  # количество операций
    }

    # Если есть сумма
    if 'amount' in df.columns:
        agg_dict['amount'] = 'sum'

    # Если есть категория
    if 'category' in df.columns or 'type' in df.columns:
        cat_col = 'category' if 'category' in df.columns else 'type'
        # Создаём dummy-переменные для категорий
        for cat in SERVICE_CATEGORIES.keys():
            df[f'is_{cat}'] = (df[cat_col] == cat).astype(int)
            agg_dict[f'is_{cat}'] = 'sum'

    daily = df.groupby('date_only').agg(agg_dict).reset_index()
    daily.columns = ['ds', 'y'] + list(daily.columns[2:])

    # Преобразование даты для Prophet
    daily['ds'] = pd.to_datetime(daily['ds'])

    return daily


def aggregate_by_week(df: pd.DataFrame) -> pd.DataFrame:
    """Агрегация операций по неделям."""

    if df.empty or 'date' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df['week_start'] = df['date'].dt.to_period('W').dt.start_time

    agg_dict = {'date': 'count'}
    if 'amount' in df.columns:
        agg_dict['amount'] = 'sum'

    weekly = df.groupby('week_start').agg(agg_dict).reset_index()
    weekly.columns = ['ds', 'y'] + list(weekly.columns[2:])
    weekly['ds'] = pd.to_datetime(weekly['ds'])

    return weekly


def add_lag_features(df: pd.DataFrame, lags: List[int] = [7, 14, 30]) -> pd.DataFrame:
    """Добавить лаговые признаки."""

    if df.empty or 'y' not in df.columns:
        return df

    df = df.copy()

    for lag in lags:
        df[f'lag_{lag}'] = df['y'].shift(lag)

    # Скользящие средние
    df['rolling_7'] = df['y'].rolling(window=7, min_periods=1).mean()
    df['rolling_14'] = df['y'].rolling(window=14, min_periods=1).mean()
    df['rolling_30'] = df['y'].rolling(window=30, min_periods=1).mean()

    return df


# ==============================================================================
# МОДЕЛИ
# ==============================================================================

class SimpleMovingAverage:
    """Простая скользящая средняя - baseline модель."""

    def __init__(self, window: int = 30):
        self.window = window
        self.last_values = None

    def fit(self, df: pd.DataFrame):
        """Обучение модели."""
        if 'y' in df.columns:
            self.last_values = df['y'].tail(self.window).values
        return self

    def predict(self, periods: int) -> np.ndarray:
        """Прогноз на periods дней."""
        if self.last_values is None:
            return np.zeros(periods)

        avg = np.mean(self.last_values)
        return np.full(periods, avg)

    def predict_with_ci(self, periods: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Прогноз с доверительными интервалами."""
        if self.last_values is None:
            zeros = np.zeros(periods)
            return zeros, zeros, zeros

        avg = np.mean(self.last_values)
        std = np.std(self.last_values)

        forecast = np.full(periods, avg)
        lower = forecast - 1.96 * std
        upper = forecast + 1.96 * std

        return forecast, lower, upper


class ARIMAModel:
    """ARIMA модель для прогнозирования."""

    def __init__(self, order: Tuple[int, int, int] = (1, 1, 1)):
        self.order = order
        self.model = None
        self.fitted = None

    def fit(self, df: pd.DataFrame):
        """Обучение модели."""
        try:
            from statsmodels.tsa.arima.model import ARIMA

            if 'y' not in df.columns or len(df) < 10:
                return self

            y = df['y'].values

            # Fit ARIMA
            self.model = ARIMA(y, order=self.order)
            self.fitted = self.model.fit()

        except ImportError:
            print("[ПРЕДУПРЕЖДЕНИЕ] statsmodels не установлен, ARIMA недоступна")
        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Ошибка ARIMA: {e}")

        return self

    def predict(self, periods: int) -> np.ndarray:
        """Прогноз на periods дней."""
        if self.fitted is None:
            return np.zeros(periods)

        try:
            forecast = self.fitted.forecast(steps=periods)
            return np.maximum(forecast, 0)  # Не допускаем отрицательных значений
        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Ошибка прогноза ARIMA: {e}")
            return np.zeros(periods)

    def predict_with_ci(self, periods: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Прогноз с доверительными интервалами."""
        if self.fitted is None:
            zeros = np.zeros(periods)
            return zeros, zeros, zeros

        try:
            forecast_result = self.fitted.get_forecast(steps=periods)
            forecast = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int()

            return (
                np.maximum(forecast, 0),
                np.maximum(conf_int.iloc[:, 0].values, 0),
                np.maximum(conf_int.iloc[:, 1].values, 0)
            )
        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Ошибка CI ARIMA: {e}")
            forecast = self.predict(periods)
            return forecast, forecast * 0.8, forecast * 1.2


class ProphetModel:
    """Prophet модель для прогнозирования."""

    def __init__(self, yearly_seasonality: bool = True, weekly_seasonality: bool = True):
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.model = None

    def fit(self, df: pd.DataFrame):
        """Обучение модели."""
        try:
            from prophet import Prophet

            if 'ds' not in df.columns or 'y' not in df.columns:
                return self

            if len(df) < 10:
                print("[ПРЕДУПРЕЖДЕНИЕ] Недостаточно данных для Prophet")
                return self

            # Подготовка данных
            train_df = df[['ds', 'y']].dropna().copy()
            train_df['y'] = train_df['y'].astype(float)

            # Создание модели
            self.model = Prophet(
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=self.weekly_seasonality,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10,
            )

            # Добавление праздников ОАЭ/РФ
            holidays_df = self._create_holidays_df()
            if not holidays_df.empty:
                self.model = Prophet(
                    yearly_seasonality=self.yearly_seasonality,
                    weekly_seasonality=self.weekly_seasonality,
                    holidays=holidays_df,
                    changepoint_prior_scale=0.05,
                )

            # Обучение
            self.model.fit(train_df)

        except ImportError:
            print("[ПРЕДУПРЕЖДЕНИЕ] prophet не установлен")
            print("Установите: pip install prophet")
        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Ошибка Prophet: {e}")

        return self

    def _create_holidays_df(self) -> pd.DataFrame:
        """Создание DataFrame праздников для Prophet."""

        holidays = []

        # Фиксированные праздники (на несколько лет)
        for year in range(2023, 2027):
            for date_key, (name, _) in UAE_HOLIDAYS_FIXED.items():
                month, day = map(int, date_key.split('-'))
                try:
                    date = datetime(year, month, day)
                    holidays.append({
                        'holiday': name,
                        'ds': date,
                        'lower_window': 0,
                        'upper_window': 1,
                    })
                except ValueError:
                    continue

        # Исламские праздники
        for year, year_holidays in ISLAMIC_HOLIDAYS.items():
            for h in year_holidays:
                try:
                    start = datetime.strptime(h['start'], "%Y-%m-%d")
                    end = datetime.strptime(h['end'], "%Y-%m-%d")
                    delta = (end - start).days

                    holidays.append({
                        'holiday': h['name'],
                        'ds': start,
                        'lower_window': 0,
                        'upper_window': delta,
                    })
                except Exception:
                    continue

        if holidays:
            return pd.DataFrame(holidays)
        return pd.DataFrame()

    def predict(self, periods: int, start_date: Optional[datetime] = None) -> pd.DataFrame:
        """Прогноз на periods дней."""

        if self.model is None:
            dates = pd.date_range(
                start=start_date or datetime.now(),
                periods=periods,
                freq='D'
            )
            return pd.DataFrame({
                'ds': dates,
                'yhat': np.zeros(periods),
                'yhat_lower': np.zeros(periods),
                'yhat_upper': np.zeros(periods),
            })

        try:
            future = self.model.make_future_dataframe(periods=periods)
            forecast = self.model.predict(future)

            # Возвращаем только прогнозные периоды
            return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)

        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Ошибка прогноза Prophet: {e}")
            dates = pd.date_range(start=datetime.now(), periods=periods, freq='D')
            return pd.DataFrame({
                'ds': dates,
                'yhat': np.zeros(periods),
                'yhat_lower': np.zeros(periods),
                'yhat_upper': np.zeros(periods),
            })

    def get_components(self) -> Optional[pd.DataFrame]:
        """Получить компоненты модели (тренд, сезонность)."""

        if self.model is None:
            return None

        try:
            future = self.model.make_future_dataframe(periods=30)
            forecast = self.model.predict(future)
            return forecast[['ds', 'trend', 'yearly', 'weekly']].copy()
        except Exception:
            return None


# ==============================================================================
# МЕТРИКИ КАЧЕСТВА
# ==============================================================================

def calculate_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict:
    """Расчёт метрик качества модели."""

    # Убираем NaN
    mask = ~np.isnan(actual) & ~np.isnan(predicted)
    actual = actual[mask]
    predicted = predicted[mask]

    if len(actual) == 0:
        return {
            'mae': None,
            'rmse': None,
            'mape': None,
            'r2': None,
        }

    # MAE
    mae = np.mean(np.abs(actual - predicted))

    # RMSE
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))

    # MAPE (избегаем деления на 0)
    non_zero = actual != 0
    if np.any(non_zero):
        mape = np.mean(np.abs((actual[non_zero] - predicted[non_zero]) / actual[non_zero])) * 100
    else:
        mape = None

    # R2
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else None

    return {
        'mae': round(mae, 2) if mae is not None else None,
        'rmse': round(rmse, 2) if rmse is not None else None,
        'mape': round(mape, 2) if mape is not None else None,
        'r2': round(r2, 4) if r2 is not None else None,
    }


def cross_validate(df: pd.DataFrame, model_class, n_splits: int = 3, **model_kwargs) -> dict:
    """Кросс-валидация модели."""

    if len(df) < 30:
        return {'avg_mae': None, 'avg_rmse': None}

    fold_size = len(df) // (n_splits + 1)
    metrics_list = []

    for i in range(n_splits):
        train_end = (i + 1) * fold_size
        test_end = train_end + fold_size

        if test_end > len(df):
            break

        train = df.iloc[:train_end]
        test = df.iloc[train_end:test_end]

        model = model_class(**model_kwargs)
        model.fit(train)

        if hasattr(model, 'predict'):
            if isinstance(model, ProphetModel):
                forecast = model.predict(len(test))
                predicted = forecast['yhat'].values
            else:
                predicted = model.predict(len(test))

            actual = test['y'].values
            fold_metrics = calculate_metrics(actual, predicted)
            metrics_list.append(fold_metrics)

    if not metrics_list:
        return {'avg_mae': None, 'avg_rmse': None}

    return {
        'avg_mae': np.mean([m['mae'] for m in metrics_list if m['mae'] is not None]),
        'avg_rmse': np.mean([m['rmse'] for m in metrics_list if m['rmse'] is not None]),
        'avg_mape': np.mean([m['mape'] for m in metrics_list if m['mape'] is not None]),
    }


# ==============================================================================
# ВИЗУАЛИЗАЦИЯ
# ==============================================================================

def create_forecast_chart(
    historical: pd.DataFrame,
    forecast: pd.DataFrame,
    title: str = "Прогноз спроса на туристические услуги"
) -> str:
    """Создание интерактивного графика Plotly."""

    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("[ПРЕДУПРЕЖДЕНИЕ] plotly не установлен")
        return ""

    # Создание фигуры с подграфиками
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        subplot_titles=('Прогноз спроса', 'Сезонные компоненты'),
        vertical_spacing=0.15,
    )

    # Исторические данные
    if not historical.empty and 'ds' in historical.columns and 'y' in historical.columns:
        fig.add_trace(
            go.Scatter(
                x=historical['ds'],
                y=historical['y'],
                mode='lines',
                name='Факт',
                line=dict(color='#2E86AB', width=2),
            ),
            row=1, col=1
        )

    # Прогноз
    if not forecast.empty:
        # Основная линия прогноза
        fig.add_trace(
            go.Scatter(
                x=forecast['ds'],
                y=forecast['yhat'],
                mode='lines',
                name='Прогноз',
                line=dict(color='#E94F37', width=2, dash='dash'),
            ),
            row=1, col=1
        )

        # Доверительный интервал
        if 'yhat_lower' in forecast.columns and 'yhat_upper' in forecast.columns:
            fig.add_trace(
                go.Scatter(
                    x=pd.concat([forecast['ds'], forecast['ds'][::-1]]),
                    y=pd.concat([forecast['yhat_upper'], forecast['yhat_lower'][::-1]]),
                    fill='toself',
                    fillcolor='rgba(233, 79, 55, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='95% CI',
                    showlegend=True,
                ),
                row=1, col=1
            )

    # Сезонные компоненты (если есть месячные данные)
    if not historical.empty and 'ds' in historical.columns:
        monthly = historical.copy()
        monthly['month'] = monthly['ds'].dt.month
        monthly_avg = monthly.groupby('month')['y'].mean().reset_index()

        if not monthly_avg.empty:
            months_ru = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
                        'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

            fig.add_trace(
                go.Bar(
                    x=[months_ru[m-1] for m in monthly_avg['month']],
                    y=monthly_avg['y'],
                    name='Сезонность',
                    marker_color=['#E94F37' if m in [1,2,3,10,11,12] else '#2E86AB'
                                 for m in monthly_avg['month']],
                ),
                row=2, col=1
            )

    # Настройка layout
    fig.update_layout(
        title=dict(text=title, font=dict(size=20)),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=700,
        template='plotly_white',
    )

    fig.update_xaxes(title_text="Дата", row=1, col=1)
    fig.update_yaxes(title_text="Количество операций", row=1, col=1)
    fig.update_xaxes(title_text="Месяц", row=2, col=1)
    fig.update_yaxes(title_text="Среднее", row=2, col=1)

    return fig.to_html(full_html=True, include_plotlyjs=True)


def create_category_chart(forecasts_by_category: dict) -> str:
    """Создание графика прогноза по категориям."""

    try:
        import plotly.graph_objects as go
    except ImportError:
        return ""

    fig = go.Figure()

    colors = ['#2E86AB', '#E94F37', '#F18F01', '#C73E1D', '#3A506B', '#5BC0BE', '#6FFFE9']

    for i, (category, data) in enumerate(forecasts_by_category.items()):
        if 'ds' in data and 'yhat' in data:
            fig.add_trace(
                go.Scatter(
                    x=data['ds'],
                    y=data['yhat'],
                    mode='lines',
                    name=SERVICE_CATEGORIES.get(category, category),
                    line=dict(color=colors[i % len(colors)], width=2),
                )
            )

    fig.update_layout(
        title="Прогноз по категориям услуг",
        xaxis_title="Дата",
        yaxis_title="Количество",
        template='plotly_white',
        height=500,
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


# ==============================================================================
# РЕКОМЕНДАЦИИ
# ==============================================================================

def generate_recommendations(forecast: pd.DataFrame, historical: pd.DataFrame) -> List[dict]:
    """Генерация рекомендаций на основе прогноза."""

    recommendations = []

    if forecast.empty:
        return recommendations

    # Анализ прогноза
    forecast = forecast.copy()
    forecast['month'] = forecast['ds'].dt.month
    forecast['day_of_week'] = forecast['ds'].dt.dayofweek

    # 1. Оптимальные даты для промо-акций
    # Ищем периоды низкого спроса
    avg_forecast = forecast['yhat'].mean()
    low_demand_dates = forecast[forecast['yhat'] < avg_forecast * 0.7]['ds'].tolist()

    if low_demand_dates:
        # Группируем по месяцам
        low_months = pd.to_datetime(low_demand_dates).month.value_counts()
        top_low_months = low_months.head(2).index.tolist()

        months_ru = {
            1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
            5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
            9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'
        }

        month_names = [months_ru.get(m, str(m)) for m in top_low_months]

        recommendations.append({
            'type': 'promo',
            'priority': 'high',
            'title': 'Оптимальное время для промо-акций',
            'description': f"Рекомендуется запустить промо-акции в {', '.join(month_names)} - "
                          f"прогнозируется низкий спрос. Это поможет стимулировать продажи.",
            'dates': [d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d)
                     for d in low_demand_dates[:5]],
        })

    # 2. Предупреждения о пиках
    high_demand_dates = forecast[forecast['yhat'] > avg_forecast * 1.5]['ds'].tolist()

    if high_demand_dates:
        recommendations.append({
            'type': 'peak_warning',
            'priority': 'high',
            'title': 'Ожидаются пики спроса',
            'description': f"В ближайшие {len(high_demand_dates)} дней прогнозируется повышенный спрос. "
                          f"Рекомендуется: увеличить штат, подготовить дополнительные ресурсы.",
            'dates': [d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d)
                     for d in high_demand_dates[:10]],
        })

    # 3. Рекомендации по ценообразованию
    # Высокий сезон
    high_season_forecast = forecast[forecast['month'].isin([1, 2, 3, 10, 11, 12])]
    low_season_forecast = forecast[forecast['month'].isin([5, 6, 7, 8, 9])]

    if not high_season_forecast.empty and not low_season_forecast.empty:
        high_avg = high_season_forecast['yhat'].mean()
        low_avg = low_season_forecast['yhat'].mean()

        if low_avg > 0:
            ratio = high_avg / low_avg

            recommendations.append({
                'type': 'pricing',
                'priority': 'medium',
                'title': 'Рекомендации по ценообразованию',
                'description': f"Спрос в высокий сезон в {ratio:.1f}x выше низкого. "
                              f"Рекомендуется: +20-30% к ценам в высокий сезон (окт-апр), "
                              f"скидки до -30% в низкий сезон (май-сен).",
                'high_season_months': [10, 11, 12, 1, 2, 3, 4],
                'low_season_months': [5, 6, 7, 8, 9],
                'demand_ratio': round(ratio, 2),
            })

    # 4. Рекомендации по дням недели
    weekday_avg = forecast.groupby('day_of_week')['yhat'].mean()
    if not weekday_avg.empty:
        best_day = weekday_avg.idxmax()
        worst_day = weekday_avg.idxmin()

        days_ru = {
            0: 'понедельник', 1: 'вторник', 2: 'среда', 3: 'четверг',
            4: 'пятница', 5: 'суббота', 6: 'воскресенье'
        }

        recommendations.append({
            'type': 'schedule',
            'priority': 'low',
            'title': 'Оптимизация расписания',
            'description': f"Пик спроса - {days_ru[best_day]}, минимум - {days_ru[worst_day]}. "
                          f"Рекомендуется: планировать выходные сотрудников на {days_ru[worst_day]}.",
            'best_day': days_ru[best_day],
            'worst_day': days_ru[worst_day],
        })

    # 5. Рамадан
    ramadan_dates = []
    for year, holidays in ISLAMIC_HOLIDAYS.items():
        for h in holidays:
            if h['name'] == 'Рамадан':
                try:
                    start = datetime.strptime(h['start'], "%Y-%m-%d")
                    end = datetime.strptime(h['end'], "%Y-%m-%d")
                    if start <= datetime.now() + timedelta(days=180) <= end or \
                       datetime.now() <= start <= datetime.now() + timedelta(days=180):
                        ramadan_dates.append((h['start'], h['end']))
                except Exception:
                    pass

    if ramadan_dates:
        recommendations.append({
            'type': 'cultural',
            'priority': 'medium',
            'title': 'Рамадан - корректировка стратегии',
            'description': f"В период Рамадана ({ramadan_dates[0][0]} - {ramadan_dates[0][1]}) "
                          f"спрос снижается на 20-30%. Рекомендуется: акцент на вечерние туры, "
                          f"iftar-ужины, специальные предложения для мусульман.",
            'ramadan_period': ramadan_dates[0],
        })

    return recommendations


# ==============================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==============================================================================

def run_forecast(
    operations_file: Path,
    seasonal_file: Optional[Path] = None,
    forecast_days: int = 90,
    output_dir: Optional[Path] = None,
) -> dict:
    """Основная функция прогнозирования."""

    print("=" * 60)
    print("ПРОГНОЗИРОВАНИЕ СПРОСА НА ТУРИСТИЧЕСКИЕ УСЛУГИ")
    print("=" * 60)

    # Директории
    if output_dir is None:
        output_dir = JSON_DIR

    output_dir.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)

    # Загрузка данных
    print("\n1. Загрузка данных...")
    df = load_operations(operations_file)

    if df.empty:
        print("[ОШИБКА] Нет данных для анализа")
        print("Создаю демо-данные для примера...")

        # Создание демо-данных
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        np.random.seed(42)

        demo_data = []
        for date in dates:
            # Базовый спрос
            base = 10

            # Сезонность
            month_coef = SEASON_COEFFICIENTS.get(date.month, 1.0)
            weekday_coef = WEEKDAY_COEFFICIENTS.get(date.dayofweek, 1.0)

            # Шум
            noise = np.random.normal(0, 2)

            count = max(0, int(base * month_coef * weekday_coef + noise))

            for _ in range(count):
                demo_data.append({
                    'date': date,
                    'category': np.random.choice(list(SERVICE_CATEGORIES.keys())),
                    'amount': np.random.uniform(100, 1000),
                })

        df = pd.DataFrame(demo_data)
        print(f"Создано демо-операций: {len(df)}")

    # Feature engineering
    print("\n2. Подготовка признаков...")
    df = create_features(df)

    # Агрегация по дням
    daily = aggregate_by_day(df)
    print(f"   Дней с данными: {len(daily)}")

    # Добавление лагов
    daily = add_lag_features(daily)

    # Обучение моделей
    print("\n3. Обучение моделей...")

    results = {
        'models': {},
        'forecasts': {},
        'metrics': {},
    }

    # Simple Moving Average (baseline)
    print("   - Simple Moving Average (baseline)...")
    sma = SimpleMovingAverage(window=30)
    sma.fit(daily)
    sma_forecast, sma_lower, sma_upper = sma.predict_with_ci(forecast_days)

    results['models']['sma'] = 'trained'

    # ARIMA
    print("   - ARIMA...")
    arima = ARIMAModel(order=(1, 1, 1))
    arima.fit(daily)
    arima_forecast, arima_lower, arima_upper = arima.predict_with_ci(forecast_days)

    results['models']['arima'] = 'trained' if arima.fitted else 'failed'

    # Prophet (основная модель)
    print("   - Prophet (основная)...")
    prophet = ProphetModel(yearly_seasonality=True, weekly_seasonality=True)
    prophet.fit(daily)

    if prophet.model is not None:
        prophet_forecast = prophet.predict(forecast_days)
        results['models']['prophet'] = 'trained'
    else:
        # Fallback к ARIMA
        print("   [!] Prophet недоступен, используем ARIMA")
        last_date = daily['ds'].max() if not daily.empty else datetime.now()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days, freq='D')
        prophet_forecast = pd.DataFrame({
            'ds': future_dates,
            'yhat': arima_forecast,
            'yhat_lower': arima_lower,
            'yhat_upper': arima_upper,
        })
        results['models']['prophet'] = 'fallback_arima'

    # Расчёт метрик (на последних 30 днях)
    print("\n4. Оценка качества моделей...")

    if len(daily) > 30:
        train = daily.iloc[:-30]
        test = daily.iloc[-30:]

        # SMA
        sma_test = SimpleMovingAverage(window=30)
        sma_test.fit(train)
        sma_pred = sma_test.predict(30)
        results['metrics']['sma'] = calculate_metrics(test['y'].values, sma_pred)

        # ARIMA
        arima_test = ARIMAModel(order=(1, 1, 1))
        arima_test.fit(train)
        arima_pred = arima_test.predict(30)
        results['metrics']['arima'] = calculate_metrics(test['y'].values, arima_pred)

        # Prophet
        if prophet.model is not None:
            prophet_test = ProphetModel()
            prophet_test.fit(train)
            prophet_pred_df = prophet_test.predict(30)
            results['metrics']['prophet'] = calculate_metrics(
                test['y'].values,
                prophet_pred_df['yhat'].values
            )
        else:
            results['metrics']['prophet'] = results['metrics']['arima']

    # Вывод метрик
    print("\n   Метрики моделей (на тестовых данных):")
    for model_name, metrics in results['metrics'].items():
        if metrics.get('mae') is not None:
            print(f"   {model_name}: MAE={metrics['mae']:.2f}, RMSE={metrics['rmse']:.2f}")

    # Выбор лучшей модели
    best_model = 'prophet'
    best_mae = float('inf')

    for model_name, metrics in results['metrics'].items():
        if metrics.get('mae') is not None and metrics['mae'] < best_mae:
            best_mae = metrics['mae']
            best_model = model_name

    print(f"\n   Лучшая модель: {best_model}")

    # Формирование финального прогноза
    print("\n5. Формирование прогноза...")

    # Используем Prophet как основную модель
    final_forecast = prophet_forecast.copy()

    # Генерация рекомендаций
    print("\n6. Генерация рекомендаций...")
    recommendations = generate_recommendations(final_forecast, daily)

    for rec in recommendations[:3]:
        print(f"   [{rec['priority'].upper()}] {rec['title']}")

    # Сохранение результатов
    print("\n7. Сохранение результатов...")

    # forecast.json
    forecast_output = {
        'generated_at': datetime.now().isoformat(),
        'forecast_days': forecast_days,
        'best_model': best_model,
        'historical_summary': {
            'total_days': len(daily),
            'total_operations': int(daily['y'].sum()) if not daily.empty else 0,
            'avg_daily': round(daily['y'].mean(), 2) if not daily.empty else 0,
            'date_range': {
                'from': daily['ds'].min().strftime('%Y-%m-%d') if not daily.empty else None,
                'to': daily['ds'].max().strftime('%Y-%m-%d') if not daily.empty else None,
            }
        },
        'forecast': {
            'dates': final_forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
            'values': [round(v, 2) for v in final_forecast['yhat'].tolist()],
            'lower_bound': [round(v, 2) for v in final_forecast['yhat_lower'].tolist()],
            'upper_bound': [round(v, 2) for v in final_forecast['yhat_upper'].tolist()],
        },
        'forecast_summary': {
            '30_days': {
                'total': round(final_forecast['yhat'].head(30).sum(), 0),
                'avg_daily': round(final_forecast['yhat'].head(30).mean(), 2),
            },
            '60_days': {
                'total': round(final_forecast['yhat'].head(60).sum(), 0),
                'avg_daily': round(final_forecast['yhat'].head(60).mean(), 2),
            },
            '90_days': {
                'total': round(final_forecast['yhat'].sum(), 0),
                'avg_daily': round(final_forecast['yhat'].mean(), 2),
            },
        },
        'recommendations': recommendations,
    }

    forecast_file = output_dir / 'forecast.json'
    with open(forecast_file, 'w', encoding='utf-8') as f:
        json.dump(forecast_output, f, ensure_ascii=False, indent=2)
    print(f"   - {forecast_file}")

    # model_metrics.json
    metrics_output = {
        'generated_at': datetime.now().isoformat(),
        'models': results['models'],
        'metrics': results['metrics'],
        'best_model': best_model,
        'training_data': {
            'records': len(daily),
            'features': list(daily.columns) if not daily.empty else [],
        }
    }

    metrics_file = output_dir / 'model_metrics.json'
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics_output, f, ensure_ascii=False, indent=2)
    print(f"   - {metrics_file}")

    # forecast_chart.html
    print("\n8. Создание графиков...")
    chart_html = create_forecast_chart(daily, final_forecast)

    if chart_html:
        chart_file = HTML_DIR / 'forecast_chart.html'
        with open(chart_file, 'w', encoding='utf-8') as f:
            f.write(chart_html)
        print(f"   - {chart_file}")

    # Итоги
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)

    print(f"\nПрогноз на {forecast_days} дней:")
    print(f"  - Ожидаемое количество операций: {forecast_output['forecast_summary']['90_days']['total']:.0f}")
    print(f"  - Среднее в день: {forecast_output['forecast_summary']['90_days']['avg_daily']:.1f}")

    print(f"\nЛучшая модель: {best_model}")
    if best_model in results['metrics'] and results['metrics'][best_model].get('mae'):
        print(f"  - MAE: {results['metrics'][best_model]['mae']:.2f}")
        print(f"  - RMSE: {results['metrics'][best_model]['rmse']:.2f}")

    print(f"\nФайлы сохранены:")
    print(f"  - {forecast_file}")
    print(f"  - {metrics_file}")
    if chart_html:
        print(f"  - {HTML_DIR / 'forecast_chart.html'}")

    return forecast_output


def main():
    """Точка входа."""

    import argparse

    parser = argparse.ArgumentParser(description="Прогнозирование спроса на туристические услуги")
    parser.add_argument(
        "--operations",
        default=str(JSON_DIR / "operations.json"),
        help="Путь к файлу операций (JSON)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Количество дней для прогноза (по умолчанию 90)"
    )
    parser.add_argument(
        "--output",
        default=str(JSON_DIR),
        help="Директория для выходных файлов"
    )

    args = parser.parse_args()

    # Создание директорий
    ensure_directories()

    # Запуск прогнозирования
    run_forecast(
        operations_file=Path(args.operations),
        forecast_days=args.days,
        output_dir=Path(args.output),
    )


if __name__ == "__main__":
    main()
