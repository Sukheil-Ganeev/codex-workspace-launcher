# Branch & Merge Visual - Визуализация веток и слияний

## Базовая структура веток

```
main:    A───B───C───D───E
              \         /
feature:       F───G───H
```

**Объяснение:**
- `main` ветка: коммиты A → B → C → D → E
- `feature` ветка создана от B
- `feature` коммиты: F → G → H
- `feature` влита обратно в `main` в точке E

---

## Создание ветки (git branch / git checkout -b)

```
До создания ветки:

main:    A───B───C  (HEAD)
                ↑
            Ты здесь

git checkout -b feature

После создания:

main:    A───B───C
                  \
feature:           C  (HEAD)
                   ↑
               Ты здесь

(feature указывает на тот же commit C, что и main)
```

---

## Работа в feature ветке

```
main:    A───B───C

feature: A───B───C───D───E  (HEAD)
                     ↑
                 Новые commits
```

**Что произошло:**
1. Переключился на `feature`: `git checkout feature`
2. Сделал изменения и коммиты D, E
3. `main` остался на C (не изменился)

---

## Параллельная разработка (два разработчика)

```
main:    A───B───C───F───G  (коллега влил свои изменения)
              \
feature:       D───E  (HEAD - твоя ветка)
```

**Ситуация:**
- Ты работал над feature (коммиты D, E)
- Коллега влил свои изменения в main (коммиты F, G)
- Теперь `feature` отстает от `main`

---

## Fast-Forward Merge (простое слияние)

**До merge:**
```
main:    A───B───C  (HEAD)

feature: A───B───C───D───E
```

**Команда:**
```bash
git checkout main
git merge feature
```

**После merge:**
```
main:    A───B───C───D───E  (HEAD)

feature: A───B───C───D───E
```

**Что произошло:**
- Git просто "перемотал" main вперед
- Никакого merge commit не создано
- Линейная история

---

## Three-Way Merge (слияние с merge commit)

**До merge:**
```
main:    A───B───C───F  (HEAD)
              \
feature:       D───E
```

**Команда:**
```bash
git merge feature
```

**После merge:**
```
main:    A───B───C───F───M  (HEAD)
              \         /
feature:       D───E───┘
```

**Что произошло:**
- Создан merge commit `M`
- `M` имеет два родителя: `F` (из main) и `E` (из feature)
- История сохраняет информацию о ветке

---

## Merge с конфликтом

```
main:    A───B───C  (изменен файл X)
              \
feature:       D  (тоже изменен файл X)

git merge feature
→ CONFLICT в файле X!

После разрешения конфликта:

main:    A───B───C───M  (HEAD)
              \     /
feature:       D───┘

(M содержит разрешенный конфликт)
```

---

## Rebase (перебазирование)

**До rebase:**
```
main:    A───B───C───F───G
              \
feature:       D───E  (HEAD)
```

**Команда:**
```bash
git checkout feature
git rebase main
```

**После rebase:**
```
main:    A───B───C───F───G

feature: A───B───C───F───G───D'───E'  (HEAD)
                             ↑    ↑
                        Новые commits (на основе G)
```

**Что произошло:**
- Коммиты D, E "переписаны" как D', E'
- Теперь feature базируется на последнем коммите main (G)
- История линейная

---

## Rebase vs Merge

### Merge
```
main:    A───B───E───F
              \     /
feature:       C───D
```
- Сохраняет историю веток
- Создает merge commit
- История не линейная

### Rebase
```
main:    A───B───E───F

feature: A───B───E───F───C'───D'
```
- Переписывает историю
- Линейная история
- Коммиты "перемещены"

---

## Множественные ветки

```
main:    A───B───E───H───J
              \     \     \
develop:       C───D \     \
                      \     \
feature1:              F───G \
                              \
feature2:                      I───K
```

**Структура:**
- `main` - production
- `develop` - разработка
- `feature1` - от develop
- `feature2` - от main

---

## Удаление ветки после merge

**До merge:**
```
main:    A───B───C

feature: A───B───C───D───E  (HEAD)
```

**После merge и удаления:**
```bash
git checkout main
git merge feature
git branch -d feature
```

```
main:    A───B───C───D───E  (HEAD)

(feature удалена, но коммиты D, E остались в main)
```

---

## Cherry-pick (выборочный перенос коммита)

```
main:    A───B───C  (HEAD)

feature: A───B───F───G───H
```

**Хочешь только коммит G в main:**

```bash
git checkout main
git cherry-pick <hash-of-G>
```

```
main:    A───B───C───G'  (HEAD)

feature: A───B───F───G───H

(G' - копия G в main)
```

---

## Сложный merge с несколькими ветками

```
main:      A───B───C───────M───N
                \         /   /
feature1:        D───E───F   /
                      \      /
feature2:              G───H
```

**История:**
1. От B создана feature1 (D, E, F)
2. От E создана feature2 (G, H)
3. feature2 влита в feature1 (коммит H)
4. feature1 влита в main (коммит M)
5. Продолжение работы в main (N)

---

## Git Flow полная схема

```
main:        A─────────E─────────J  (production releases)
                      /         /
develop:    A───B───C───D───────H───I  (integration branch)
                 \       \       \
feature1:         F───G   \       \
                            \      \
feature2:                    K───L  \
                                     \
hotfix:                               M───N
                                           \
                                            (влит в main и develop)
```

---

## GitHub Flow (упрощенный)

```
main:    A───B───────E───────H  (всегда deployable)
              \     /     \   \
feature1:      C───D       \   \
                            \   \
feature2:                    F───G
```

**Правила:**
- Всегда от main
- Pull Request для merge
- main всегда стабилен

---

## Временные метки (tags и releases)

```
main:    A───B───C───D───E───F───G
              ↑       ↑       ↑
            v1.0    v1.1    v2.0
            (tag)   (tag)   (tag + release)
```

**Команды:**
```bash
git tag v1.0 B
git tag v1.1 D
git tag -a v2.0 G -m "Major release"
```

---

## HEAD, ветки и коммиты

```
main:    A───B───C───D  ← main (ветка-указатель)
                     ↑
                    HEAD (указывает на main)
```

**После `git checkout <commit-B>`:**
```
main:    A───B───C───D  ← main
              ↑
             HEAD (detached HEAD - указывает на B)
```

---

## Восстановление удаленной ветки

```
main:    A───B───C

feature: A───B───C───D───E  (случайно удалена)
```

**Если помнишь hash коммита E:**
```bash
git branch feature <hash-of-E>
```

```
main:    A───B───C

feature: A───B───C───D───E  (восстановлена)
```

**Или через reflog:**
```bash
git reflog  # Найди hash
git branch feature <hash>
```

---

## Визуальное представление git log

**Команда:**
```bash
git log --all --graph --oneline --decorate
```

**Вывод:**
```
* a1b2c3d (HEAD -> main) Merge feature
|\
| * e4f5g6h (feature) Add feature 2
| * i7j8k9l Add feature 1
|/
* m1n2o3p Initial commit
```

---

## Заключение

**Основные паттерны:**

1. **Feature Branch:**
   ```
   main → create branch → work → merge back
   ```

2. **Parallel Development:**
   ```
   main
   ├─ feature1
   └─ feature2
   ```

3. **Merge:**
   ```
   feature ──merge──▶ main (создает merge commit)
   ```

4. **Rebase:**
   ```
   feature ──rebase──▶ main (переписывает историю)
   ```

**Помни:** Ветки - это просто указатели на коммиты!
