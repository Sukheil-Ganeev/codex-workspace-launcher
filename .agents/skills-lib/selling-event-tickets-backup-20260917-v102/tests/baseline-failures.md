# Baseline failures observed before the skill

These are real failure patterns extracted from the ten source conversations. They serve as the RED phase for the skill.

| ID | Baseline failure | Required behavior after skill |
|---|---|---|
| B01 | Starts fresh research without checking an earlier quote. | Recover event/client history, prior selling price and local pricing rule first. |
| B02 | Mixes similarly named events, dates or sessions. | Normalize exact event, city, date and session before research and before output. |
| B03 | Sends procurement price to the partner. | Compute full cost, add the approved local profit rule, expose only final selling price externally. |
| B04 | Applies profit before seller/checkout fees. | Apply profit only after FULL COST. |
| B05 | Describes an internal reserve as a platform fee. | Label confirmed fee and internal reserve separately. |
| B06 | Adds a fee twice to an all-in marketplace price. | Verify checkout and count each fee once. |
| B07 | Reuses another event's 35/40/50/60% markup. | Recover the latest event/client/category rule; otherwise show scenarios. |
| B08 | Silently changes a previously quoted price. | Preserve old price when viable; otherwise show old/new and reason internally. |
| B09 | Calls Official Platinum or a named section a VIP package. | Keep exact product name and add only documented inclusions. |
| B10 | Invents food, alcohol, parking, lounge, paddock, transfer or seat details. | State only event-specific confirmed facts; mark unknowns as requiring confirmation. |
| B11 | Treats “2 tickets” as two guaranteed adjacent seats. | Confirm together guarantee separately from quantity and exact seat numbers. |
| B12 | Ignores order limits and split-order seating risk for groups. | Check limits, allocation/hold and acceptable block configurations. |
| B13 | Buys strict real-name tickets on Marsel for later transfer. | Obtain final guest identity data and issue directly to the guests when transfer/name change is prohibited. |
| B14 | Relies on buyer guarantee although flights/hotel depend on fulfilment. | Verify exact seller/allocation, in-hand status, delivery and transfer before travel commitments. |
| B15 | Exposes supplier links, procurement and profit in partner copy. | Produce a clean external TXT and a separate internal block. |
| B16 | Uses `**bold**` in WhatsApp copy. | Use one asterisk on each side: `*bold*`. |
| B17 | Omits age rules or generalizes them from another event. | Verify event-specific minimum age, child ticket and accompanying adult rules. |
| B18 | Assumes VAT from the event country. | Confirm invoicing entity, exact rate and taxable base. |
| B19 | Confuses event weekend days with package access days. | State exact product access days. |
| B20 | Claims active page/listing means secured live stock. | Reconfirm exact inventory and final price immediately before payment. |
| B21 | Calls estimated profit “net”. | Use estimated/gross until every actual cost is settled. |
| B22 | Reveals official sale timing to the partner and encourages self-purchase. | Keep procurement timing internal; record the lead and provide a recheck date. |
| B23 | Publishes volatile advertising inventory at a fixed price without approval. | Prefer price-on-request or clearly approved current prices with recheck policy. |
| B24 | Uses a secondary seller label as an official venue category. | Map seller labels to the official venue map or disclose that the label is seller-defined. |
| B25 | Gives a full catalogue after the buyer has selected one product. | Answer the current decision, not the entire inventory, unless building an advertising pack. |
