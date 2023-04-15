# To avoid confusion I will refer to TaskPaper 'tags' as 'attributes'.
# Whenever I actually use the word 'tag' it will refer to a Things 3 tag.

# Note: Converting areas is not supported. Instead, convert projects and generate 1 file per area

from src.things3 import *

NEWLINE_WITH_INDENT = "\n    "

DEFER_TIME = "08:00"
DUE_TIME = "17:00"


def convert_tags(tags: list[Tag]) -> str:
    def format_tag(tag: Tag) -> str:
        if tag.parent:
            return f"{tag.parent.name} : {tag.name}"
        return tag.name

    return ", ".join(map(format_tag, tags))


def convert_task(task: Task) -> str:
    # NOTE: No need to add the '@context' attribute, it is added automatically by OmniFocus.
    #       Not adding it removes a lot of complexity as its value depends on the tags of the parent project.

    def append_attribute(attribute: str, value: str) -> None:
        header.append(f"@{attribute}({value})")

    def format_date(date, time):
        return f"{date.isoformat()} {time}"

    def format_note() -> str:
        if not task.note:
            return ""
        return NEWLINE_WITH_INDENT + task.note.replace("\n", NEWLINE_WITH_INDENT) + "\n"

    def format_checklist() -> str:
        if not task.checklist:
            return ""
        return NEWLINE_WITH_INDENT + NEWLINE_WITH_INDENT.join(
            convert_task(Task(item, tags=task.tags)) for item in task.checklist
        )

    header = [task.title]
    append_attribute("parallel", "true")
    append_attribute("autodone", "false")
    if task.tags:
        append_attribute("tags", convert_tags(task.tags))
    if task.defer_date:
        append_attribute("defer", format_date(task.defer_date, DEFER_TIME))
    if task.due_date:
        append_attribute("due", format_date(task.due_date, DUE_TIME))
    if task.status == Status.COMPLETED:
        append_attribute("done", task.completion_datetime.isoformat())
    if task.status == Status.DROPPED:
        append_attribute("dropped", task.completion_datetime.isoformat())

    return "- " + " ".join(header) + format_note() + format_checklist()
