# Worker Output Contract

Each worker must write a compact machine-readable outcome.

## Required Fields

- `chat_id`
- `assigned_domain_count`
- `completed_domain_count`
- `status_counts`
- `domains`
- `created_files`
- `blocked_actions`
- `needs_owner_decision`
- `validator_command`
- `validation_status`

## Per-Domain Fields

- `domain`
- `final_status`
- `source_used`
- `evidence_file`
- `event_rows`
- `missing_fields`
- `next_action`
- `risk_gate`

## Allowed Final Statuses

- `adapter_works`
- `adapter_preview_ready_from_saved_source`
- `spec_ready`
- `yellow_window_needed`
- `no_public_vector`
- `out_of_scope`
- `error_with_evidence`

## Rejection Rules

Reject a worker result if:

- any assigned domain has no final status;
- a domain is duplicated across workers;
- a worker edited shared core code without a proposal file;
- a worker ran live/browser/raw/API/Firecrawl without a yellow-window proof;
- a worker wrote to `master`, confirmed layers, or git.
- a worker launched a shared handoff/project hook or changed files outside its exact outcome namespace, even when its domain findings were useful.
