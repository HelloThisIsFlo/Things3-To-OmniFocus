import sqlite3
from dataclasses import dataclass
from pathlib import Path

from src.things3.hierarchy import Area, Tag

SQL_FETCH_TAG = "select title from TMTag where uuid = ?"

SQL_FETCH_AREA_TAGS = """select tag.title, tag.parent from TMArea area
                        join TMAreaTag areaTag on areaTag.areas = area.uuid
                        join TMTag tag on tag.uuid = areaTag.tags
                        where area.uuid = ?"""

FETCH_EVERYTHING_SQL = """
SELECT * FROM TMTask
where area = ?
"""


@dataclass
class AreaInfo:
    uuid: str
    title: str


class DB:
    def __init__(self, db_path: Path):
        print(db_path.absolute())
        self.conn = sqlite3.connect(str(db_path))

    def list_areas(self):
        return [
            AreaInfo(row[0], row[1])
            for row in self.conn.execute("SELECT uuid, title FROM TMArea")
        ]

    def fetch_area(self, area_uuid):
        def fetch_title():
            row = self.conn.execute(
                "SELECT title FROM TMArea where uuid = ?", (area_uuid,)
            ).fetchone()
            if not row:
                raise ValueError(f"Area with uuid '{area_uuid}' does not exist")
            return row[0]

        def fetch_area_tags():
            tags = []
            for tag_row in self.conn.execute(SQL_FETCH_AREA_TAGS, (area_uuid,)):
                tag = Tag(tag_row[0])
                if parent_tag := tag_row[1]:
                    tag.parent = Tag(
                        self.conn.execute(
                            SQL_FETCH_TAG, (parent_tag,)
                        ).fetchone()[0]
                    )
                tags.append(tag)
            return tags

        def fetch_projects():
            return []

        def fetch_tasks():
            return []

        return Area(
            fetch_title(),
            tags=fetch_area_tags(),
            projects=fetch_projects(),
            tasks=fetch_tasks(),
        )
