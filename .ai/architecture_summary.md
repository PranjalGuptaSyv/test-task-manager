# Architecture Summary — Task Manager

## Purpose

A single-user CLI task manager. Intentionally minimal — no server, no async, no external runtime dependencies.
Serves as a reference implementation for AI-assisted engineering workflow tooling.

---

## Module Dependency Graph

```
cli.py
  ├── models.py   (Task dataclass)
  └── storage.py  (load_tasks, save_tasks, next_id)
        └── models.py

tests/test_tasks.py
  ├── models.py
  └── storage.py (next_id only)
```

No circular dependencies. `models.py` has no internal imports.

---

## Data Model

```python
@dataclass
class Task:
    id: int                  # auto-assigned, never reused
    title: str               # user-provided, no validation
    created_at: str          # ISO 8601, set at construction
    completed: bool = False  # toggled by `complete`, never un-toggled
```

Storage format: JSON array of `Task.to_dict()` objects.

```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "created_at": "2026-06-01T15:00:37.192441",
    "completed": true
  }
]
```

---

## Storage Layer

- **File**: `Path.cwd() / ".task_manager_data.json"`
- **Format**: JSON array, pretty-printed with `indent=2`
- **Concurrency**: none — single process, single user
- **Schema evolution**: no migration support; `from_dict` will raise `KeyError` on missing fields
- **ID generation**: `max(ids, default=0) + 1` — monotonically increasing, gaps left after deletion

---

## CLI Layer

Entry via `python3 -m task_manager.cli <subcommand>`.

| Subcommand | Handler | Behaviour |
|---|---|---|
| `add <title>` | `cmd_add` | load → append new Task → save |
| `list` | `cmd_list` | load → print with `[ ]`/`[x]` prefix |
| `complete <id>` | `cmd_complete` | load → find → idempotency check → set completed → save |
| `delete <id>` | `cmd_delete` | load → filter → not-found check → save |

Error exits: `sys.exit(1)` for not-found. No exceptions propagated to user.

---

## Test Coverage

| Area | Covered | Method |
|---|---|---|
| `Task` serialization round-trip | Yes | `test_task_roundtrip` |
| `Task` default `completed=False` | Yes | `test_task_defaults_not_completed` |
| `next_id` empty list | Yes | `test_next_id_empty` |
| `next_id` with gaps | Yes | `test_next_id_existing` |
| `completed` flag serialization | Yes | `test_task_complete_flag` |
| `completed` flag deserialization | Yes | `test_task_from_dict_completed` |
| CLI handler dispatch | No | Manual only |
| Storage file I/O | No | Manual only |

---

## Key Invariants

1. `id` values are never reused after deletion — gaps are acceptable and expected
2. `completed` can be set `True` but never reset to `False` — no un-complete command
3. All writes follow `load → mutate → save` — no partial writes, no deferred saves
4. Storage path is CWD-relative — not user-home-relative
5. `created_at` is set once at Task construction and never mutated

---

## Extension Points

If the project grows, the most natural extension points are:

- **New subcommands**: add a `cmd_<name>` function, register with argparse in `main()`
- **New Task fields**: add to dataclass + update `to_dict`/`from_dict` + handle missing keys in old data
- **Storage backends**: `load_tasks`/`save_tasks` could be abstracted behind an interface, but only if multiple backends are genuinely needed
- **Due dates / priorities**: natural next fields on `Task` — store as ISO strings or integers respectively

Avoid adding abstraction ahead of actual need.
