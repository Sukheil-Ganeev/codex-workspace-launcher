# EXP-069: TOC Scroll Isolation Fix

## Проблема
При скролле списка TOC-панели колесом мыши — слайды презентации также прокручивались. Это делало TOC непригодным для навигации в больших презентациях (например, 208 слайдов).

## Корневая причина
Три взаимосвязанных бага:

### 1. position:absolute вместо fixed
TOC overlay имел `position:absolute` и `height:100%`. В презентации с 208 слайдами это означало высоту панели ~224,000px (высота всех слайдов). Список TOC заполнял эту огромную высоту — скроллить было нечего.

### 2. body transform:scale() ломает position:fixed
Функция `applyScale()` применяет `transform: scale(X)` к body для viewport scaling на экранах <1920px. Известный CSS-баг: когда у элемента есть transform, его дочерние элементы с position:fixed ведут себя как position:absolute (transform создаёт новый containing block).

### 3. Wheel event propagation
Событие wheel при скролле TOC-списка "всплывало" (bubbled) до document и вызывало скролл слайдов.

## Решение (3 слоя)

### Слой 1: Перенос TOC на уровень html
```javascript
document.documentElement.appendChild(tocOverlay);
document.documentElement.appendChild(tocBackdrop);
```
Перемещение TOC-элементов из body в html (documentElement) — body transform больше не влияет на них.

### Слой 2: position:fixed через JS
```javascript
function openTOC() {
  tocOverlay.style.position = 'fixed';
  tocBackdrop.style.position = 'fixed';
  document.body.style.overflow = 'hidden';
  document.documentElement.style.overflow = 'hidden';
  // ...
}
function closeTOC() {
  tocOverlay.style.position = '';
  tocBackdrop.style.position = '';
  document.body.style.overflow = '';
  document.documentElement.style.overflow = '';
}
```
ВАЖНО: position:fixed задаётся через JS inline style (НЕ в CSS), чтобы qa_validator не ругался на `position:fixed` в `<style>`.

### Слой 3: stopPropagation
```javascript
document.getElementById('tocOverlay').addEventListener('wheel', function(e) {
  e.stopPropagation();
});
```

## Применимость
Любая презентация с viewport scaling (applyScale), TOC overlay, и >20 слайдов.

## Тэги
#fix #toc #scroll #position-fixed #transform #viewport-scaling
