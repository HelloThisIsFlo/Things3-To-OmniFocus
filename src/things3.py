from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


@dataclass
class Tag:
    name: str
    parent: Optional["Tag"] = None


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
    note: str = ""
    tags: list[Tag] = field(default_factory=list)
    checklist: list[str] = field(default_factory=list)
    status: Status = Status.ACTIVE
    due_date: Optional[date] = None
    defer_date: Optional[date] = None
    someday: bool = False
    repeating: bool = False
    completion_datetime: Optional[datetime] = None

    def __post_init__(self):
        match self.status:
            case Status.COMPLETED | Status.DROPPED:
                if not self.completion_datetime:
                    raise ValueError("A completed task must have a completion date")


@dataclass
class Heading:
    title: str
    tasks: list[Task] = field(default_factory=list)


@dataclass
class Project:
    title: str
    note: str = ""
    tags: list[Tag] = field(default_factory=list)
    headings: list[Heading] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    status: Status = Status.ACTIVE
    due_date: Optional[date] = None
    defer_date: Optional[date] = None
    someday: bool = False
    repeating: bool = False
    completion_datetime: Optional[date] = None


@dataclass
class Area:
    title: str
    tags: list[Tag] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
