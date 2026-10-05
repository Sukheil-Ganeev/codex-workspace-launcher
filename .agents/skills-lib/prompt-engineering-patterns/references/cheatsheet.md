# Cheatsheet — prompt-engineering-patterns

## Техники промптинга
| Техника | Когда использовать | Пример |
|---------|-------------------|--------|
| Zero-shot | Простые задачи | "Classify this text as positive/negative" |
| Few-shot | Нужен формат/паттерн | 3-5 примеров input->output |
| Zero-shot CoT | Рассуждение без примеров | "Let's think step by step" |
| Few-shot CoT | Сложное рассуждение | Примеры с цепочкой мыслей |
| Self-consistency | Повышение точности | N ответов -> мажоритарный |
| Tree-of-Thought | Сложный выбор | Несколько веток рассуждений |
| ReAct | Агентные задачи | Thought -> Action -> Observation |
| Reflexion | Самокоррекция | Generate -> Evaluate -> Refine |

## Структура промпта (шаблон)
```
<system>
You are {role}. {persona description}.

## Rules
- {rule 1}
- {rule 2}
- NEVER {constraint}

## Output Format
{exact format specification}
</system>

<user>
## Context
{background information, documents, data}

## Task
{specific instruction}

## Examples
Input: {example 1 input}
Output: {example 1 output}

Input: {example 2 input}
Output: {example 2 output}
</user>
```

## XML-теги для структурирования
```xml
<context>Фоновая информация, документы</context>
<instructions>Что нужно сделать</instructions>
<rules>Ограничения и правила</rules>
<examples>Примеры input/output</examples>
<format>Формат ответа</format>
<output>Сюда модель пишет ответ</output>
```

## Температура
| Temperature | Использование | Пример задач |
|-------------|--------------|--------------|
| 0 | Детерминизм, факты | Извлечение данных, классификация, код |
| 0.1-0.3 | Низкая вариативность | Суммаризация, перевод, Q&A |
| 0.5-0.7 | Баланс | Написание текстов, чат-боты |
| 0.8-1.0 | Креативность | Брейншторм, поэзия, идеи |
| >1.0 | Максимум разнообразия | Экспериментальная генерация |

## Ключевые фразы-модификаторы
| Фраза | Эффект |
|-------|--------|
| "Think step by step" | Активирует CoT рассуждение |
| "Be concise" | Короткие ответы |
| "ONLY use information from the context" | Снижает галлюцинации |
| "If unsure, say 'I don't know'" | Честность при неуверенности |
| "Format as JSON/markdown/table" | Контроль формата |
| "Do NOT include..." | Исключение лишнего |
| "Before answering, verify..." | Самопроверка |
| "Consider edge cases" | Покрытие крайних случаев |
| "Explain your reasoning" | Прозрачность решений |
| "Act as a {role}" | Установка экспертизы |

## Few-shot: правила подбора примеров
| Правило | Описание |
|---------|----------|
| Разнообразие | Примеры покрывают разные кейсы |
| Последовательность | Одинаковый формат во всех примерах |
| Релевантность | Похожи на реальные входные данные |
| Edge cases | Включить 1-2 граничных случая |
| Порядок | От простых к сложным |
| Количество | 3-5 оптимально |

## Паттерн: Structured Output
```
# Anthropic (tool_use)
tools=[{
  "name": "extract_info",
  "description": "Extract structured information",
  "input_schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "age": {"type": "integer"},
      "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["name"]
  }
}]

# OpenAI (response_format)
response_format={"type": "json_schema", "json_schema": {...}}
```

## Паттерн: ReAct (Agent)
```
You have access to the following tools:
- search(query): Search the web
- calculate(expression): Calculate math

Format:
Thought: I need to find...
Action: search("query")
Observation: [result]
Thought: Now I know...
Action: calculate("2+2")
Observation: 4
Answer: The final answer is...
```

## Паттерн: Self-Evaluation
```
First, generate your answer.
Then, evaluate it against these criteria:
1. Accuracy: Is every fact verifiable?
2. Completeness: Does it address all parts of the question?
3. Clarity: Is it easy to understand?
Rate each 1-5. If any score < 3, revise your answer.
```

## Антипаттерны (НЕ делать)
| Антипаттерн | Почему плохо | Как правильно |
|-------------|-------------|---------------|
| "Do everything perfectly" | Слишком размыто | Конкретные критерии |
| Противоречивые инструкции | Модель выберет случайно | Одна чёткая инструкция |
| Огромный промпт без структуры | Lost in the middle | XML-теги, секции |
| Только negative rules | Модель не знает что делать | Positive + negative |
| Неявный формат | Каждый раз разный вывод | Явный шаблон + примеры |
| temperature=1 для фактов | Галлюцинации | temperature=0 |
