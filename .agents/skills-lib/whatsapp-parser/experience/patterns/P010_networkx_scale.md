# P010: NetworkX для графа контактов на масштабе

> Дата: 2026-02-12 | Контекст: Построение contact_graph_full.json (224K узлов, 235K рёбер)

---

## Задача

Построить граф связей для всех 3,220 контактов + их упоминания (телефоны, VCF, рефералы). Итого 224K узлов и 235K рёбер.

## Почему NetworkX

| Библиотека | Масштаб | RAM | Скорость |
|------------|---------|-----|----------|
| NetworkX | до ~1M узлов | ~2 GB для 224K | Достаточно |
| igraph | до ~10M | Меньше | Быстрее, но сложнее API |
| graph-tool | до ~100M | Минимально | Самый быстрый, но C++ |

Для 224K узлов NetworkX достаточен и имеет самый простой API.

## Betweenness centrality с sampling

Полный betweenness centrality для 224K узлов — O(VE) = часы. Решение: sampling.

```python
import networkx as nx

G = nx.Graph()
# ... добавить узлы и рёбра ...

# ПРАВИЛЬНО: sampling k=500
centrality = nx.betweenness_centrality(G, k=500, seed=42)

# НЕПРАВИЛЬНО: полный расчёт (часы на 224K)
# centrality = nx.betweenness_centrality(G)  # Не делать!
```

k=500 даёт приемлемую точность за ~30-60 сек вместо часов.

## BFS кластеризация

```python
def bfs_clusters(G):
    visited = set()
    clusters = []

    for node in G.nodes():
        if node not in visited:
            cluster = set()
            queue = [node]
            while queue:
                n = queue.pop(0)
                if n not in visited:
                    visited.add(n)
                    cluster.add(n)
                    queue.extend(set(G.neighbors(n)) - visited)
            clusters.append(cluster)

    return clusters

clusters = bfs_clusters(G)
# Субкластеризация для кластеров >100 узлов
for cluster in clusters:
    if len(cluster) > 100:
        subgraph = G.subgraph(cluster)
        # Louvain / label propagation для разбивки
```

## Сериализация

**JSON, НЕ pickle!**

```python
import json

graph_data = {
    "nodes": [{"id": n, **G.nodes[n]} for n in G.nodes()],
    "edges": [{"source": u, "target": v, **G.edges[u, v]} for u, v in G.edges()],
    "statistics": {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
    }
}

with open("contact_graph_full.json", "w", encoding="utf-8") as f:
    json.dump(graph_data, f, ensure_ascii=False)
```

Pickle проблемы:
- Не читается человеком
- Не переносим между версиями Python
- Нельзя частично загрузить
- Проблемы безопасности (arbitrary code execution)

## Метрики

| Метрика | Значение |
|---------|----------|
| Узлов | 224,336 |
| Рёбер | 235,412 |
| Размер JSON | 151 MB |
| RAM при построении | ~1.5 GB |
| Время построения | ~3-5 мин |
| Betweenness (k=500) | ~45 сек |

---

## Связанные записи

- [W006](../warnings/W006_large_json_memory.md) — не грузить contact_graph_full.json целиком
- [P008](P008_streaming_jsonl.md) — потоковое чтение JSONL
