---
name: selling-event-tickets
description: Use when researching, sourcing, pricing, verifying, packaging, advertising, or replying to requests for event tickets, concerts, sports, Formula 1, UFC, football, tennis, VIP/VVIP, hospitality, lounges, suites, boxes, paddock, groups, delivery, resale, transfer, or real-name entry risks.
---

# Selling Event Tickets

## Core principle

Sell only what is verifiable, calculate profit only after **FULL COST**, and keep the partner-facing offer separate from internal sourcing, risk and margin.

## Mandatory workflow

1. **Recover history first.** Find the same event/client/category, prior quote, local pricing rule, rejected options and status.
2. **Normalize the request.** Exact event, city, date/session, quantity, ages, together requirement, category/row, budget and whether this is a live enquiry or advertising pack.
3. **Verify current facts — always with live internet search, and as much of it as needed.** Event ticketing lives on websites: listings, prices and availability change constantly, so never quote them from memory. Search the web first, open the actual pages, reach final checkout where possible, and record which page each fact came from. Use current sources in this order: organizer → venue → official ticket operator → official hospitality → authorised partner → trusted supplier → secondary. Load the relevant [platform](references/platform-playbooks.md) and [event](references/event-playbooks/) playbook.
4. **Check the whole product ladder.** GA/standing, seated, premium, VIP/VVIP, lounge/loge, hospitality, suite/box/table, paddock/team and bundles where relevant.
5. **Verify the ticket mechanics.** Exact product, category/section/row/seats, quantity together, in-hand/allocation, PDF/mobile/app/dynamic QR/physical, delivery date, transfer, name change, lead booker, real-name/passport/face verification, refund and age rules.
6. **Reach final checkout before quoting full cost.** Capture every confirmed fee, tax, delivery charge, currency and Total/Payable. Listing ≠ secured inventory.
7. **Price from FULL COST.** `base + confirmed fees + tax + delivery/transfer + payment cost + bank/FX reserve`. Use 5% reserve for non-AED only when actual bank cost is unknown; no automatic FX reserve for AED. Working AED/USD rate is 3.65 unless Marsel gives another. Recover the latest **local pricing rule**; never import another event’s markup. Use `scripts/calculate_offer.py` when shell access exists.
8. **Produce two separate outputs.** Follow the output contract below.
9. **Reconfirm immediately before payment.** Listing, quantity, seats, total, transfer, names and delivery must still work.

## Output contract

### A. Partner TXT

Copy-ready WhatsApp text in natural business Russian:

- one asterisk for emphasis: `*text*`, never `**text**`;
- final selling price only;
- no supplier, procurement link, base cost, reserve or profit;
- verified inclusions only;
- age/child/accompanying-adult rules;
- options normally cheap → expensive;
- exact access days and product unit;
- live-availability/final-price reconfirmation.

Validate with `scripts/validate_partner_message.py` when available.

### B. Internal block for Marsel

Direct links, source status, base price, each confirmed fee and reserve, FULL COST, sale price, estimated/gross profit in USD and AED, order profit, actual percentage after rounding, old price comparison, delivery/transfer/real-name/refund risks and every unresolved item.

## Decision rules

| Situation | Required response |
|---|---|
| Sales not open | Keep timing internal; record lead and use the waiting template with a recheck date. |
| Official sold out | Secondary only after event-specific resale/transfer verification. |
| Strict real-name | Obtain final guest identity data before purchase; do not promise later transfer. |
| Group order | Check per-order limits, one block/adjacent rows, allocation/hold and payment deadline. |
| Advertising pack | Full category ladder, clean map, age, transfer and price-on-request unless a fixed price is approved. |
| Buyer chose one product | Answer that decision; do not repeat the entire catalogue. |

## Non-negotiable accuracy

- `Official Platinum` is not automatically VIP/hospitality.
- A section name is not a package; a venue suite is not event inventory.
- “2 together” does not reveal seat numbers.
- “VAT excluded” does not prove a rate.
- Never invent inclusions, category mapping, seats, secured stock or guarantees.
- Estimated profit is not “net” until every actual cost is settled.

## Read as needed

Start with [core context](references/core-context.md) and the [operator prompt (RU)](references/system-prompt-ru.md), then consult the [rule registry](references/rule-registry.md), [pricing](references/pricing-and-profit.md), [sourcing](references/research-and-sourcing.md), [verification](references/verification-and-risk.md), [communication](references/partner-communication.md), [conflicts](references/conflicts-and-evolution.md), [freshness matrix](references/source-freshness.md), [common mistakes](references/common-ai-mistakes.md) and the [event-and-platform index](references/event-and-platform-index.md) — the index is historical, reverify before quoting. Use the matching file in `templates/` rather than drafting from scratch.
