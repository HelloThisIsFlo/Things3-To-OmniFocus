from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


@dataclass
class Tag:
    name: str
    parent: Optional["Tag"]


class Status(Enum):
    """
    The values correspond to the values in the Things database.
    """

    ACTIVE = 0
    DROPPED = 2
    COMPLETED = 3


@dataclass
class Task:
    title: str
    notes: str
    due_date: Optional[date]
    defer_date: Optional[date]
    tags: list[Tag]
    checklist: list[str]
    someday: bool
    repeating: bool
    status: Status
    completion_date: Optional[date]


@dataclass
class Heading:
    title: str
    tasks: list[Task]


@dataclass
class Project:
    title: str
    notes: str
    due_date: Optional[date]
    defer_date: Optional[date]
    tags: list[Tag]
    someday: bool
    repeating: bool
    status: Status
    completion_date: Optional[date]
    tasks: list[Task]
    headings: list[Heading]


@dataclass
class Area:
    title: str
    tags: list[Tag]
    projects: list[Project]
    tasks: list[Task]
