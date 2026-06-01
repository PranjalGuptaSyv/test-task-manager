# Task Manager

A simple CLI task manager.

## Usage

```bash
python3 -m task_manager.cli add "Buy groceries"
python3 -m task_manager.cli list
python3 -m task_manager.cli complete <id>
python3 -m task_manager.cli delete <id>
```

## Development

```bash
pip install -r requirements.txt
pytest
```
