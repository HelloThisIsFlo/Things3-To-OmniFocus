import sqlite3
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from pathlib import Path

from src.things3.hierarchy import Area, Tag, Task, Status, Project, Heading


class Type(Enum):
    TASK = 0
    PROJECT = 1
    HEADING = 2


@dataclass
class AreaInfo:
    uuid: str
    title: str


# Tag Queries
SQL_FETCH_TAG = "SELECT title FROM TMTag WHERE uuid = ?"
SQL_AREA_FETCH_TAGS = """SELECT tag.title, tag.parent FROM TMArea area
                        JOIN TMAreaTag areaTag ON areaTag.areas = area.uuid
                        JOIN TMTag tag ON tag.uuid = areaTag.tags
                        WHERE area.uuid = ?"""
SQL_TASK_OR_PROJECT_FETCH_TAGS = """SELECT tag.title, tag.parent FROM TMTask task
                        JOIN TMTaskTag taskTag ON taskTag.tasks = task.uuid
                        JOIN TMTag tag ON tag.uuid = taskTag.tags
                        WHERE task.uuid = ?"""

# IDs Queries
SQL_AREA_FETCH_TASK_IDS = f"""select uuid 
                                    from TMTask task 
                                    where task.area = ? 
                                        and task.type = {Type.TASK.value}
                                        and trashed = 0
                                    ORDER BY task."index" """
SQL_AREA_FETCH_PROJECT_IDS = f"""select uuid 
                                        from TMTask project 
                                        where project.area = ? 
                                            and project.type = {Type.PROJECT.value}
                                            and trashed = 0
                                        ORDER BY project."index" """

SQL_PROJECT_FETCH_TASK_IDS = f"""select uuid 
                                    from TMTask task 
                                    where task.project = ?
                                        and task.type = {Type.TASK.value}
                                        and trashed = 0
                                    ORDER BY task."index" """
SQL_PROJECT_FETCH_HEADING_IDS = f"""select uuid 
                                    from TMTask heading
                                    where heading.project = ?
                                        and heading.type = {Type.HEADING.value}
                                        and trashed = 0
                                    ORDER BY heading."index" """
SQL_HEADING_FETCH_TASK_IDS = f"""select uuid    
                                        from TMTask task 
                                        where task.heading = ?
                                            and task.type = {Type.TASK.value}
                                            and trashed = 0
                                        ORDER BY task."index" """

# Item Queries
SQL_FETCH_PROJECT_OR_HEADING_OR_TASK = """
SELECT title, notes, status, deadline, startDate, start, rt1_recurrenceRule, stopDate 
FROM TMTask
WHERE uuid = ?
"""
SQL_FETCH_CHECKLIST_ITEMS = (
    'SELECT title FROM TMChecklistItem WHERE task == ? ORDER BY "index"'
)


def convert_bin_date(bin_date):
    start_year = 16
    start_month = 12
    start_day = 7

    def day():
        return (((1 << start_month) - 1) & bin_date) >> start_day

    def month():
        return (((1 << start_year) - 1) & bin_date) >> start_month

    def year():
        return bin_date >> start_year

    return date(year(), month(), day())


class DB:
    """
    A wrapper around the Things 3 SQLite database.

    NOT SUPPORTED:
        - Trashed items
        - Projects NOT in an Area
        - Repeating schedule on repeating tasks
        (only supports flagging the task as repeating)

    SUPPORTED:
        - Everything Else
    """

    def __init__(self, db_path: Path):
        print(db_path.absolute())
        self.conn = sqlite3.connect(str(db_path))

    def list_areas(self):
        return [
            AreaInfo(row[0], row[1])
            for row in self.conn.execute("SELECT uuid, title FROM TMArea")
        ]

    def fetch_area(self, area_uuid, ignore_logbook=False):
        def fetch_title():
            row = self.conn.execute(
                "SELECT title FROM TMArea WHERE uuid = ?", (area_uuid,)
            ).fetchone()
            if not row:
                raise ValueError(f"Area with uuid '{area_uuid}' does not exist")
            return row[0]

        def fetch_area_tags():
            tags = []
            for tag_row in self.conn.execute(SQL_AREA_FETCH_TAGS, (area_uuid,)):
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
            project_ids = [
                row[0]
                for row in self.conn.execute(
                    SQL_AREA_FETCH_PROJECT_IDS, (area_uuid,)
                )
            ]
            projects = [
                self.fetch_project(project_id, ignore_logbook)
                for project_id in project_ids
            ]
            if ignore_logbook:
                projects = [p for p in projects if p.status == Status.ACTIVE]
            return projects

        def fetch_tasks():
            task_ids = [
                row[0]
                for row in self.conn.execute(
                    SQL_AREA_FETCH_TASK_IDS, (area_uuid,)
                )
            ]
            tasks = [self.fetch_task(task_id) for task_id in task_ids]
            if ignore_logbook:
                tasks = [t for t in tasks if t.status == Status.ACTIVE]
            return tasks

        return Area(
            fetch_title(),
            tags=fetch_area_tags(),
            projects=fetch_projects(),
            tasks=fetch_tasks(),
        )

    def fetch_task(self, task_id):
        def fetch_tags():
            tags = []
            for tag_row in self.conn.execute(
                    SQL_TASK_OR_PROJECT_FETCH_TAGS, (task_id,)
            ):
                tag = Tag(tag_row[0])
                if parent_tag := tag_row[1]:
                    tag.parent = Tag(
                        self.conn.execute(
                            SQL_FETCH_TAG, (parent_tag,)
                        ).fetchone()[0]
                    )
                tags.append(tag)
            return tags

        def fetch_checklist_items():
            return [
                Task(row[0])
                for row in self.conn.execute(
                    SQL_FETCH_CHECKLIST_ITEMS, (task_id,)
                )
            ]

        row = self.conn.execute(
            SQL_FETCH_PROJECT_OR_HEADING_OR_TASK, (task_id,)
        ).fetchone()

        title = row[0]
        note = row[1]
        status = row[2]
        deadline = row[3]
        start_date = row[4]
        start = row[5]
        recurrence_rule = row[6]
        stop_date = row[7]

        return Task(
            title,
            note,
            tags=fetch_tags(),
            checklist=fetch_checklist_items(),
            status=Status(status),
            due_date=convert_bin_date(deadline) if deadline else None,
            defer_date=convert_bin_date(start_date) if start_date else None,
            someday=start == 2 and not start_date and recurrence_rule is None,
            repeating=recurrence_rule is not None,
            completion_datetime=(
                datetime.fromtimestamp(stop_date) if stop_date else None
            ),
        )

    def fetch_project(self, project_id, ignore_logbook):
        def fetch_tags():
            tags = []
            for tag_row in self.conn.execute(
                    SQL_TASK_OR_PROJECT_FETCH_TAGS, (project_id,)
            ):
                tag = Tag(tag_row[0])
                if parent_tag := tag_row[1]:
                    tag.parent = Tag(
                        self.conn.execute(
                            SQL_FETCH_TAG, (parent_tag,)
                        ).fetchone()[0]
                    )
                tags.append(tag)
            return tags

        def fetch_tasks():
            task_ids = [
                row[0]
                for row in self.conn.execute(
                    SQL_PROJECT_FETCH_TASK_IDS, (project_id,)
                )
            ]
            tasks = [self.fetch_task(task_id) for task_id in task_ids]
            if ignore_logbook:
                tasks = [t for t in tasks if t.status == Status.ACTIVE]
            return tasks

        def fetch_headings():
            heading_ids = [
                row[0]
                for row in self.conn.execute(
                    SQL_PROJECT_FETCH_HEADING_IDS, (project_id,)
                )
            ]
            return [
                self.fetch_heading(heading_id, ignore_logbook)
                for heading_id in heading_ids
            ]

        row = self.conn.execute(
            SQL_FETCH_PROJECT_OR_HEADING_OR_TASK, (project_id,)
        ).fetchone()

        title = row[0]
        note = row[1]
        status = row[2]
        deadline = row[3]
        start_date = row[4]
        start = row[5]
        repeating_template = row[6]
        stop_date = row[7]

        return Project(
            title,
            note,
            tags=fetch_tags(),
            tasks=fetch_tasks(),
            headings=fetch_headings(),
            status=Status(status),
            due_date=convert_bin_date(deadline) if deadline else None,
            defer_date=convert_bin_date(start_date) if start_date else None,
            someday=start == 2 and not start_date,
            repeating=repeating_template is not None,
            completion_datetime=(
                datetime.fromtimestamp(stop_date) if stop_date else None
            ),
        )

    def fetch_heading(self, heading_id, ignore_logbook):
        def fetch_tasks():
            task_ids = [
                row[0]
                for row in self.conn.execute(
                    SQL_HEADING_FETCH_TASK_IDS, (heading_id,)
                )
            ]
            tasks = [self.fetch_task(task_id) for task_id in task_ids]
            if ignore_logbook:
                tasks = [t for t in tasks if t.status == Status.ACTIVE]
            return tasks

        row = self.conn.execute(
            SQL_FETCH_PROJECT_OR_HEADING_OR_TASK, (heading_id,)
        ).fetchone()

        return Heading(title=row[0], tasks=fetch_tasks())
