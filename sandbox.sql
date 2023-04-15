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
       task.repeaterMigrationDate
FROM TMTask task
         LEFT JOIN TMTask project ON task.project == project.uuid
WHERE task.type == 0;

--     WHERE task IN (SELECT demo_task_id.uuid FROM demo_task_id)


SELECT title, stopDate, startDate, reminderTime, *
FROM TMTask
WHERE reminderTime IS NOT NULL
  AND status = 0
ORDER BY reminderTime