# EXP-078: body transform ломает position:fixed

## Проблема
Когда у элемента есть CSS `transform` (например, `transform: scale(0.8)`), все его дочерние элементы с `position: fixed` начинают вести себя как `position: absolute`.

## Причина
Спецификация CSS: transform создаёт новый containing block для всех positioned descendants. Это значит:
- position:fixed больше не относится к viewport
- Элемент позиционируется относительно transformed ancestor

## Где встречается
Функция `applyScale()` в JS презентаций:
```javascript
function applyScale() {
  var w = window.innerWidth;
  if (w < 1920) {
    var scale = w / 1920;
    document.body.style.transform = 'scale(' + scale + ')';
    document.body.style.transformOrigin = 'top left';
  }
}
```

## Симптомы
- TOC overlay с position:fixed не фиксируется — прокручивается со слайдами
- Overlay занимает высоту всех слайдов (а не viewport)
- На мониторах >=1920px работает (scale не применяется), на <1920px ломается

## Решение
Перенести overlay элементы из body в html:
```javascript
document.documentElement.appendChild(tocOverlay);
document.documentElement.appendChild(tocBackdrop);
```
Теперь body.transform не влияет на TOC, т.к. TOC больше не child элемент body.

## ВАЖНО
- Этот баг затрагивает ВСЕ position:fixed элементы внутри body с transform
- При добавлении любого нового fixed overlay — помнить про appendChild к documentElement
- Тестировать на разных размерах окна (не только 1920px)

## Тэги
#warning #css #transform #position-fixed #viewport-scaling #critical
