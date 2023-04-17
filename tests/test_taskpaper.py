import re
from datetime import date, datetime
from textwrap import dedent

import pytest

from src.taskpaper import (
    convert_task,
    DEFER_TIME,
    DUE_TIME,
    convert_project,
    SOMEDAY_TAG,
    convert_area,
    MANUALLY_CONVERT_TAGS,
)
from src.things3.hierarchy import Task, Tag, Status, Project, Heading, Area

TASK_TITLE = "The Task"


class TestConvertTask:
    def test_simple_task(self):
        task = Task(TASK_TITLE)
        assert convert_task(
            task) == "- The Task @parallel(true) @autodone(false)"

    def test_with_note(self):
        task = Task(TASK_TITLE,
                    "The note\nSecond line of the note\nThird line of the note")
        assert convert_task(task) == dedent(
            """\
            - The Task @parallel(true) @autodone(false)
                The note
                Second line of the note
                Third line of the note
            """
        )

    def test_with_note__escape_dash_with_em_dash(self):
        task = Task(TASK_TITLE,
                    "- The note\n"
                    "- Second line of the note\n"
                    "- Third line of the note")
        assert convert_task(task) == dedent(
            """\
            - The Task @parallel(true) @autodone(false)
                – The note
                – Second line of the note
                – Third line of the note
            """
        )

    def test_with_note__escape_end_of_line_column_by_adding_a_space(self):
        task = Task(TASK_TITLE,
                    "This line ends in with a column note:\n"
                    "- It is problematic because:\n"
                    "  - OmniFocus would believe this describes a project")
        assert convert_task(task) == dedent(
            """\
            - The Task @parallel(true) @autodone(false)
                This line ends in with a column note: 
                – It is problematic because: 
                  – OmniFocus would believe this describes a project
            """
        )

    def test_with_tags(self):
        task = Task(TASK_TITLE, tags=[Tag(name="tag1"), Tag(name="tag2_child",
                                                            parent=Tag(
                                                                "tag_parent"))])
        assert convert_task(
            task) == "- The Task @parallel(true) @autodone(false) @tags(tag1, tag_parent : tag2_child)"

    def test_with_defer_and_due_dates_using_configured_times(self):
        task = Task(TASK_TITLE, defer_date=date(2023, 4, 19),
                    due_date=date(2023, 5, 10))
        assert (
                convert_task(task)
                == f"- The Task @parallel(true) @autodone(false) @defer(2023-04-19 {DEFER_TIME}) @due(2023-05-10 {DUE_TIME})"
        )

    def test_completed_task(self):
        task = Task(TASK_TITLE, status=Status.COMPLETED,
                    completion_datetime=datetime(2023, 5, 10, 12, 0, 0))
        assert convert_task(
            task) == "- The Task @parallel(true) @autodone(false) @done(2023-05-10 12:00:00)"

    def test_dropped_task(self):
        task = Task(TASK_TITLE, status=Status.DROPPED,
                    completion_datetime=datetime(2023, 5, 10, 5, 45, 30))
        assert convert_task(
            task) == "- The Task @parallel(true) @autodone(false) @dropped(2023-05-10 05:45:30)"

    def test_with_checklist__tags_are_inherited(self):
        task = Task(
            TASK_TITLE,
            tags=[Tag(name="tag1")],
            checklist=[
                Task("Checklist item 1"),
                Task("Checklist item 2"),
            ],
        )
        assert convert_task(task) == dedent(
            """\
        - The Task @parallel(true) @autodone(false) @tags(tag1)
            - Checklist item 1 @parallel(true) @autodone(false) @tags(tag1)
            - Checklist item 2 @parallel(true) @autodone(false) @tags(tag1)"""
        )

    def test_with_checklist_and_note(self):
        task = Task(
            TASK_TITLE,
            note="note",
            checklist=[
                Task("Checklist item 1"),
                Task("Checklist item 2"),
            ],
        )
        assert convert_task(task) == dedent(
            """\
        - The Task @parallel(true) @autodone(false)
            note

            - Checklist item 1 @parallel(true) @autodone(false)
            - Checklist item 2 @parallel(true) @autodone(false)"""
        )

    def test_someday_task__flags_with_tags(self):
        task = Task(TASK_TITLE, someday=True)
        assert convert_task(
            task) == f"- The Task @parallel(true) @autodone(false) @tags({SOMEDAY_TAG})"

    def test_repeating_task__flags_with_tags(self):
        task = Task(TASK_TITLE, repeating=True)
        assert (
                convert_task(task)
                == f"- The Task @parallel(true) @autodone(false) @tags({MANUALLY_CONVERT_TAGS['REPEATING']})"
        )

    def test_repeating_task_with_checklist__flags_with_tags__tag_does_not_propagate_to_checklist_items(
            self):
        task = Task(
            TASK_TITLE,
            repeating=True,
            checklist=[
                Task("Checklist item 1"),
                Task("Checklist item 2"),
            ],
        )
        assert convert_task(task) == dedent(
            f"""\
                - The Task @parallel(true) @autodone(false) @tags({MANUALLY_CONVERT_TAGS['REPEATING']})
                    - Checklist item 1 @parallel(true) @autodone(false)
                    - Checklist item 2 @parallel(true) @autodone(false)"""
        )


class TestConvertProject:
    def test_completed_project(self):
        project = Project("The Project", status=Status.COMPLETED,
                          completion_datetime=datetime(2023, 5, 10, 12, 0, 0))
        assert convert_project(
            project) == "- The Project @parallel(true) @autodone(false) @done(2023-05-10 12:00:00)"

    def test_project_with_most_attributes_and_note_but_no_task(self):
        project = Project(
            title="The Project",
            note="The project note\n- Dash to escape",
            tags=[Tag(name="tag1"),
                  Tag(name="tag2_child", parent=Tag("tag_parent"))],
            status=Status.ACTIVE,
            due_date=date(2023, 5, 10),
            defer_date=date(2023, 4, 19),
            repeating=True,
        )
        assert convert_project(project) == dedent(
            f"""\
            - The Project @parallel(true) @autodone(false) @defer(2023-04-19 {DEFER_TIME}) @due(2023-05-10 {DUE_TIME}) @tags(tag1, tag_parent : tag2_child, {MANUALLY_CONVERT_TAGS['REPEATING']})
                The project note
                – Dash to escape
            """
        )

    def test_someday_project_uses_someday_project_tag__someday_project_tag_does_not_propagate_to_tasks(
            self):
        # Note: It's not possible to set a project "on hold" via TaskPaper, so we flag it and let the user manually
        #       resolve it.
        project = Project(
            "The Project",
            someday=True,
            tasks=[
                Task("Task 1 - Basic"),
                Task("Task 2 - With Tags", tags=[Tag(name="tag1"),
                                                 Tag(name="tag2_child",
                                                     parent=Tag(
                                                         "tag_parent"))]),
            ],
        )
        assert convert_project(project) == dedent(
            f"""\
                - The Project @parallel(true) @autodone(false) @tags({MANUALLY_CONVERT_TAGS['SOMEDAY_PROJECT']})
                    - Task 1 - Basic @parallel(true) @autodone(false)
                    - Task 2 - With Tags @parallel(true) @autodone(false) @tags(tag1, tag_parent : tag2_child)"""
        )

    def test_repeating_project__repeating_project_tag_does_not_propagate_to_tasks(
            self):
        project = Project(
            "The Project",
            repeating=True,
            tasks=[
                Task("Task 1 - Basic"),
                Task("Task 2 - With Tags", tags=[Tag(name="tag1"),
                                                 Tag(name="tag2_child",
                                                     parent=Tag(
                                                         "tag_parent"))]),
            ],
        )
        assert convert_project(project) == dedent(
            f"""\
                - The Project @parallel(true) @autodone(false) @tags({MANUALLY_CONVERT_TAGS['REPEATING']})
                    - Task 1 - Basic @parallel(true) @autodone(false)
                    - Task 2 - With Tags @parallel(true) @autodone(false) @tags(tag1, tag_parent : tag2_child)"""
        )

    def test_project_with_tasks(self):
        project = Project(
            "The Project",
            note="The project note",
            tags=[Tag(name="project_tag")],
            tasks=[
                Task("Task 1 - Basic"),
                Task("Task 2 - With Note", "The note"),
                Task("Task 3 - With Tags", tags=[Tag(name="tag1"),
                                                 Tag(name="tag2_child",
                                                     parent=Tag(
                                                         "tag_parent"))]),
                Task("Task 4 - With Checklist",
                     checklist=[Task("Checklist item 1"),
                                Task("Checklist item 2")]),
                Task(
                    "Task 5 - With Note and Checklist",
                    "The note",
                    checklist=[Task("Checklist item 1"),
                               Task("Checklist item 2")],
                ),
            ],
        )
        assert convert_project(project) == dedent(
            """\
            - The Project @parallel(true) @autodone(false) @tags(project_tag)
                The project note
                
                - Task 1 - Basic @parallel(true) @autodone(false) @tags(project_tag)
                - Task 2 - With Note @parallel(true) @autodone(false) @tags(project_tag)
                    The note

                - Task 3 - With Tags @parallel(true) @autodone(false) @tags(project_tag, tag1, tag_parent : tag2_child)
                - Task 4 - With Checklist @parallel(true) @autodone(false) @tags(project_tag)
                    - Checklist item 1 @parallel(true) @autodone(false) @tags(project_tag)
                    - Checklist item 2 @parallel(true) @autodone(false) @tags(project_tag)
                - Task 5 - With Note and Checklist @parallel(true) @autodone(false) @tags(project_tag)
                    The note

                    - Checklist item 1 @parallel(true) @autodone(false) @tags(project_tag)
                    - Checklist item 2 @parallel(true) @autodone(false) @tags(project_tag)"""
        )

    def test_project_with_headings_and_tasks(self):
        project = Project(
            "The Project",
            note="The project note",
            tags=[Tag(name="project_tag")],
            tasks=[
                Task(
                    "Root Task - With Note and Checklist",
                    "The note",
                    tags=[Tag(name="tag1"),
                          Tag(name="tag2_child", parent=Tag("tag_parent"))],
                    checklist=[Task("Checklist item 1"),
                               Task("Checklist item 2")],
                ),
            ],
            headings=[
                Heading(
                    "Heading 1",
                    tasks=[
                        Task("Task 1 - Basic"),
                        Task(
                            "Task 2 - With Tags",
                            tags=[Tag(name="tag1"), Tag(name="tag2_child",
                                                        parent=Tag(
                                                            "tag_parent"))],
                        ),
                    ],
                ),
            ],
        )
        assert convert_project(project) == dedent(
            """\
            - The Project @parallel(true) @autodone(false) @tags(project_tag)
                The project note

                - Root Task - With Note and Checklist @parallel(true) @autodone(false) @tags(project_tag, tag1, tag_parent : tag2_child)
                    The note
                    
                    - Checklist item 1 @parallel(true) @autodone(false) @tags(project_tag, tag1, tag_parent : tag2_child)
                    - Checklist item 2 @parallel(true) @autodone(false) @tags(project_tag, tag1, tag_parent : tag2_child)
                - Heading 1 @parallel(true) @autodone(false) @tags(project_tag)
                    - Task 1 - Basic @parallel(true) @autodone(false) @tags(project_tag)
                    - Task 2 - With Tags @parallel(true) @autodone(false) @tags(project_tag, tag1, tag_parent : tag2_child)"""
        )


class TestConvertArea:
    def test_area_with_projects_and_tags(self):
        area = Area(
            "The Area",
            tags=[Tag(name="area_tag")],
            projects=[
                Project("Project 1"),
                Project(
                    "Project 2",
                    tags=[Tag(name="project_tag")],
                    tasks=[
                        Task(
                            "Task 1 - With Tags",
                            tags=[Tag(name="tag1"), Tag(name="tag2_child",
                                                        parent=Tag(
                                                            "tag_parent"))],
                        )
                    ],
                ),
            ],
        )
        assert convert_area(area) == dedent(
            """\
            - Project 1 @parallel(true) @autodone(false) @tags(area_tag)
            - Project 2 @parallel(true) @autodone(false) @tags(area_tag, project_tag)
                - Task 1 - With Tags @parallel(true) @autodone(false) @tags(area_tag, project_tag, tag1, tag_parent : tag2_child)"""
        )

    def test_area_with_tasks__wrap_in_a_single_actions_project__tasks_dont_inherit_single_actions_tag(
            self):
        area = Area(
            "The Area",
            tags=[Tag(name="area_tag")],
            tasks=[
                Task(
                    "Task 1 - With Tags",
                    tags=[Tag(name="tag1"),
                          Tag(name="tag2_child", parent=Tag("tag_parent"))],
                )
            ],
        )
        assert convert_area(area) == dedent(
            f"""\
            - [The Area] @parallel(true) @autodone(false) @tags(area_tag, {MANUALLY_CONVERT_TAGS['SINGLE-ACTIONS']})
                - Task 1 - With Tags @parallel(true) @autodone(false) @tags(area_tag, tag1, tag_parent : tag2_child)"""
        )
