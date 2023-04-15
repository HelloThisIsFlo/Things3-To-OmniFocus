from datetime import date, datetime
from textwrap import dedent

from src.taskpaper import convert_task, DEFER_TIME, DUE_TIME
from src.things3 import Task, Tag, Status

TASK_TITLE = "The Task"


def test_convert_simple_task():
    task = Task(TASK_TITLE)
    assert convert_task(task) == "- The Task @parallel(true) @autodone(false)"


def test_convert_task_with_note():
    task = Task(TASK_TITLE, "The note\nSecond line of the note\nThird line of the note")
    assert convert_task(task) == dedent(
        """\
        - The Task @parallel(true) @autodone(false)
            The note
            Second line of the note
            Third line of the note
        """
    )


def test_convert_task_with_tags():
    task = Task(TASK_TITLE, tags=[Tag(name="tag1"), Tag(name="tag2_child", parent=Tag("tag_parent"))])
    assert convert_task(task) == "- The Task @parallel(true) @autodone(false) @tags(tag1, tag_parent : tag2_child)"


def test_convert_task_with_defer_and_due_dates_using_configured_times():
    task = Task(TASK_TITLE, defer_date=date(2023, 4, 19), due_date=date(2023, 5, 10))
    assert (
        convert_task(task)
        == f"- The Task @parallel(true) @autodone(false) @defer(2023-04-19 {DEFER_TIME}) @due(2023-05-10 {DUE_TIME})"
    )


def test_convert_completed_task():
    task = Task(TASK_TITLE, status=Status.COMPLETED, completion_datetime=datetime(2023, 5, 10, 12, 0, 0))
    assert convert_task(task) == "- The Task @parallel(true) @autodone(false) @done(2023-05-10T12:00:00)"


def test_convert_dropped_task():
    task = Task(TASK_TITLE, status=Status.DROPPED, completion_datetime=datetime(2023, 5, 10, 5, 45, 30))
    assert convert_task(task) == "- The Task @parallel(true) @autodone(false) @dropped(2023-05-10T05:45:30)"
