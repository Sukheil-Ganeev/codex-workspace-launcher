# Quality gates

Перед выдачей проверить:

1. Получатель определён: internal/agent/client.
2. Мессенджер определён или формат не зависит от него.
3. Section + Row + Seat не потеряны.
4. Category доказана, не угадана по цене/section.
5. Official Platinum не выдан как Category.
6. Цена относится к нужному слою: procurement / agent base / client final.
7. Для agent/client нет закупки, source URL/ID, investor/owner profit.
8. Aisle +100 применён только при provider surcharge 100.
9. Pending owner ladder не заменена примерными числами.
10. Sold используется только для explicit sold.
11. Есть timestamp/freshness и recheck before payment.
12. Hospitality label official vs commercial quote точен.
13. WhatsApp separator и жирный синтаксис корректны.
14. Текст не обещает reserve/checkout/гарантированное наличие.
15. Реальная отправка не выполнена без отдельного разрешения.
16. Русский язык используется по умолчанию.
17. В agent/client тексте нет сырых кодов `SECC4A`, source IDs или physical keys.

Для проверки готового `.txt` можно использовать `scripts/validate_message.py`.
