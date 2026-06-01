# PR Context — feature/complete-and-delete

> Local convenience artifact. The GitHub PR description is the canonical source of truth.

## Purpose

Extends the CLI with `complete` and `delete` commands, completing the core task lifecycle surface. The `Task` model already had a `completed` boolean field — this PR wires up the missing CLI commands to expose it.

## Affected Systems

- `task_manager/cli.py` — `cmd_complete`, `cmd_delete` handlers; updated `main()` dispatch
- `tests/test_tasks.py` — serialization tests for `completed` flag
- `README.md` — usage examples for new commands
- `.gitignore` — `__pycache__/` exclusion

## Architectural Notes

- Both commands follow the `load → mutate → save` pattern from `cmd_add`
- `complete` is idempotent: re-completing a task is a no-op with a user message
- `delete` is permanent: no soft-delete, no undo, consistent with the simple file-based storage model
- Task IDs are not reassigned after deletion — gaps are intentional, consistent with `next_id()` using `max(ids) + 1`

## Constraints

- Storage is `Path.cwd() / .task_manager_data.json` — project-scoped, set in a prior commit
- No undo mechanism — the storage layer has no history by design

## Tradeoffs

- `complete` idempotency uses a guard + message rather than silent success — more user-friendly but two success exit paths
- CLI handler logic is not unit-tested; integration testing via the CLI is the expected validation path

## Reviewer Guidance

- Verify the not-found check in `cmd_delete` (length comparison after filter)
- Verify idempotency guard messaging in `cmd_complete` is clear to end users
- `.gitignore` and README changes are housekeeping — no review focus needed
