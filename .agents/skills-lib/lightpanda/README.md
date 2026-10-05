# Lightpanda Skill

Управление Lightpanda — сверхлёгким headless-браузером для AI-автоматизации.

## Что это

Lightpanda — браузер на Zig, построенный с нуля для машин (не форк Chrome).
Работает через Docker-контейнер на порту 9222.

- 10x быстрее Chrome headless
- 9x меньше памяти
- Совместим с Playwright и Puppeteer через CDP

## Команды

| Команда | Описание |
|---------|----------|
| `/lightpanda start` | Запустить контейнер |
| `/lightpanda stop` | Остановить |
| `/lightpanda status` | Проверить статус |
| `/lightpanda test` | Тест подключения |
| `/lightpanda restart` | Перезапустить |

## Ограничения

- Скриншоты и PDF не поддерживаются (для этого Chrome)
- Бета (~95% совместимость с сайтами)
- Требует Docker Desktop

## Ссылки

- GitHub: https://github.com/lightpanda-io/browser
- Docs: https://lightpanda.io/docs
- Docker Hub: https://hub.docker.com/r/lightpanda/browser
