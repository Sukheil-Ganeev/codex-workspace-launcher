# doc-ops — Experience Log

> Объединённый опыт из delivery-docs + docs-optimizer.
> Новые уроки добавлять в конец файла.

## Уроки

### Из docs-optimizer

1. **Emoji grep на Windows (MINGW64) не работает** — использовать текстовые метки вместо emoji символов при поиске в файлах.

2. **Research-папки создают ложные orphan-сигналы** — исключать docs/research/competitors/, docs/archive/ из проверки AP-03.

3. **Файлы .claude/rules/ могут быть не в git** — проверять через `git status` при аудите.

4. **MEMORY.md физический размер ≠ тому что видит Claude** — Claude Code инжектит расширенный контент в system-reminder. Замерять токены по фактическому файлу.

5. **Главный выигрыш: .claude/rules/** — при выносе протоколов/шаблонов из CLAUDE.md в .claude/rules/ файл сразу теряет ~60% размера. Один сеанс поднял проект с 2/5 до 4/5.

### Из delivery-docs

(Пока нет записей — скилл был новым)

---

*Sessions: docs-optimizer 2 sessions, delivery-docs 0 sessions*
*Last updated: 2026-03-17*
