---
name: rdc-browser-automation-ops
description: Use when working with RDC, Dubai Courts, GDRFA, UAE charity portals, Brave profile/session access, browser-use, CUA Driver, CDP, Playwright, PDF downloads, authenticated government portals, cookies/localStorage expectations, or recovery after browser window/tab/profile confusion.
---

# RDC Browser Automation Ops

Use this skill before acting on RDC, Dubai Courts, GDRFA, charity portals, banking/government portals, or any task where the user says "мой Brave профиль", "browser-use", "CUA", "CDP", "скачай PDF", "достань документы", or similar.

## Read First

Load the shared D-disk protocol first:

```text
D:\Downloads\00_BROWSER_AUTOMATION_KNOWLEDGE_BASE\13_RDC_AND_SENSITIVE_PORTAL_PROTOCOL.md
```

For the Charity Support HQ project, also load:

```text
D:\Downloads\ЧАРИТИ БЛАГОТВОРИТЕЛЬНОСТЬ\docs\05_automation\browser_reliability_control_center\README.md
D:\Downloads\ЧАРИТИ БЛАГОТВОРИТЕЛЬНОСТЬ\docs\05_automation\browser_reliability_control_center\rdc_sensitive_portal_protocol_2026-06-09.md
```

Keep context small: read only these files unless blocked.

## Non-Negotiable Rule

Before clicking, typing, navigating, downloading, uploading, closing, or batch-running:

```text
prove pid + window_id + title + URL + visible page proof
```

Do not route by PID alone.

## Meaning of "my Brave profile"

Interpret it as the user's real visible Brave state:

```text
cookies + localStorage + session state + saved login + visible authorization
```

If the agent sees login but the owner sees authenticated page, assume wrong window/profile/tab/session until proven otherwise.

## Tool Router

- `browser-use`: simple browser state, DOM, navigation, repeatable CLI work.
- `CUA Driver`: native Windows UI, PDF viewer buttons, Save dialogs, real visible windows.
- `CDP / Chrome DevTools`: read-only tab/window/page inspection before acting.
- `Playwright`: local HTML/UI QA, screenshots, tests.
- `Browser Harness`: scoped fallback for complex self-healing browser work.
- Cookie/session helper: experimental last resort only; never automatic.

## RDC PDF Gate

Batch download is forbidden until one-file proof passes:

```text
PDF opens inside authenticated browser session
file saved locally
Magic=%PDF-
size recorded
SHA256 recorded
manifest/log updated
```

HTTP 200 HTML is not PDF.

## Experimental Script Rule

Do not silently delete risky or partial helper scripts. If risky:

1. mark experimental/quarantine;
2. document why it exists;
3. do not run automatically;
4. do not log secrets;
5. ask owner before deletion.

Current restored helper in Charity Support HQ:

```text
D:\Downloads\ЧАРИТИ БЛАГОТВОРИТЕЛЬНОСТЬ\scripts\download_rdc_portal_documents_from_brave_profile.py
```

## Stop Condition

If windows/tabs/profiles become ambiguous, stop browser actions and write a short status report. Do not keep clicking while uncertain.

## 2026-06-10 RDC Financial Claim Printout Lesson

If the goal is to prove the current RDC amount, do not confuse it with a payment voucher.

Working path proven in Charity Support HQ:

```text
authorized RDC window -> OpenCase2 -> tab المطالبة المالية -> Brave menu -> Print -> Save as PDF
```

Required verification after save:

```text
Magic=%PDF-
size recorded
SHA256 recorded
text extraction or visual preview confirms amount
manifest/evidence registry updated
```

Known result from Marsel case:

```text
EV-054 confirmed total/remaining financial claim 50,140.92 AED for case 04/03032/2026.
```

Limit: this proves amount/current financial claim only. It does not prove payment route, beneficiary details, or full court payment voucher.
