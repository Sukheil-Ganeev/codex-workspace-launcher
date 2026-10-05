#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивный веб-дашборд для визуализации метрик WhatsApp чатов.

Использование:
    streamlit run dashboard.py

Страницы:
    1. Обзор (Home) - KPI карточки, графики, топ контактов
    2. Контакты - Таблица с фильтрами, карточки профилей
    3. Операции - Воронка продаж, выручка, P&L
    4. Аналитика - Сезонность, LTV, время отклика, тренды
    5. Чаты - Просмотр переписки, поиск по сообщениям
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ═══════════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════════

BASE_DIR = Path("D:/Downloads/Chats/_база")
JSON_DIR = BASE_DIR / "json"
RAW_DIR = BASE_DIR / "raw"
MD_DIR = BASE_DIR / "md"

# Цветовая схема
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#bcbd22",
    "info": "#17becf",
    "purple": "#9467bd",
    "pink": "#e377c2",
    "gray": "#7f7f7f",
    "brown": "#8c564b",
}

# Типы контактов с русскими названиями
CONTACT_TYPE_NAMES = {
    "клиенты": "Клиенты",
    "агенты": "Агенты",
    "поставщики": "Поставщики",
    "сотрудники": "Сотрудники",
    "clients": "Клиенты",
    "agents": "Агенты",
    "suppliers": "Поставщики",
    "employees": "Сотрудники",
}

# Названия стадий воронки
FUNNEL_STAGE_NAMES = {
    "inquiry": "Запрос",
    "quote": "Расчёт",
    "booking": "Бронь",
    "payment": "Оплата",
    "completed": "Выполнено",
    "lost": "Потеряно",
}


# ═══════════════════════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def load_json_file(filepath: Path) -> Any:
    """Загрузить JSON файл с кэшированием."""
    if not filepath.exists():
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Ошибка загрузки {filepath.name}: {e}")
        return None


@st.cache_data(ttl=300)
def load_jsonl_file(filepath: Path, limit: int = 0) -> List[Dict]:
    """Загрузить JSONL файл с кэшированием."""
    if not filepath.exists():
        return []

    messages = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if limit > 0 and i >= limit:
                    break
                line = line.strip()
                if line:
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        st.warning(f"Ошибка загрузки {filepath.name}: {e}")

    return messages


def load_contacts() -> pd.DataFrame:
    """Загрузить контакты в DataFrame."""
    data = load_json_file(JSON_DIR / "contacts.json")

    if data is None:
        return pd.DataFrame()

    # Поддержка разных форматов
    if isinstance(data, list):
        contacts = data
    elif isinstance(data, dict) and "contacts" in data:
        contacts = data["contacts"]
    else:
        return pd.DataFrame()

    df = pd.DataFrame(contacts)

    # Добавление LTV данных если есть
    if "ltv" in df.columns:
        ltv_df = pd.json_normalize(df["ltv"].dropna())
        if not ltv_df.empty:
            ltv_df.index = df["ltv"].dropna().index
            for col in ltv_df.columns:
                df.loc[ltv_df.index, f"ltv_{col}"] = ltv_df[col]

    return df


def load_operations() -> pd.DataFrame:
    """Загрузить операции в DataFrame."""
    data = load_json_file(JSON_DIR / "operations.json")

    if data is None or not isinstance(data, list):
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # Преобразование даты
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df


def load_sales_funnel() -> Dict:
    """Загрузить данные воронки продаж."""
    return load_json_file(JSON_DIR / "sales_funnel.json") or {}


def load_ltv_analysis() -> Dict:
    """Загрузить LTV анализ."""
    return load_json_file(JSON_DIR / "ltv_analysis.json") or {}


def load_seasonal_analysis() -> Dict:
    """Загрузить сезонный анализ."""
    return load_json_file(JSON_DIR / "seasonal_analysis.json") or {}


def load_response_times() -> Dict:
    """Загрузить метрики времени отклика."""
    return load_json_file(JSON_DIR / "response_times.json") or {}


def load_profiles() -> pd.DataFrame:
    """Загрузить профили клиентов."""
    data = load_json_file(JSON_DIR / "profiles.json")

    if data is None:
        return pd.DataFrame()

    if isinstance(data, dict) and "profiles" in data:
        profiles = data["profiles"]
    elif isinstance(data, list):
        profiles = data
    else:
        return pd.DataFrame()

    return pd.DataFrame(profiles)


def load_messages_sample(limit: int = 10000) -> pd.DataFrame:
    """Загрузить выборку сообщений."""
    messages = load_jsonl_file(RAW_DIR / "all_messages.jsonl", limit=limit)

    if not messages:
        return pd.DataFrame()

    df = pd.DataFrame(messages)

    # Преобразование даты
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

    return df


# ═══════════════════════════════════════════════════════════════════════════════
# КОМПОНЕНТЫ UI
# ═══════════════════════════════════════════════════════════════════════════════

def metric_card(label: str, value: Any, delta: Optional[str] = None, delta_color: str = "normal"):
    """Отобразить карточку метрики."""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def kpi_row(metrics: List[Dict]):
    """Отобразить ряд KPI карточек."""
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            metric_card(
                label=metric.get("label", ""),
                value=metric.get("value", 0),
                delta=metric.get("delta"),
                delta_color=metric.get("delta_color", "normal"),
            )


def info_box(title: str, content: str, icon: str = "info"):
    """Информационный блок."""
    icons = {
        "info": "blue",
        "success": "green",
        "warning": "orange",
        "error": "red",
    }
    color = icons.get(icon, "blue")
    st.markdown(
        f"""
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: {color}10; border-left: 4px solid {color};">
            <strong>{title}</strong><br>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# СТРАНИЦА: ОБЗОР (HOME)
# ═══════════════════════════════════════════════════════════════════════════════

def page_home():
    """Главная страница с обзором."""
    st.title("Обзор")

    # Загрузка данных
    contacts_df = load_contacts()
    operations_df = load_operations()
    funnel_data = load_sales_funnel()
    seasonal_data = load_seasonal_analysis()

    # === KPI КАРТОЧКИ ===
    st.subheader("Ключевые показатели")

    total_contacts = len(contacts_df) if not contacts_df.empty else 0
    total_messages = seasonal_data.get("summary", {}).get("total_messages", 0)

    # Расчёт выручки
    total_revenue = 0
    if not operations_df.empty and "amount" in operations_df.columns:
        aed_ops = operations_df[operations_df.get("currency", "AED") == "AED"]
        total_revenue = aed_ops["amount"].sum() if not aed_ops.empty else operations_df["amount"].sum()

    # Конверсия из воронки
    funnel = funnel_data.get("funnel", {})
    completed_rate = funnel.get("completed", {}).get("rate", 0)
    conversion_pct = f"{completed_rate * 100:.1f}%"

    kpi_row([
        {"label": "Контакты", "value": f"{total_contacts:,}"},
        {"label": "Сообщения", "value": f"{total_messages:,}"},
        {"label": "Выручка (AED)", "value": f"{total_revenue:,.0f}"},
        {"label": "Конверсия", "value": conversion_pct},
    ])

    st.divider()

    # === ГРАФИКИ ===
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Сообщения по дням")

        by_month = seasonal_data.get("by_month", {})
        if by_month:
            months = sorted(by_month.keys())[-12:]  # Последние 12 месяцев
            values = [by_month[m].get("messages", 0) for m in months]

            fig = px.bar(
                x=months,
                y=values,
                labels={"x": "Месяц", "y": "Сообщения"},
                color_discrete_sequence=[COLORS["primary"]],
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                height=300,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных о сообщениях")

    with col2:
        st.subheader("Типы контактов")

        if not contacts_df.empty and "type" in contacts_df.columns:
            type_counts = contacts_df["type"].value_counts()

            labels = [CONTACT_TYPE_NAMES.get(t, t) for t in type_counts.index]

            fig = px.pie(
                names=labels,
                values=type_counts.values,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных о контактах")

    st.divider()

    # === ТОП-5 АКТИВНЫХ КОНТАКТОВ ===
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Топ-5 активных контактов")

        if not contacts_df.empty:
            # Сортировка по количеству сообщений или LTV
            if "message_count" in contacts_df.columns:
                top_contacts = contacts_df.nlargest(5, "message_count")[["name", "type", "message_count"]]
            elif "ltv_historical_ltv_aed" in contacts_df.columns:
                top_contacts = contacts_df.nlargest(5, "ltv_historical_ltv_aed")[["name", "type", "ltv_historical_ltv_aed"]]
                top_contacts = top_contacts.rename(columns={"ltv_historical_ltv_aed": "LTV (AED)"})
            else:
                top_contacts = contacts_df.head(5)[["name", "type"]] if "name" in contacts_df.columns else pd.DataFrame()

            if not top_contacts.empty:
                # Переименовать колонки для отображения
                display_cols = {"name": "Имя", "type": "Тип", "message_count": "Сообщения"}
                top_contacts = top_contacts.rename(columns=display_cols)
                st.dataframe(top_contacts, use_container_width=True, hide_index=True)
            else:
                st.info("Нет данных")
        else:
            st.info("Нет данных о контактах")

    with col2:
        st.subheader("Последние операции")

        if not operations_df.empty:
            recent_ops = operations_df.nlargest(5, "date")[["date", "amount", "currency", "type"]] if "date" in operations_df.columns else operations_df.head(5)

            if not recent_ops.empty:
                display_cols = {"date": "Дата", "amount": "Сумма", "currency": "Валюта", "type": "Тип"}
                recent_ops = recent_ops.rename(columns=display_cols)
                st.dataframe(recent_ops, use_container_width=True, hide_index=True)
            else:
                st.info("Нет данных")
        else:
            st.info("Нет данных об операциях")


# ═══════════════════════════════════════════════════════════════════════════════
# СТРАНИЦА: КОНТАКТЫ
# ═══════════════════════════════════════════════════════════════════════════════

def page_contacts():
    """Страница управления контактами."""
    st.title("Контакты")

    contacts_df = load_contacts()
    profiles_df = load_profiles()

    if contacts_df.empty:
        st.warning("Файл контактов не найден или пуст")
        st.info(f"Ожидаемый путь: {JSON_DIR / 'contacts.json'}")
        return

    # === ФИЛЬТРЫ ===
    st.subheader("Фильтры")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Фильтр по типу
        types = ["Все"] + list(contacts_df["type"].dropna().unique()) if "type" in contacts_df.columns else ["Все"]
        selected_type = st.selectbox("Тип контакта", types)

    with col2:
        # Фильтр по источнику
        sources = ["Все"]
        if "source" in contacts_df.columns:
            sources += list(contacts_df["source"].dropna().unique())
        selected_source = st.selectbox("Источник", sources)

    with col3:
        # Поиск
        search_query = st.text_input("Поиск (имя/телефон)", "")

    # Применение фильтров
    filtered_df = contacts_df.copy()

    if selected_type != "Все" and "type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["type"] == selected_type]

    if selected_source != "Все" and "source" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["source"] == selected_source]

    if search_query:
        mask = pd.Series(False, index=filtered_df.index)
        if "name" in filtered_df.columns:
            mask |= filtered_df["name"].str.contains(search_query, case=False, na=False)
        if "phone" in filtered_df.columns:
            mask |= filtered_df["phone"].str.contains(search_query, case=False, na=False)
        filtered_df = filtered_df[mask]

    st.divider()

    # === ТАБЛИЦА КОНТАКТОВ ===
    st.subheader(f"Контакты ({len(filtered_df)})")

    # Выбор колонок для отображения
    display_columns = ["name", "phone", "type"]
    if "ltv_historical_ltv_aed" in filtered_df.columns:
        display_columns.append("ltv_historical_ltv_aed")
    if "ltv_segment" in filtered_df.columns:
        display_columns.append("ltv_segment")

    available_cols = [c for c in display_columns if c in filtered_df.columns]

    if available_cols:
        display_df = filtered_df[available_cols].copy()

        # Переименование колонок
        col_names = {
            "name": "Имя",
            "phone": "Телефон",
            "type": "Тип",
            "ltv_historical_ltv_aed": "LTV (AED)",
            "ltv_segment": "Сегмент",
        }
        display_df = display_df.rename(columns=col_names)

        # Отображение таблицы с выбором строки
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
        )

        # Показать карточку выбранного контакта
        if event.selection and event.selection.rows:
            selected_idx = event.selection.rows[0]
            selected_contact = filtered_df.iloc[selected_idx]

            st.divider()
            st.subheader("Карточка контакта")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Имя:** {selected_contact.get('name', 'N/A')}")
                st.markdown(f"**Телефон:** {selected_contact.get('phone', 'N/A')}")
                st.markdown(f"**Тип:** {CONTACT_TYPE_NAMES.get(selected_contact.get('type', ''), selected_contact.get('type', 'N/A'))}")

                if "jid" in selected_contact:
                    st.markdown(f"**JID:** `{selected_contact['jid']}`")

            with col2:
                if "ltv_historical_ltv_aed" in selected_contact:
                    st.markdown(f"**LTV:** {selected_contact['ltv_historical_ltv_aed']:,.0f} AED")
                if "ltv_segment" in selected_contact:
                    st.markdown(f"**Сегмент:** {selected_contact['ltv_segment']}")
                if "ltv_orders_count" in selected_contact:
                    st.markdown(f"**Заказов:** {selected_contact['ltv_orders_count']}")
                if "ltv_churn_risk" in selected_contact:
                    risk = selected_contact["ltv_churn_risk"]
                    risk_color = {"low": "green", "medium": "orange", "high": "red"}.get(risk, "gray")
                    st.markdown(f"**Риск оттока:** :{risk_color}[{risk}]")
    else:
        st.info("Нет данных для отображения")

    st.divider()

    # === PIE CHART КЛАССИФИКАЦИИ ===
    st.subheader("Классификация контактов")

    if "type" in contacts_df.columns:
        type_counts = contacts_df["type"].value_counts()

        fig = px.pie(
            names=[CONTACT_TYPE_NAMES.get(t, t) for t in type_counts.index],
            values=type_counts.values,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4,
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# СТРАНИЦА: ОПЕРАЦИИ
# ═══════════════════════════════════════════════════════════════════════════════

def page_operations():
    """Страница операций и воронки продаж."""
    st.title("Операции")

    operations_df = load_operations()
    funnel_data = load_sales_funnel()

    # === ВОРОНКА ПРОДАЖ ===
    st.subheader("Воронка продаж")

    funnel = funnel_data.get("funnel", {})

    if funnel:
        # Данные для воронки
        stages = ["inquiry", "quote", "booking", "payment", "completed"]
        values = [funnel.get(s, {}).get("count", 0) for s in stages]
        labels = [FUNNEL_STAGE_NAMES.get(s, s) for s in stages]

        fig = go.Figure(go.Funnel(
            y=labels,
            x=values,
            textposition="inside",
            textinfo="value+percent initial",
            marker=dict(color=[COLORS["primary"], COLORS["secondary"], COLORS["info"], COLORS["success"], COLORS["purple"]]),
        ))
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Потерянные
        lost = funnel.get("lost", {})
        if lost.get("count", 0) > 0:
            st.warning(f"Потеряно: {lost['count']} ({lost.get('rate', 0) * 100:.1f}%)")

        # Причины потерь
        lost_reasons = funnel_data.get("lost_reasons", {})
        if lost_reasons:
            st.markdown("**Причины потерь:**")
            reason_names = {
                "price": "Цена",
                "no_response": "Нет ответа",
                "competitor": "Конкурент",
                "cancelled": "Отмена",
                "timing": "Время",
            }
            for reason, count in sorted(lost_reasons.items(), key=lambda x: x[1], reverse=True):
                name = reason_names.get(reason, reason)
                st.text(f"  {name}: {count}")
    else:
        st.info("Данные воронки не найдены")
        st.info(f"Запустите build_sales_funnel.py для генерации данных")

    st.divider()

    # === ВЫРУЧКА ПО ТИПАМ УСЛУГ ===
    st.subheader("Выручка по типам услуг")

    if not operations_df.empty and "type" in operations_df.columns and "amount" in operations_df.columns:
        revenue_by_type = operations_df.groupby("type")["amount"].sum().sort_values(ascending=True)

        fig = px.bar(
            x=revenue_by_type.values,
            y=revenue_by_type.index,
            orientation="h",
            labels={"x": "Сумма (AED)", "y": "Тип услуги"},
            color_discrete_sequence=[COLORS["success"]],
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет данных об операциях")

    st.divider()

    # === P&L СВОДКА ===
    st.subheader("P&L Сводка")

    if not operations_df.empty:
        col1, col2, col3 = st.columns(3)

        total_revenue = operations_df["amount"].sum() if "amount" in operations_df.columns else 0
        total_operations = len(operations_df)
        avg_check = total_revenue / total_operations if total_operations > 0 else 0

        with col1:
            st.metric("Общая выручка", f"{total_revenue:,.0f} AED")
        with col2:
            st.metric("Операций", f"{total_operations:,}")
        with col3:
            st.metric("Средний чек", f"{avg_check:,.0f} AED")

        # Выручка по месяцам
        if "date" in operations_df.columns:
            ops_with_date = operations_df.dropna(subset=["date"])
            if not ops_with_date.empty:
                ops_with_date["month"] = ops_with_date["date"].dt.to_period("M").astype(str)
                monthly_revenue = ops_with_date.groupby("month")["amount"].sum()

                st.subheader("Выручка по месяцам")
                fig = px.line(
                    x=monthly_revenue.index,
                    y=monthly_revenue.values,
                    labels={"x": "Месяц", "y": "Выручка (AED)"},
                    markers=True,
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=300,
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет данных об операциях")


# ═══════════════════════════════════════════════════════════════════════════════
# СТРАНИЦА: АНАЛИТИКА
# ═══════════════════════════════════════════════════════════════════════════════

def page_analytics():
    """Страница аналитики."""
    st.title("Аналитика")

    seasonal_data = load_seasonal_analysis()
    ltv_data = load_ltv_analysis()
    response_times = load_response_times()

    # === СЕЗОННОСТЬ (HEATMAP) ===
    st.subheader("Сезонность активности")

    by_hour = seasonal_data.get("by_hour", {})
    by_day = seasonal_data.get("by_day_of_week", {})

    if by_hour and by_day:
        # Создание матрицы для heatmap
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_names_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        hours = list(range(24))

        # Генерация данных (упрощённо - используем by_hour)
        matrix = []
        for day in days:
            row = []
            day_data = by_day.get(day, {})
            day_msgs = day_data.get("messages", 0)
            for hour in hours:
                hour_data = by_hour.get(str(hour), {})
                hour_msgs = hour_data.get("messages", 0)
                # Примерное распределение
                value = (day_msgs / 7 + hour_msgs / 24) / 2 if day_msgs > 0 or hour_msgs > 0 else 0
                row.append(value)
            matrix.append(row)

        fig = px.imshow(
            matrix,
            x=[f"{h:02d}:00" for h in hours],
            y=day_names_ru,
            labels=dict(x="Час", y="День недели", color="Активность"),
            color_continuous_scale="Blues",
            aspect="auto",
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет данных о сезонности")
        st.info("Запустите seasonal_analysis.py для генерации данных")

    st.divider()

    # === LTV DISTRIBUTION ===
    st.subheader("Распределение LTV")

    ltv_by_contact = ltv_data.get("ltv_by_contact", [])

    if ltv_by_contact:
        ltv_values = [c.get("historical_ltv_aed", 0) for c in ltv_by_contact]

        fig = px.histogram(
            x=ltv_values,
            nbins=30,
            labels={"x": "LTV (AED)", "y": "Количество клиентов"},
            color_discrete_sequence=[COLORS["purple"]],
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Сегменты
        segments = ltv_data.get("segments", {})
        if segments:
            st.markdown("**Сегменты клиентов:**")
            cols = st.columns(len(segments))
            for col, (seg, data) in zip(cols, segments.items()):
                with col:
                    st.metric(seg, data.get("count", 0), f"LTV: {data.get('avg_ltv', 0):,.0f}")
    else:
        st.info("Нет данных LTV")
        st.info("Запустите calculate_ltv.py для генерации данных")

    st.divider()

    # === RESPONSE TIME METRICS ===
    st.subheader("Метрики времени отклика")

    overall = response_times.get("overall", {})

    if overall:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            avg = overall.get("avg_response_min", 0)
            st.metric("Среднее", f"{avg:.1f} мин")
        with col2:
            median = overall.get("median_response_min", 0)
            st.metric("Медиана", f"{median:.1f} мин")
        with col3:
            p95 = overall.get("p95_response_min", 0)
            st.metric("P95", f"{p95:.1f} мин")
        with col4:
            fast_pct = overall.get("fast_response_pct", 0)
            st.metric("Быстрых (<5мин)", f"{fast_pct:.1f}%")

        # По дням недели
        by_day = response_times.get("by_day_of_week", {})
        if by_day:
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

            days = []
            times = []
            for i, day in enumerate(day_order):
                if day in by_day:
                    days.append(day_ru[i])
                    times.append(by_day[day].get("avg_response_min", 0))

            if days:
                fig = px.bar(
                    x=days,
                    y=times,
                    labels={"x": "День недели", "y": "Среднее время ответа (мин)"},
                    color_discrete_sequence=[COLORS["info"]],
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=300,
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет данных о времени отклика")
        st.info("Запустите calculate_response_time.py для генерации данных")

    st.divider()

    # === ТРЕНДЫ ===
    st.subheader("Тренды")

    trends = seasonal_data.get("trends", {})
    monthly_summary = trends.get("monthly_summary", [])

    if monthly_summary:
        df = pd.DataFrame(monthly_summary)

        if "month" in df.columns and "messages" in df.columns:
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            fig.add_trace(
                go.Bar(x=df["month"], y=df["messages"], name="Сообщения", marker_color=COLORS["primary"]),
                secondary_y=False,
            )

            if "mom_change" in df.columns:
                fig.add_trace(
                    go.Scatter(x=df["month"], y=df["mom_change"] * 100, name="MoM %", mode="lines+markers", line=dict(color=COLORS["danger"])),
                    secondary_y=True,
                )

            fig.update_yaxes(title_text="Сообщения", secondary_y=False)
            fig.update_yaxes(title_text="MoM %", secondary_y=True)
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет данных о трендах")


# ═══════════════════════════════════════════════════════════════════════════════
# СТРАНИЦА: ЧАТЫ
# ═══════════════════════════════════════════════════════════════════════════════

def page_chats():
    """Страница просмотра чатов."""
    st.title("Чаты")

    messages_df = load_messages_sample(limit=50000)
    contacts_df = load_contacts()

    if messages_df.empty:
        st.warning("Файл сообщений не найден или пуст")
        st.info(f"Ожидаемый путь: {RAW_DIR / 'all_messages.jsonl'}")
        st.info("Запустите parse_all_chats.py для создания файла сообщений")
        return

    # === ПОИСК ===
    st.subheader("Поиск по сообщениям")

    col1, col2 = st.columns([3, 1])

    with col1:
        search_query = st.text_input("Поиск", placeholder="Введите текст для поиска...")

    with col2:
        # Выбор контакта
        contacts_list = ["Все"]
        if "chat_name" in messages_df.columns:
            unique_chats = messages_df["chat_name"].dropna().unique()[:100]  # Лимит для производительности
            contacts_list += list(unique_chats)

        selected_contact = st.selectbox("Контакт", contacts_list)

    # Фильтрация
    filtered_df = messages_df.copy()

    if search_query and "text" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["text"].str.contains(search_query, case=False, na=False)]

    if selected_contact != "Все" and "chat_name" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["chat_name"] == selected_contact]

    st.text(f"Найдено сообщений: {len(filtered_df):,}")

    st.divider()

    # === TIMELINE ЧАТА ===
    st.subheader("Переписка")

    if not filtered_df.empty:
        # Сортировка по дате
        if "datetime" in filtered_df.columns:
            filtered_df = filtered_df.sort_values("datetime", ascending=True)

        # Отображение последних 50 сообщений
        display_df = filtered_df.tail(50)

        for _, msg in display_df.iterrows():
            is_from_me = msg.get("is_from_me", False)
            text = msg.get("text", "")
            dt = msg.get("datetime", "")
            sender = msg.get("sender", "Я" if is_from_me else "Контакт")

            # Форматирование даты
            if isinstance(dt, datetime):
                dt_str = dt.strftime("%d.%m.%Y %H:%M")
            elif dt:
                dt_str = str(dt)[:16]
            else:
                dt_str = ""

            # Стиль сообщения
            if is_from_me:
                st.markdown(
                    f"""
                    <div style="background-color: #dcf8c6; padding: 8px 12px; border-radius: 8px; margin: 4px 0 4px 50px;">
                        <small style="color: #888;">{dt_str} - Я</small><br>
                        {text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="background-color: #f0f0f0; padding: 8px 12px; border-radius: 8px; margin: 4px 50px 4px 0;">
                        <small style="color: #888;">{dt_str} - {sender}</small><br>
                        {text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("Нет сообщений для отображения")

    st.divider()

    # === СТАТИСТИКА ЧАТА ===
    if selected_contact != "Все" and not filtered_df.empty:
        st.subheader("Статистика чата")

        col1, col2, col3 = st.columns(3)

        with col1:
            total_msgs = len(filtered_df)
            st.metric("Всего сообщений", total_msgs)

        with col2:
            from_me = filtered_df["is_from_me"].sum() if "is_from_me" in filtered_df.columns else 0
            st.metric("Отправлено мной", int(from_me))

        with col3:
            from_contact = total_msgs - from_me
            st.metric("Получено", int(from_contact))


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Основная функция приложения."""

    # Настройка страницы
    st.set_page_config(
        page_title="WhatsApp Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Кастомный CSS
    st.markdown(
        """
        <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
        }
        .stDataFrame {
            font-size: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Боковая панель с навигацией
    with st.sidebar:
        st.title("WhatsApp Analytics")
        st.markdown("---")

        # Навигация
        page = st.radio(
            "Навигация",
            ["Обзор", "Контакты", "Операции", "Аналитика", "Чаты"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Информация о данных
        st.markdown("### Источники данных")
        st.text(f"База: {BASE_DIR}")

        # Статус файлов
        files_status = {
            "contacts.json": (JSON_DIR / "contacts.json").exists(),
            "operations.json": (JSON_DIR / "operations.json").exists(),
            "sales_funnel.json": (JSON_DIR / "sales_funnel.json").exists(),
            "ltv_analysis.json": (JSON_DIR / "ltv_analysis.json").exists(),
            "seasonal_analysis.json": (JSON_DIR / "seasonal_analysis.json").exists(),
            "all_messages.jsonl": (RAW_DIR / "all_messages.jsonl").exists(),
        }

        for fname, exists in files_status.items():
            status = "available" if exists else "missing"
            color = "green" if exists else "red"
            st.markdown(f":{color}[{status}] {fname}")

        st.markdown("---")
        st.caption("Streamlit Dashboard v1.0")

    # Отображение выбранной страницы
    pages = {
        "Обзор": page_home,
        "Контакты": page_contacts,
        "Операции": page_operations,
        "Аналитика": page_analytics,
        "Чаты": page_chats,
    }

    page_func = pages.get(page, page_home)
    page_func()


if __name__ == "__main__":
    main()
