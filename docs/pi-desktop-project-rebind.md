# PI-Desktop: фикс «переключение проекта не перепривязывает workspace»

Дата: 2026-09-10
Приложение: PI-Desktop v0.14.6 (стороннее, `vastsa/PI-Desktop`)

## Проблема

PI-Desktop держит два независимых «текущих проекта», которые могут разойтись:

1. **Глобальный workspace** — `workspace.get` / `workspace.set` (host), kv-ключ
   `app.currentProjectId`. Показывает файловый листинг.
2. **Проект сессии** — `sessions.project_id` → `projects.path`. Источник
   Project instructions (AGENTS.md) и песочницы инструментов.

При переключении проекта в UI обновлялось только второе: инструкции приходили
от нового проекта, а файлы оставались от старого.

## Фикс

Одна правка в `apps/desktop/electron/main/index.ts` (функция
`resolveAgentRuntimeLaunch`): при каждом запуске агента глобальный workspace
выравнивается на `session.projectPath`. Live-rebind, без новой сессии.

```ts
if (projectPath) {
  const current = await host.call("workspace.get");
  if (current.workspace?.path !== projectPath) {
    await host.call("workspace.set", { path: projectPath });
    setCurrentWorkspacePath(projectPath);
  }
}
```

Фикс встроен в собранный `app.asar`:
`A:\Programs\PI-Desktop\app\resources\app.asar`.

## Переживание обновлений

Автообновление PI-Desktop (GitHub, `vastsa/PI-Desktop`) заменяет `app.asar` и
стирает фикс. После обновления:

1. Запустить `A:\Programs\PI-Desktop\fix-project-rebind\ПОЧИНИТЬ-ПРОЕКТ.cmd`
   (скрипт `reapply-fix.mjs` распакует → вставит строку → упакует → заменит).
2. Перезапустить PI-Desktop.

## Перенос на другую машину (например, брату)

`A:\Programs\PI-Desktop\НАСТРОЙКА-ДЛЯ-БРАТА.cmd` (+ `настройка-для-брата.py`):
сам находит/спрашивает путь к muse.exe, прописывает Python, создаёт автозапуск
моста и провайдера «Meta Muse».

## Заметки

- Это локальный патч стороннего приложения (не апстрим, не PR).
- Полный контекст и границы: `A:\Programs\PI-Desktop\AGENTS.md`,
  `A:\Programs\PI-Desktop\FIX-project-rebind-2026-09-10.md`.
- Безопасность: фикс не меняет логику мостов (`meta-bridge.py` / `codex-bridge.py`).
