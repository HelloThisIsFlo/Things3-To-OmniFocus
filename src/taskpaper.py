# To avoid confusion I will refer to TaskPaper 'tags' as 'attributes'.
# Whenever I actually use the word 'tag' it will refer to a Things 3 tag.
from dataclasses import replace

from src.things3 import *

# Note: Converting areas is not supported. Instead, convert projects and generate 1 file per area

INDENT = "    "

DEFER_TIME = "08:00"
DUE_TIME = "17:00"
SOMEDAY_TAG = "SOMEDAY"
REPEATING_TAG = "REPEATING"


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
    return newline(indent) + newline(indent).join(
        convert_task(replace(task, tags=tags + task.tags), indent) for task in subtasks
    )


def convert_task(task: Task, indent=0) -> str:
    # NOTE: No need to add the '@context' attribute, it is added automatically by OmniFocus.
    #       Not adding it removes a lot of complexity as its value depends on the tags of the parent project.

    def append_attribute(attribute: str, value: str) -> None:
        header.append(f"@{attribute}({value})")

    def format_date(date, time):
        return f"{date.isoformat()} {time}"

    def format_note() -> str:
        if not task.note:
            return ""
        return newline(indent) + task.note.replace("\n", newline(indent)) + "\n"

    def format_checklist():
        return format_subtasks(task.checklist, tags, indent)

    indent += 1
    header = [task.title]

    append_attribute("parallel", "true")
    append_attribute("autodone", "false")

    if task.defer_date:
        append_attribute("defer", format_date(task.defer_date, DEFER_TIME))
    if task.due_date:
        append_attribute("due", format_date(task.due_date, DUE_TIME))

    tags = task.tags.copy()
    if task.someday:
        tags.append(Tag(SOMEDAY_TAG))
    if task.repeating:
        tags.append(Tag(REPEATING_TAG))
    if tags:
        append_attribute("tags", convert_tags(tags))

    if task.status == Status.COMPLETED:
        append_attribute("done", task.completion_datetime.isoformat())
    if task.status == Status.DROPPED:
        append_attribute("dropped", task.completion_datetime.isoformat())

    return "- " + " ".join(header) + format_note() + format_checklist()


def convert_project(project: Project, indent=0) -> str:
    def format_headings():
        if not project.headings:
            return ""
        return newline(indent) + newline(indent).join(
            convert_task(Task(h.title, checklist=h.tasks, tags=project.tags), indent) for h in project.headings
        )

    project_as_task = Task(
        title=project.title,
        note=project.note,
        tags=project.tags,
        status=project.status,
        due_date=project.due_date,
        defer_date=project.defer_date,
        someday=project.someday,
        repeating=project.repeating,
        completion_datetime=project.completion_datetime,
    )

    indent += 1
    project_taskpaper = convert_task(project_as_task)
    return project_taskpaper + format_subtasks(project.tasks, project.tags, indent) + format_headings()
