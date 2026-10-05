# Визуализация -- Полный код

Полные реализации интерактивных дашбордов (Plotly), тепловых карт и финансовых отчётов (PDF).

---

## Интерактивный дашборд (Plotly)

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json

def create_dashboard(data_path: str, output_path: str):
    """
    Создание интерактивного дашборда.

    Args:
        data_path: Путь к данным (JSON/JSONL)
        output_path: Путь для сохранения HTML
    """
    # Загрузка данных
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data['messages'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour

    # Создание дашборда
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Сообщения по дням',
            'Распределение по типам',
            'Активность по часам',
            'Приоритеты',
            'Sentiment анализ',
            'Top клиенты'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "pie"}],
            [{"type": "bar"}, {"type": "pie"}],
            [{"type": "pie"}, {"type": "bar"}]
        ]
    )

    # График 1: Сообщения по дням
    daily = df.groupby('date').size().reset_index(name='count')
    fig.add_trace(
        go.Scatter(x=daily['date'], y=daily['count'], mode='lines+markers', name='Сообщения'),
        row=1, col=1
    )

    # График 2: Типы сообщений
    types = df['type'].value_counts()
    fig.add_trace(
        go.Pie(labels=types.index, values=types.values, name='Типы'),
        row=1, col=2
    )

    # График 3: Активность по часам
    hourly = df.groupby('hour').size().reset_index(name='count')
    fig.add_trace(
        go.Bar(x=hourly['hour'], y=hourly['count'], name='По часам'),
        row=2, col=1
    )

    # График 4: Приоритеты
    priorities = df['priority'].value_counts()
    colors = {'critical': 'red', 'high': 'orange', 'medium': 'yellow', 'low': 'green'}
    fig.add_trace(
        go.Pie(
            labels=priorities.index,
            values=priorities.values,
            marker_colors=[colors.get(p, 'gray') for p in priorities.index],
            name='Приоритеты'
        ),
        row=2, col=2
    )

    # График 5: Sentiment
    sentiment = df['sentiment'].value_counts()
    sentiment_colors = {'positive': 'green', 'neutral': 'gray', 'negative': 'red'}
    fig.add_trace(
        go.Pie(
            labels=sentiment.index,
            values=sentiment.values,
            marker_colors=[sentiment_colors.get(s, 'gray') for s in sentiment.index],
            name='Sentiment'
        ),
        row=3, col=1
    )

    # График 6: Top клиенты
    top_clients = df.groupby('client_name').size().nlargest(10).reset_index(name='count')
    fig.add_trace(
        go.Bar(x=top_clients['client_name'], y=top_clients['count'], name='Top клиенты'),
        row=3, col=2
    )

    # Настройки layout
    fig.update_layout(
        title_text='AI-Агент: Дашборд классификации',
        height=1200,
        showlegend=True
    )

    # Сохранение
    fig.write_html(output_path)
    print(f"Dashboard saved to {output_path}")
```

---

## Тепловая карта активности

```python
def create_heatmap(messages_path: str, output_path: str):
    """
    Создание тепловой карты активности.
    """
    import plotly.express as px

    # Загрузка сообщений
    messages = []
    with open(messages_path, 'r', encoding='utf-8') as f:
        for line in f:
            messages.append(json.loads(line))

    df = pd.DataFrame(messages)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['weekday'] = df['datetime'].dt.day_name()
    df['hour'] = df['datetime'].dt.hour

    # Группировка
    heatmap_data = df.groupby(['weekday', 'hour']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values='count').fillna(0)

    # Порядок дней
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex(day_order)

    # Создание heatmap
    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Час", y="День недели", color="Сообщений"),
        x=list(range(24)),
        y=day_order,
        color_continuous_scale="YlOrRd",
        title="Активность по дням недели и часам"
    )

    fig.write_html(output_path)
```

---

## Финансовые отчёты (PDF)

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_financial_report(data: dict, output_path: str):
    """
    Генерация финансового отчёта в PDF.

    Args:
        data: Финансовые данные
        output_path: Путь для сохранения PDF
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Заголовок
    elements.append(Paragraph("Финансовый отчёт", styles['Title']))
    elements.append(Paragraph(f"Период: {data['period']}", styles['Normal']))

    # Таблица выручки
    revenue_data = [
        ['Услуга', 'Количество', 'Сумма (AED)', 'Доля (%)'],
    ]
    for item in data['revenue_by_service']:
        revenue_data.append([
            item['service'],
            str(item['count']),
            f"{item['amount']:,.2f}",
            f"{item['share']:.1f}%"
        ])

    revenue_table = Table(revenue_data)
    revenue_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(revenue_table)

    # Сохранение
    doc.build(elements)
```
