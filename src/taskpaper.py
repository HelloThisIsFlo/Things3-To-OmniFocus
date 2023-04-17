# To avoid confusion I will refer to TaskPaper 'tags' as 'attributes'.
# Whenever I actually use the word 'tag' it will refer to a Things 3 tag.
from dataclasses import replace
from datetime import time

from src.things3.hierarchy import *

DEFER_TIME = time(8)
DUE_TIME = time(17)
SOMEDAY_TAG = "SOMEDAY"
MANUALLY_CONVERT_TAGS = {
    "SOMEDAY_PROJECT": "MANUALLY_CONVERT__SOMEDAY_PROJECT",
    "REPEATING": "MANUALLY_CONVERT__REPEATING",
    "SINGLE-ACTIONS": "MANUALLY_CONVERT__SINGLE-ACTIONS",
}

INDENT = "    "


def newline(indent=0):
    return "\n" + INDENT * indent


def convert_tags(tags: list[Tag]) -> str:
    def format_tag(tag: Tag) -> str:
        if tag.parent:
            return f"{tag.parent.name} : {tag.name}"
        return tag.name

    return ", ".join(map(format_tag, tags))


def format_subtasks(subtasks: list[Task], tags: list[Tag], indent=0) -> str:
    if not subtasks:
        return ""
    tags = [t for t in tags if t.name not in MANUALLY_CONVERT_TAGS.values()]
    return newline(indent) + newline(indent).join(
        convert_task(replace(task, tags=tags + task.tags), indent)
        for task in subtasks
    )


def convert_task(task: Task, indent=0) -> str:
    # NOTE: No need to add the '@context' attribute, it is added automatically by OmniFocus.
    #       Not adding it removes a lot of complexity as its value depends on the tags of the parent project.

    def append_attribute(attribute: str, value: str) -> None:
        header.append(f"@{attribute}({value})")

    def format_datetime(to_format: datetime) -> str:
        return to_format.strftime("%Y-%m-%d %H:%M:%S")

    def format_note() -> str:
        def escape_dash_with_emdash(note: str) -> str:
            return note.replace("-", "–")

        if not task.note:
            return ""

        note = escape_dash_with_emdash(task.note)
        return (
                newline(indent)
                + note.replace("\n", newline(indent))
                + newline(0)
        )

    def format_checklist():
        return format_subtasks(task.checklist, tags, indent)

    indent += 1
    header = [task.title]

    append_attribute("parallel", "true")
    append_attribute("autodone", "false")

    if task.defer_date:
        append_attribute(
            "defer",
            format_datetime(datetime.combine(task.defer_date, DEFER_TIME))
        )
    if task.due_date:
        append_attribute(
            "due",
            format_datetime(datetime.combine(task.due_date, DUE_TIME))
        )

    tags = task.tags.copy()
    if task.someday:
        tags.append(Tag(SOMEDAY_TAG))
    if task.repeating:
        tags.append(Tag(MANUALLY_CONVERT_TAGS["REPEATING"]))
    if tags:
        append_attribute("tags", convert_tags(tags))

    if task.status == Status.COMPLETED:
        append_attribute(
            "done",
            task.completion_datetime.strftime("%Y-%m-%d %H:%M:%S")
        )
    if task.status == Status.DROPPED:
        append_attribute("dropped", format_datetime(task.completion_datetime))

    return "- " + " ".join(header) + format_note() + format_checklist()


def convert_project(project: Project, indent=0) -> str:
    def format_headings():
        if not project.headings:
            return ""
        return newline(indent) + newline(indent).join(
            convert_task(
                Task(h.title, checklist=h.tasks, tags=project.tags), indent
            )
            for h in project.headings
        )

    project_as_task = Task(
        title=project.title,
        note=project.note,
        tags=(
            [Tag(MANUALLY_CONVERT_TAGS["SOMEDAY_PROJECT"])] + project.tags
            if project.someday
            else project.tags
        ),
        status=project.status,
        due_date=project.due_date,
        defer_date=project.defer_date,
        someday=False,
        repeating=project.repeating,
        completion_datetime=project.completion_datetime,
    )

    indent += 1
    project_taskpaper = convert_task(project_as_task)
    return (
            project_taskpaper
            + format_subtasks(project.tasks, project.tags, indent)
            + format_headings()
    )


def convert_area(area: Area) -> str:
    indent = 0

    projects = area.projects
    if area.tasks:
        area_project = Project(
            title=f"[{area.title}]",
            tags=[Tag(MANUALLY_CONVERT_TAGS["SINGLE-ACTIONS"])],
            tasks=area.tasks,
        )
        projects = [area_project] + area.projects

    projects = [replace(p, tags=area.tags + p.tags) for p in projects]

    return newline(indent).join(convert_project(p, indent) for p in projects)
