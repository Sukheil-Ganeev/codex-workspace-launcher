# Pricing & Profit Engine

## 1. Full-cost rule

`FULL COST = BASE + CONFIRMED FEES + TAX + DELIVERY/TRANSFER + PAYMENT COST + BANK/FX RESERVE`

Profit is applied only after FULL COST.

## 2. Confirmed fee vs reserve

- **Confirmed fee:** visible at checkout or stated by the seller for this exact product.
- **Reserve:** internal protection for an unconfirmed cost.
- Never tell a partner that a reserve is a marketplace fee.
- Never add a fee twice when the displayed price is already all-in.

## 3. Currency

- Partner selling price: normally USD.
- Working AED rate: 1 USD = 3.65 AED unless instructed otherwise.
- Non-AED purchase: add 5% bank/FX reserve unless actual card cost is known.
- AED purchase: no automatic 5% FX reserve.

## 4. Profit selection

There is no universal markup. First recover the last event/client/category-specific instruction. Historical examples include percentage margins, fixed dollar profit, separate partner margin and different margins for cheap/premium tickets. They are examples, not global defaults.

If no rule exists, show:

1. full cost;
2. current official/secondary market range;
3. conservative price;
4. recommended price;
5. premium price;
6. profit and actual percentage for each.

## 5. Calculation table

| Option | Base | Seller fee | Order fee | Tax | Delivery | FX reserve | Full cost | Sale | Profit USD | Profit AED | Order profit | Actual % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|

## 6. Rounding

Round after the exact calculation, normally upward to a convenient USD amount. Recalculate actual profit after rounding; do not assume the target percentage still holds.

## 7. Price continuity

If the old partner price still covers full cost and target profit, keep it. If it does not, show old/new internally and explain the change. Never silently change a previously quoted price.

## 8. Unit discipline

- Ticket: price per ticket.
- Exact request: total may be added for requested quantity.
- Box/suite/sofa/table: price for the entire object when sold as a unit.
- Group discount: do not apply to a smaller quantity.
- Per-order fee: allocate across the actual number purchased, then recalculate if quantity changes.
