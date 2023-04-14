
import shutil
import sqlite3
from pathlib import Path


DB_PATH = Path("/Users/floriankempenich/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac/simplified_copy/main.sqlite")

tasks_name = "neighborhood"
query = """
SELECT task.title, project.*, actionGroup.*, task.*
FROM TMTask AS task
        LEFT JOIN TMTask AS actionGroup ON task.actionGroup == actionGroup.uuid
        LEFT JOIN TMTask AS project ON (task.project == project.uuid OR actionGroup.project == project.uuid)
        JOIN TMTaskTag tasktag ON (task.uuid == tasktag.tasks OR project.uuid == tasktag.tasks)
        JOIN TMTag AS tag ON tag.uuid == tasktag.tags
WHERE tag.title == '📍 Neighbourhood'
    AND task.status == 0
    AND task.trashed == 0
    AND task.start == 1
    AND task.type == 0
    AND (project.start == 1 OR project.start IS NULL);
"""

# Explanation
# ===========
# task.status == 0     <- Task is not 'completed' (3 otherwise)
# task.type == 1       <- 'Task' is not _actually_ a Project
# task.trashed == 0    <- Task is not trashed
# task.type == 0       <- Task is not a project (1 otherwise)
# task.start == 1      <- Task is either Today or Anytime (not Someday or Scheduled)
# project.start == 1   <- Project, in which the Task is, is either  Today or Anytime (not Someday or Scheduled)
#                         Using 'LEFT JOIN' to make sure to include Tasks not in a Project (directly in Area)
#
# What is 'actionGroup'?
# ----------------------
# When a task is within a heading, it won't have a 'project' ID,
# instead it will have an 'actionGroup' ID, and this 'actionGroup' ID will have the 'project' ID.

TASKS_ATTRIBUTE = "tasks"


def sandbox():
    # Copy the DB file
    # This is to prevent Syncthings from seeing local modifications and stop syncing
    # DB_PATH_COPY.parent.mkdir(exist_ok=True)
    # shutil.copyfile(DB_PATH_ORIGINAL, DB_PATH_COPY)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    tasks = [row[0] for row in results]
    cursor.close()
    conn.close()
    return tasks

sandbox()