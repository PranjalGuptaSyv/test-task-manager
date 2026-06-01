from task_manager.models import Task
from task_manager.storage import next_id


def test_task_roundtrip():
    task = Task(id=1, title="Buy milk", created_at="2026-06-01T10:00:00", completed=False)
    assert Task.from_dict(task.to_dict()) == task


def test_task_defaults_not_completed():
    task = Task(id=1, title="Walk dog")
    assert task.completed is False


def test_next_id_empty():
    assert next_id([]) == 1


def test_next_id_existing():
    tasks = [Task(id=1, title="a"), Task(id=3, title="b")]
    assert next_id(tasks) == 4


def test_task_complete_flag():
    task = Task(id=1, title="Read book")
    task.completed = True
    assert task.to_dict()["completed"] is True


def test_task_from_dict_completed():
    data = {"id": 2, "title": "Write tests", "created_at": "2026-06-01T10:00:00", "completed": True}
    task = Task.from_dict(data)
    assert task.completed is True
