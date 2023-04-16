from pathlib import Path

import pytest

from src.things3.db import DB, AreaInfo
from src.things3.hierarchy import Area, Tag

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
        projects=[],
        tasks=[],
    )
