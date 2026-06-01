# CLAUDE.md — Task Manager

## Repository Overview

A minimal Python CLI task manager. Single-user, local-only, file-backed.
No server, no async, no external dependencies beyond `pytest`.
Designed as a lightweight reference implementation for AI-assisted engineering workflows.

---

## Architecture

Three-layer structure with no abstraction beyond what the domain requires:

```
task_manager/
  models.py    — Task dataclass (data shape + serialization)
  storage.py   — JSON file I/O (load, save, next_id)
  cli.py       — argparse subcommands (add, list, complete, delete)
tests/
  test_tasks.py — pytest unit tests (model layer only)
```

**Data flow for all write operations:**
```
load_tasks() → mutate in memory → save_tasks()
```

This pattern is used consistently across `cmd_add`, `cmd_complete`, and `cmd_delete`.
Do not introduce caching, lazy loading, or deferred saves — the load/mutate/save cycle is intentional.

---

## Important Modules

### `task_manager/models.py`

- `Task` is a `@dataclass` with fields: `id: int`, `title: str`, `created_at: str`, `completed: bool`
- `created_at` is an ISO 8601 string set at construction time via `datetime.now().isoformat()`
- Serialization: `to_dict()` / `from_dict()` — both must stay in sync with storage schema
- `completed` defaults to `False`

### `task_manager/storage.py`

- Storage file: `Path.cwd() / ".task_manager_data.json"` — **CWD-scoped**, not home-dir-scoped
- Running the CLI from different directories creates independent task lists — this is intentional
- `next_id()` returns `max(existing ids) + 1` — IDs are never reassigned, gaps after deletion are expected
- No migration mechanism — storage schema changes require manual data handling

### `task_manager/cli.py`

- Entry point: `main()` via argparse subcommands
- Handler naming convention: `cmd_<subcommand>` (e.g. `cmd_add`, `cmd_complete`)
- Not-found errors exit with `sys.exit(1)` — consistent across all handlers
- `complete` is idempotent: re-completing a task prints a message and returns without error
- `delete` is permanent — no soft-delete, no undo, no archive

---

## Key Workflows

### Adding a task
```bash
python3 -m task_manager.cli add "Task title"
```
Loads tasks, assigns `next_id`, appends, saves.

### Listing tasks
```bash
python3 -m task_manager.cli list
```
Loads and prints all tasks with `[ ]` / `[x]` status prefix.

### Completing a task
```bash
python3 -m task_manager.cli complete <id>
```
Finds by ID, guards against re-completion, sets `completed=True`, saves.

### Deleting a task
```bash
python3 -m task_manager.cli delete <id>
```
Filters out by ID, detects not-found via length comparison, saves remainder.

---

## Coding Conventions

- Python 3 only — no compatibility shims
- Standard library only: `argparse`, `json`, `pathlib`, `dataclasses`, `datetime`
- No third-party runtime dependencies — `requirements.txt` contains only `pytest`
- Type hints used in function signatures (`List[Task]`, `-> None`, etc.)
- `sys.exit(1)` for error exits — do not raise exceptions in CLI handlers
- Print-based user feedback — no logging framework
- No comments unless the WHY is non-obvious

---

## Operational Constraints

- **CWD-scoped storage**: the data file lives in the working directory. Scripts or tests that change CWD will operate on different data files. Be explicit about CWD when testing or scripting.
- **No schema migrations**: adding fields to `Task` requires updating `from_dict` carefully. Missing keys will raise `KeyError` on existing data files.
- **No locking**: concurrent writes to `.task_manager_data.json` are not safe — the tool is single-user and single-process by design.
- **Data file is gitignored**: `.task_manager_data.json` is excluded from version control.

---

## Testing Expectations

- Framework: `pytest` only — no mocking libraries, no fixtures currently
- Test scope: **model layer only** (`models.py`, `next_id` from `storage.py`)
- CLI handler logic (`cmd_add`, `cmd_complete`, `cmd_delete`) is **not unit tested** — validated manually via CLI
- Tests are in `tests/test_tasks.py`
- Run with: `pytest`
- New tests should cover model serialization, edge cases in `next_id`, and any new model fields
- Do not mock the storage layer in tests — if storage logic needs testing, test it directly

---

## Reviewer Guidance

- The `load → mutate → save` pattern must be preserved in all write handlers
- `next_id` gap behaviour (IDs not reassigned after delete) is intentional — do not change without discussion
- `complete` idempotency is by design — re-completing should never error
- Storage path (`Path.cwd()`) is intentional and must not be changed to `Path.home()` — this was an explicit prior decision
- CLI handler tests are out of scope for unit tests — do not request them in review unless adding integration test infrastructure
- No new runtime dependencies without discussion

---

## Known Tradeoffs

| Tradeoff | Decision |
|---|---|
| CWD-scoped storage | Keeps data project-local; breaks if invoked from unexpected directories |
| No ID reassignment | Simpler `next_id` logic; leaves gaps in ID sequences after deletion |
| No soft-delete | Simpler storage; no undo for deleted tasks |
| No CLI unit tests | Reduces test overhead; relies on manual CLI validation |
| `completed` as flat boolean | Simple; no support for timestamps, history, or state machine |

---

## Things To Avoid

- Do not introduce a database or ORM — the JSON file store is intentional
- Do not add a web server or API layer — this is a CLI tool
- Do not reassign task IDs after deletion
- Do not change storage path from CWD to home directory
- Do not add runtime dependencies without explicit agreement
- Do not add error handling for internal invariants — trust the data model
- Do not add undo/redo or soft-delete unless explicitly scoped
