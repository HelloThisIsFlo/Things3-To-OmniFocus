-- DOCUMENTATION OF THE FIELDS
--
-- * type:
--   0 task
--   1 project
--   2 heading
--
-- * start:
--   0 In Inbox
--   1 Not Deferred/Someday (Available or Completed/Dropped)
--   2 Deferred/Someday
--
-- * status:
--   0 To-do / Active
--   1 ???
--   2 Dropped
--   3 Completed
--
-- * trashed
--   0 TODO
--
-- * stopDate: Completion/Dropped date

SELECT *
FROM TMArea;
SELECT *
FROM TMAreaTag;
SELECT *
FROM TMTag
SELECT *
FROM TMTask
WHERE uuid == 'Dr6Ji5SN5eyuDWzKxK9WL9'

-- Get all tasks uuids
SELECT uuid
FROM TMTask
WHERE type = 0;

-- Get DEMO task uuid
-- NOTE: Put the result in the parameters (pycharm/datagrip)
SELECT uuid
FROM TMTask task
WHERE task.title LIKE '%EVERYTHING%'
  AND rt1_recurrenceRule IS NULL;


-- Get checklist items of DEMO task
SELECT title
FROM TMChecklistItem
WHERE task == ${demo_task_uuid}
ORDER BY "index";


SELECT uuid,
       title,
       notes,
       startDate,
       deadline,
       project,
       heading,
       area,
       rt1_repeatingTemplate
FROM TMTask
WHERE uuid == ${demo_task_uuid};

SELECT uuid,
       title,
       notes,
       startDate,
       deadline,
       project,
       heading,
       area,
       rt1_repeatingTemplate
FROM TMTask;

SELECT startDate, deadline
FROM TMTask
WHERE uuid == ${demo_task_uuid};

SELECT task.title,
       project.title,
       task.start,
       task.status,
       task.trashed,
       task.stopDate,
       task.startBucket,
       task.t2_deadlineOffset,
       task.untrashedLeafActionsCount,
       task.openUntrashedLeafActionsCount,
       task.rt1_instanceCreationPaused,
       task.rt1_instanceCreationCount,
       task.experimental,
       task.repeater,
       task.repeaterMigrationDate,
       task.rt1_repeatingTemplate,
       task.rt1_recurrenceRule

FROM TMTask task
         LEFT JOIN TMTask project ON task.project == project.uuid
WHERE task.type == 0;

--     WHERE task IN (SELECT demo_task_id.uuid FROM demo_task_id)


SELECT title, stopDate, startDate, reminderTime, *
FROM TMTask
WHERE reminderTime IS NOT NULL
  AND status = 0
ORDER BY reminderTime

SELECT *
FROM TMTask

SELECT title, uuid, project
FROM TMTask
WHERE project IS NOT NULL;

SELECT title, uuid
FROM TMTask
WHERE uuid == 'E54iBHBjgbBpWxhwoSGpGE';



SELECT task.title, project.title
FROM TMTask task
         LEFT JOIN TMTask project ON task.project == project.uuid;

SELECT task.title, task.heading, heading.project, project.title
FROM TMTask task
         LEFT JOIN TMTask heading ON task.heading == heading.uuid
         LEFT JOIN TMTask project ON heading.project == project.uuid
WHERE task.title LIKE 'Task w/ Subtask in Project In The Area'
LIMIT 1;

SELECT task.title, project.*, heading.*, task.*
FROM TMTask AS task
         LEFT JOIN TMTask AS heading ON task.heading == heading.uuid
         LEFT JOIN TMTask AS project ON (task.project == project.uuid OR heading.project == project.uuid)
         JOIN TMTaskTag tasktag ON (task.uuid == tasktag.tasks OR project.uuid == tasktag.tasks)
         JOIN TMTag AS tag ON tag.uuid == tasktag.tags
WHERE tag.title == 'Task Tag Parent'
  AND task.status == 0
  AND task.trashed == 0
  AND task.start == 1
  AND task.type == 0
  AND (project.start == 1 OR project.start IS NULL);

SELECT title, uuid
FROM TMTask
WHERE title LIKE '%Task w/ Checklist in Project In The Area%';
SELECT title
FROM TMChecklistItem
WHERE task == ${demo_task_uuid}
ORDER BY "index"

SELECT title, uuid, rt1_recurrenceRule, start, startDate, trashed, *
FROM TMTask
WHERE title LIKE '%Repeating Task%';
SELECT leavesTombstone, trashed, *
FROM TMTask;
SELECT trashed
FROM TMTask
WHERE trashed != 0;

SELECT title, uuid
FROM TMTask
WHERE type = 1;

SELECT title, "index", trashed, status, *
FROM TMTask
WHERE (project = ${debug_project_id} OR heading = ${debug_heading_id})
  AND trashed == 0
  AND type = 0
ORDER BY  "index", status;
