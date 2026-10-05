---
name: x-viral-business-strategist
description: Русский бизнес-оркестратор для X/Twitter контента. Use when the user asks to score an X/Twitter post, predict viral potential, improve a draft before publishing, compare hooks, rewrite a tweet/thread, plan replies, reduce negative-signal risk, or optimize content for business outcomes such as leads, authority, profile clicks, trust, and sales. Combines local x-phoenix-score, x-algo-* references, x-write, x-mastery, and x-algorithm while clearly separating evidence-backed mechanics from marketing heuristics.
---

# X Viral Business Strategist

## Назначение

Оценивай и улучшай посты для X/Twitter так, чтобы одновременно росли:

- шанс получить охват;
- шанс получить полезные replies/reposts/bookmarks/profile clicks;
- бизнес-польза: лиды, доверие, экспертность, переходы в профиль, продажи;
- безопасность: меньше спама, кликбейта, неподтвержденных обещаний и негативных сигналов.

Всегда говори прямо: это не точный прогноз продакшен-алгоритма X, а практичная оценка по открытым источникам, локальным эвристикам и видимому тексту.

## Когда включаться

Используй навык для запросов вроде:

- "оценить пост", "залетит?", "будет вирусным?", "перед публикацией";
- "перепиши для X", "сделай тред", "сделай hook";
- "почему пост слабый", "что убивает охват";
- "сравни 3 варианта поста";
- "сделай пост под бизнес/лиды/экспертность/личный бренд".

## Источники внутри пакета

Проверяй по ситуации:

- `../x-phoenix-score/` - быстрый локальный scorer и JSON-разбор черновика.
- `../x-algo-scoring/` - weighted scoring и роль predicted actions.
- `../x-algo-engagement/` - список engagement/action signals.
- `../x-algo-filters/` - причины фильтрации/понижения.
- `../x-algo-pipeline/` - где scoring стоит в For You pipeline.
- `../x-algo-ml/` - Phoenix/Grok model context.
- `../x-write/` - генерация X posts/replies/thread patterns.
- `../x-algorithm/` и `../x-mastery/` - growth playbook. Используй как эвристику, не как доказанный закон.
- `references/source-map.md` - откуда взяты исходные skills и насколько им можно доверять.

## Рабочий процесс

1. Определи тип входа:
   - черновик одного поста;
   - thread;
   - reply/quote;
   - URL/screenshot;
   - идея без готового текста.
2. Если есть готовый текст, запусти baseline:

```bash
python ~/.codex/skills/x-phoenix-score/scripts/score_x_post.py --text "POST_TEXT" --json
```

Если путь недоступен, используй `scripts/x_business_score.py` из этого skill.

3. Отдельно оцени бизнес:
   - есть ли понятный адресат;
   - есть ли конкретная боль/выгода;
   - есть ли proof/result/artifact;
   - есть ли мягкий CTA;
   - не выглядит ли пост как спам, инфобизнес или пустая мотивация.
4. Отделяй факты от эвристик:
   - "открытая механика" - pipeline, predicted actions, weighted scoring, filters;
   - "практическая эвристика" - timing, early replies, media multipliers, Premium boost;
   - "неизвестно" - личный graph пользователя, текущие тренды, реальные model weights, account-specific distribution.
5. Дай улучшения, сохранив смысл и голос пользователя.

## Формат ответа

Пиши по-русски, коротко и прикладно:

1. `Вердикт`: 1-2 предложения.
2. `Оценки`:
   - viral score 0-100;
   - business score 0-100;
   - risk score низкий/средний/высокий;
   - confidence низкая/средняя/высокая.
3. `Что помогает`: 3-5 пунктов.
4. `Что убивает`: 3-5 пунктов.
5. `Как переписать`: 2-4 варианта:
   - безопасный бизнес-вариант;
   - higher-reply вариант;
   - higher-bookmark/repost вариант;
   - при необходимости founder/personal voice вариант.
6. `План публикации`: что сделать до поста, первые 30 минут, первые 2 часа.
7. `Важно`: короткая caveat про то, что оценка не гарантирует охват.

## Правила качества

- Не обещай "точно завирусится".
- Не предлагай автоответы, масс-лайки, накрутки, спам, pods как основной путь.
- Не советуй спорность ради спорности, если это может вредить бренду.
- Для бизнес-контента предпочитай конкретность: цифры, кейс, чеклист, артефакт, скрин, короткое доказательство.
- Если пост продающий, не делай его слишком рекламным. Сначала value/proof, потом мягкий CTA.
- Если тема чувствительная, снижай риск блоков/мьютов/репортов.

## Быстрый scoring helper

Для независимой бизнес-проверки можно запускать:

```bash
python ~/.codex/skills/x-viral-business-strategist/scripts/x_business_score.py --text "POST_TEXT" --json
```

Он не заменяет суждение, но дает повторяемую baseline-оценку.
