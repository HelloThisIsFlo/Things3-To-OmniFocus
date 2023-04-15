import pytest

from src.things3.hierarchy import Task, Status


def test_completed_task_must_have_completion_datetime():
    with pytest.raises(ValueError):
        Task("The Task", status=Status.COMPLETED, completion_datetime=None)


def test_dropped_task_must_have_completion_datetime():
    with pytest.raises(ValueError):
        Task("The Task", status=Status.DROPPED, completion_datetime=None)
