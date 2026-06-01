import argparse
import sys

from task_manager.models import Task
from task_manager.storage import load_tasks, next_id, save_tasks


def cmd_add(args):
    tasks = load_tasks()
    task = Task(id=next_id(tasks), title=args.title)
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task [{task.id}]: {task.title}")


def cmd_list(args):
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        status = "x" if task.completed else " "
        print(f"[{status}] {task.id}. {task.title}")


def main():
    parser = argparse.ArgumentParser(prog="tasks", description="Simple task manager")
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Add a new task")
    add_p.add_argument("title", help="Task title")

    sub.add_parser("list", help="List all tasks")

    args = parser.parse_args()

    if args.command == "add":
        cmd_add(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
