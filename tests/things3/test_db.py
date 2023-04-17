from datetime import date, datetime
from pathlib import Path

import pytest

from src.things3.db import DB, AreaInfo
from src.things3.hierarchy import Area, Tag, Task, Status, Project, Heading

AREA_ID_THE_AREA = "Dr6Ji5SN5eyuDWzKxK9WL9"

AREA_ID_EMPTY = "Jbjf23KssoqXWDjZzGngut"


@pytest.fixture
def db():
    return DB(Path(__file__).parent / "example_db" / "main.sqlite")


def test_list_areas(db):
    assert db.list_areas() == [
        AreaInfo(AREA_ID_THE_AREA, "The Area"),
        AreaInfo(AREA_ID_EMPTY, "Empty Area"),
    ]


def test_fetch_empty_area(db):
    assert db.fetch_area(AREA_ID_EMPTY) == Area("Empty Area", tags=[], tasks=[])


def test_fetch_nonexistent_area(db):
    with pytest.raises(ValueError):
        db.fetch_area("Nonexistent Area")


def test_area_with_everything(db):
    # Note: Only supporting 1 degree of tag nesting (for now?)
    assert db.fetch_area(AREA_ID_THE_AREA) == Area(
        "The Area",
        tags=[
            Tag("Area Tag Child", parent=Tag("Area Tag Parent")),
        ],
        projects=[
            Project(
                "Project In The Area",
                note="Some project note",
                tags=[Tag("Project Tag Parent")],
                due_date=date(2023, 7, 14),
                tasks=[
                    Task(
                        "Task in Project In The Area",
                        note="Some Task note",
                        tags=[Tag("Task Tag Parent")],
                    ),
                    Task(
                        "Task w/ Deadline in Project In The Area",
                        due_date=date(2023, 6, 14),
                        tags=[Tag("Task Tag Parent")],
                    ),
                    Task(
                        "Task w/ Checklist in Project In The Area",
                        checklist=[
                            Task("Checklist item 1"),
                            Task("Checklist item 2"),
                            Task("Checklist item 3"),
                        ],
                        tags=[
                            Tag("Task Tag Child", parent=Tag("Task Tag Parent"))
                        ],
                    ),
                    Task(
                        "Dropped Task in Project In The Area",
                        status=Status.DROPPED,
                        completion_datetime=datetime(
                            2023, 4, 14, 10, 37, 14, 472046
                        ),
                    ),
                    Task(
                        "Completed Task in Project In The Area",
                        status=Status.COMPLETED,
                        completion_datetime=datetime(
                            2023, 4, 14, 10, 37, 7, 466055
                        ),
                    ),
                    Task(
                        "Deferred Task in Project In The Area",
                        defer_date=date(2024, 1, 1),
                    ),
                    Task("Someday Task in Project In The Area", someday=True),
                    Task(
                        "Repeating Task in Project In The Area",
                        repeating=True,
                    ),
                ],
                headings=[
                    Heading(
                        "Heading",
                        tasks=[
                            Task("Task in Heading"),
                            Task("Another Task in Heading"),
                        ],
                    )
                ],
            ),
            Project(
                "Dropped In The Area",
                status=Status.DROPPED,
                completion_datetime=datetime(2023, 4, 14, 10, 39, 8, 309116),
                tasks=[
                    Task(
                        "Dropped Task in Project In The Area",
                        status=Status.DROPPED,
                        completion_datetime=datetime(
                            2023, 4, 14, 10, 37, 14, 472046
                        ),
                    ),
                    Task(
                        "Completed Task in Project In The Area",
                        status=Status.COMPLETED,
                        completion_datetime=datetime(
                            2023, 4, 14, 10, 37, 7, 466055
                        ),
                    ),
                ],
            ),
            Project(
                "Completed Project In The Area",
                status=Status.COMPLETED,
                completion_datetime=datetime(2023, 4, 14, 10, 38, 56, 889877),
                tasks=[
                    Task(
                        "Dropped Task in Project In The Area",
                        status=Status.DROPPED,
                        completion_datetime=datetime(
                            2023, 4, 14, 10, 37, 14, 472046
                        ),
                    ),
                    Task(
                        "Completed Task in Project In The Area",
                        status=Status.COMPLETED,
                        completion_datetime=datetime(
                            2023, 4, 14, 10, 37, 7, 466055
                        ),
                    ),
                ],
            ),
            Project(
                "Someday Project In The Area",
                someday=True,
                tasks=[
                    Task("Task in Someday Project In The Area"),
                ],
            ),
            Project(
                "Deferred Project In The Area",
                defer_date=date(2024, 1, 1),
                tasks=[
                    Task("Task in Deferred Project In The Area"),
                ],
            ),
        ],
        tasks=[
            Task("Task in the Area"),
            Task(
                "Completed Task in the Area",
                status=Status.COMPLETED,
                completion_datetime=datetime(2023, 4, 14, 10, 40, 18, 94449),
            ),
            Task(
                "Dropped Task in the Area",
                status=Status.DROPPED,
                completion_datetime=datetime(2023, 4, 14, 10, 40, 21, 182182),
            ),
            Task("Deferred Task in the Area", defer_date=date(2024, 1, 1)),
            Task("Someday Task in the Area", someday=True),
        ],
    )
