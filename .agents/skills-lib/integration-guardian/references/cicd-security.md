# CI/CD Security Gates — GitHub Actions Reference

Security gates для GitHub Actions pipeline в VIP-DXB-CatalogBot. Каждый gate блокирует деплой при обнаружении проблемы.

---

## Архитектура security pipeline

```
push/PR
   ↓
[lint]  →  [test + PostgreSQL]  →  [security-scan]  →  [build]  →  [deploy]
                                         ↑
                              Блокирует при: critical CVE,
                              hardcoded secrets, SAST critical
```

Правило: `security-scan` должен завершиться успешно ДО `build` и `deploy`.

---

## 1. Dependency Review Action

Автоматически проверяет новые зависимости в PR на CVE:

```yaml
# .github/workflows/security.yml
name: Security Gates

on:
  pull_request:
    paths:
      - 'requirements*.txt'
      - 'pyproject.toml'

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: high        # Блокировать при high и critical
          allow-licenses: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Python-2.0
          deny-licenses: GPL-3.0, LGPL-3.0  # Запретить copyleft лицензии
```

---

## 2. pip-audit — Python CVE Scanner

Основной инструмент для Python проектов:

```yaml
  security-scan:
    runs-on: ubuntu-latest
    needs: [lint, test]  # Запускать только после успешных lint и test
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install pip-audit
        run: pip install pip-audit

      - name: Run pip-audit
        run: |
          pip-audit -r requirements.txt --format=json -o audit-results.json || true
          pip-audit -r requirements.txt --format=cyclonedx-json -o sbom.json || true
          # Провалить pipeline только при critical/high:
          pip-audit -r requirements.txt --vulnerability-service=osv \
            --desc=on 2>&1 | tee audit-output.txt
          if grep -q "CRITICAL\|HIGH" audit-output.txt; then
            echo "Critical or High CVE found — blocking deploy"
            exit 1
          fi

      - name: Upload audit results
        uses: actions/upload-artifact@v4
        if: always()  # Загружать даже при failure
        with:
          name: security-audit-results
          path: |
            audit-results.json
            sbom.json
            audit-output.txt
```

---

## 3. Bandit — Python SAST (Static Analysis)

Bandit анализирует Python код на паттерны уязвимостей:

```yaml
      - name: Run Bandit SAST
        run: |
          pip install bandit[toml]
          # Сканируем все платформенные боты и core
          bandit -r \
            bot/ vk_bot/ instagram_bot/ whatsapp_bot/ \
            facebook_bot/ viber_bot/ core/ data/ miniapp/ \
            -f json -o bandit-results.json \
            --skip B101,B601 \
            -ll  # Только medium и выше
          # -ll = минимальный уровень LOW severity для вывода
          # B101 = assert statements (OK в тестах)
          # B601 = paramiko (не используем)

      - name: Check Bandit results
        run: |
          ISSUES=$(python -c "
          import json
          with open('bandit-results.json') as f:
              data = json.load(f)
          high = [r for r in data.get('results', [])
                  if r['issue_severity'] in ('HIGH', 'CRITICAL')]
          print(len(high))
          ")
          echo "High/Critical issues: $ISSUES"
          if [ "$ISSUES" -gt "0" ]; then
            echo "Bandit found high-severity issues — blocking deploy"
            cat bandit-results.json | python -m json.tool
            exit 1
          fi

      - name: Upload Bandit results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: bandit-results
          path: bandit-results.json
```

---

## 4. Trivy — Container и Filesystem Scanner

Сканирует Docker образы и файловую систему:

```yaml
  trivy-scan:
    runs-on: ubuntu-latest
    needs: [build]  # Запускать после сборки образа
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy filesystem scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'  # Провалить при critical/high

      - name: Upload Trivy results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

      # Для Docker образа:
      - name: Run Trivy image scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'catalog-bot:${{ github.sha }}'
          format: 'table'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
```

---

## 5. Secret Scanning (Gitleaks)

Находит hardcoded secrets в коде и git history:

```yaml
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Полная history для проверки всех коммитов

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          config-path: .gitleaks.toml  # Опционально
```

**Конфиг `.gitleaks.toml` для VIP-DXB-CatalogBot:**
```toml
[extend]
useDefault = true

[[rules]]
id = "vip-dxb-telegram-token"
description = "Telegram Bot Token"
regex = '''[0-9]{8,10}:[A-Za-z0-9_-]{35}'''
severity = "CRITICAL"

[[rules]]
id = "vip-dxb-meta-secret"
description = "Meta App Secret (hardcoded)"
regex = '''META_APP_SECRET\s*=\s*["'][^"']{20,}["']'''
severity = "CRITICAL"

[allowlist]
description = "Allowlist for test fixtures"
paths = [
  "tests/",
  "*.example",
  "*.sample",
]
regexes = [
  '''EXAMPLE_TOKEN''',
  '''test_secret_key''',
]
```

---

## 6. CodeQL Analysis

Глубокий статический анализ от GitHub:

```yaml
  codeql:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: python
          queries: security-and-quality

      - name: Autobuild
        uses: github/codeql-action/autobuild@v3

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: "/language:python"
```

---

## 7. Environment Protection Rules

В GitHub repo settings → Environments:

**Production environment (main branch):**
- Required reviewers: 1 (при ручном деплое)
- Wait timer: 0 мин (авто-деплой при push в main)
- Allowed branches: `main` only
- Environment secrets: `SERVER_HOST`, `SERVER_USER`, `SSH_PRIVATE_KEY`

**Staging environment (develop branch):**
- Allowed branches: `develop`, `feature/*`
- Environment secrets: `STAGING_HOST`, `STAGING_USER`, `STAGING_KEY`

```yaml
  deploy:
    needs: [security-scan, trivy-scan]  # Оба должны пройти
    environment: production             # Использует защищённые secrets
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to GCP
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/catalog-bot
            git pull origin main
            docker compose --env-file .env.prod \
              -f deploy/docker-compose.prod.yml \
              up -d --build
```

---

## 8. Secrets Rotation Strategy

Когда ротировать secrets:

| Событие | Действие | Срочность |
|---------|----------|-----------|
| Сотрудник уволен | Ротировать все shared secrets | Немедленно |
| Secret попал в git | Ротировать + удалить из history | Немедленно |
| Quarterly | Ротировать все production secrets | Плановая |
| CVE в webhook library | Проверить не скомпрометированы ли secrets | В течение 24ч |

**Процедура при утечке secret в VIP-DXB-CatalogBot:**
```
1. META_APP_SECRET → Meta Developer Portal → App Settings → Reset Secret
2. CATALOG_BOT_TOKEN → @BotFather → /revoke → generate new token
3. VK_BOT_TOKEN → vk.com/dev → Group → Manage → API → Reset Token
4. DATABASE_URL password → ALTER USER catalog_user PASSWORD 'new_password'
5. Обновить .env.prod на GCP VM: tourist-bot
6. Обновить GitHub Actions secrets (repo settings)
7. Перезапустить docker-compose на VM
8. Удалить secret из git history: git filter-branch или BFG Repo Cleaner
```

---

## Итоговая матрица coverage

| Угроза | Инструмент | Gate |
|--------|-----------|------|
| CVE в зависимостях | pip-audit | security-scan |
| Новые CVE в PR | dependency-review-action | PR check |
| Hardcoded secrets | gitleaks | secret-scan |
| SAST (SQL injection, etc.) | bandit | security-scan |
| Container уязвимости | trivy | trivy-scan |
| Глубокий анализ кода | CodeQL | codeql |
| Неправильные env secrets | Environment protection | deploy gate |
