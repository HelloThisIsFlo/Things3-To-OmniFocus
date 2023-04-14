
-- my listAllLists()
my checkList("Someday")
-- my checkList("Later Projects")
-- my checkList("Logbook")

on listAllLists()
    tell application "Things3"
        repeat with l in every list
            set listName to name of l as string
            log listName
        end repeat
    end tell
end listAllLists

-- # Someday
-- class:selected to do,
-- status:open,
-- tag names:,
-- cancellation date:missing value,
-- due date:missing value,
-- modification date:date Friday,
-- 14 April 2023 at 10:38:24,
-- contact:missing value,
-- project:project id Km4EJiWToPe5pu2EkrPp5x,
-- area:missing value,
-- notes:,
-- activation date:missing value,
-- id:HU7MeeWyYSKFetsyxCDTCC,
-- completion date:missing value,
-- name:Someday Task in Project In The Area,
-- creation date:date Friday, 14 April 2023 at 10:38:24

-- # Defered
-- class:selected to do,
-- status:open,
-- tag names:,
-- cancellation date:missing value,
-- due date:missing value,
-- modification date:date Friday,
-- 14 April 2023 at 10:38:24,
-- contact:missing value,
-- project:project id Km4EJiWToPe5pu2EkrPp5x,
-- area:missing value,
-- notes:,
-- activation date:date Monday,
-- 1 January 2024 at 00:00:00,
-- id:HMbTknenqpRvoEtpJpnp2x,
-- completion date:missing value,
-- name:Defered Task in Project In The Area,
-- creation date:date Friday, 14 April 2023 at 10:38:24

-- # Anytime
-- class:selected to do,
-- status:open,
-- tag names:,
-- cancellation date:missing value,
-- due date:missing value,
-- modification date:date Friday,
-- 14 April 2023 at 10:38:24,
-- contact:missing value,
-- project:project id Km4EJiWToPe5pu2EkrPp5x,
-- area:missing value,
-- notes:,
-- activation date:missing value,
-- id:HGgMoSx3jxDVJtWYjLHrbg,
-- completion date:missing value,
-- name:Task in Project In The Area,
-- creation date:date Friday, 14 April 2023 at 10:38:24

on checkList(theList)
    tell application "Things3"
        set theTasks to to dos of list theList
        repeat with aTask in theTasks
            log name of aTask as string
            -- log (get properties of aTask)
            if class of aTask is project then
                set theProjectTasks to to dos of aTask
                repeat with aProjectTask in theProjectTasks
                    log "- " & name of aProjectTask as string
                    log (get properties of aProjectTask)
                end repeat
            end if
        end repeat
    end tell
    -- tell application "Things3"
    --     set theTasks to to dos of list theList
    --     log count of theTasks
    --     repeat with aTask in theTasks
    --         log name of aTask as string
    --         log (get properties of aTask)
    --         set taskProperties to properties of aTask
    --         repeat with propertyName in name of every property of aTask
    --             log propertyName & ": " & (get value of property propertyName of taskProperties)
    --         end repeat




    --         -- set theDueDate to due date of aTask
    --         -- if theDueDate is not missing value then
    --         --     log theDueDate
    --         --     -- log (get properties of theDueDate)
    --         --     -- log "hello"
    --         --     set time string of theDueDate to "17:00:00" 
    --         -- end if
    --     end repeat
    -- end tell
end checkList


-- tell application "OmniFocus"
--     tell default document
--         -- Create Tag: 'DROPPED' to show that a task was 'cancelled' in Things 3
--         --  => Will need to manually set it to 'dropped' in OmniFocus

--         set droppedTag to make new tag with properties {name:"DROPPED"}
--         set newTask to make new inbox task with properties {name:"Test Task", note:"testNote"}

--         add droppedTag to (tags of newTask)


--         -- set theProject to make new project with properties {name:"test project" , note:"noooote", due date: date "01/01/2019 00:00:00"}
--         set theProject to make new project with properties {name:"test project" , note:"noooote", due date: missing value}
--         set theDueDate to due date of theProject
--         log "yo"
--         set time of theDueDate to "17:00"
--         log "yo"
--         log theDueDate


--     end tell
-- end tell


	-- set theTodos to to dos of list "Inbox"  & to dos of list "Anytime" & to dos of list "Upcoming" & to dos of list "Later Projects"


-- tell application "Things3"
--     repeat with l in every list
--         set listName to name of l as string
--         log listName
--     end repeat

-- 	repeat with aProject in every project
--         set debug to name of aProject as string
--         -- log (get properties of aProject)
--         set theDueDate to due date of aProject
-- 		if theDueDate is not missing value then
--             log theDueDate
--             -- log (get properties of theDueDate)
--             -- log "hello"
--             set time string of theDueDate to "17:00:00" 
--         end if

-- 		-- set areaName to null
-- 		-- if area of aProject is missing value then
-- 		-- 	set areaName to missing value
-- 		-- else
-- 		-- 	set areaName to name of area of aProject as string
-- 		-- end if
-- 		-- set projectName to name of aProject as string
-- 		-- set projectNotes to notes of aProject as string
-- 		-- --		set tagList to every text item of (tag names of aProject as string)
-- 		-- set tagList to my gatherTagsOf(aProject)
		
-- 		-- set projectCompletionDate to completion date of aProject
		
-- 		-- -- status: active/‌on hold/‌done/‌dropped. vs open completed canceled
-- 		-- set projectStatus to status of aProject as string
		
-- 		-- copy {areaName, projectName, projectNotes, projectStatus, projectCompletionDate, tagList} to end of projectList
-- 	end repeat
-- end tell