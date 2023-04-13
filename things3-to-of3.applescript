--------------------------------------------------
--------------------------------------------------
-- Import tasks from Things to OmniFocus
--------------------------------------------------
--------------------------------------------------
--
-- Script taken from: http://forums.omnigroup.com/showthread.php?t=14846&page=2 && https://gist.github.com/cdzombak/11265615 
-- Added: OF3 & Things 3 compatibility; task order; areas/folders; tags
-- Empty your Things Trash first.
--
-- Does not support:
--  Recurring tasks
--  Sub-tasks
--  Someday tasks (can't get them from T3 unless they are not in a project)
--  Tag short cuts (not an OF3 feature)
--  Cancellation date (no OF3 equivalent)
--  Contact for a task (no OF3 equivalent)
--  Modification date from Things (it's a read only attribute in OF3)

--
-- Title of project for stuff in things with no project (avoids going into the Inbox)
--
property noProjectTitle : "No Project In Things"

set answer to the button returned of ¬
	(display alert ¬
		¬
			"Things 3 to Omnifocus 3 Importer" & return & return & "PLEASE READ BEFORE PROCEEDING" message ¬
		"The script does not yet import sub-tasks or recurrences.
>> 'Some Day' tasks that are assigned to a project will not be imported. <<
Omnifocus does not support tag short cuts, cancellation dates or contact info for a task,
and does not permit the importation of modification date.

1. TAKE BACKUPS!
2. Empty your trash on Things 3.
3. Reset your database on OmniFocus 3 & delete default tags.
4. Run Clean Up when done on OmniFocus to remove logged tasks.
5. Setup sync after import has completed.

Then press 'I Understand' to get going.
Importation will take a while, about 3,000 tasks per hour.
" buttons {"How do I reset Omnifocus?", "I Understand", "    Cancel    "} default button 3)
if answer is "    Cancel    " then return
if answer is "How do I reset Omnifocus?" then
	display dialog "Make sure you take backups of your Omnifocus database if you've used it before. Resetting will delete even the backups unless they are copied elsewhere!" with icon stop
	open location "https://support.omnigroup.com/omnifocus-reset-database/"
	return
end if
tell application "Things3"
	--
	-- Import T3 hierarchal tags into OF3 in correct order and without duplicates
	--
	-- Get tags from T3
	set tagList to {}
	repeat with aTag in every tag
		if (parent tag of aTag) is missing value then
			copy {null, name of aTag as string} to end of tagList
		else
			copy {name of parent tag of aTag as string, name of aTag as string} to end of tagList
		end if
	end repeat
	
	-- Put tags into OF3
	tell application "OmniFocus"
		tell default document
			-- we do this twice, once with first level and then again with second level
			-- this is the only way to preserve order
			
			-- first pass - parents only
			repeat with aTag in tagList
				set theParentTag to first item of aTag
				set theChildTag to second item of aTag
				
				if theParentTag is null then
					if not (tag theChildTag exists) then ¬
						make new tag with properties {name:theChildTag}
				end if
			end repeat
			
			-- second pass - children only			
			repeat with aTag in tagList
				set theParentTag to first item of aTag
				set theChildTag to second item of aTag
				
				if theParentTag is not null then
					set parentTag to tag theParentTag
					if not (my isTagInList(name of every tag of parentTag, theChildTag)) then
						set childTag to make new tag with properties {name:theChildTag}
						move childTag to (end of tags of (first tag whose name is theParentTag))
					end if
				end if
			end repeat
		end tell
	end tell -- End of Tag Import
	
	--	
	-- Import T3 Areas as Folders into OF3
	--
	-- Get areas from T3
	set folderList to name of every area
	log "Processing " & (count of folderList) & " folders"
	
	-- Put areas into OF3
	tell application "OmniFocus"
		tell default document
			repeat with aFolder in folderList
				if not (folder aFolder exists) then
					make new folder with properties {name:aFolder}
				end if
			end repeat
		end tell
	end tell -- End of Folder Import
	--
	-- Import Projects into OF3
	-- 
	set projectList to {{missing value, noProjectTitle, "", "active", "", {}}}
	set completedProjectList to {}
	set AppleScript's text item delimiters to ","
	repeat with aProject in every project
		set areaName to null
		if area of aProject is missing value then
			set areaName to missing value
		else
			set areaName to name of area of aProject as string
		end if
		set projectName to name of aProject as string
		set projectNotes to notes of aProject as string
		--		set tagList to every text item of (tag names of aProject as string)
		set tagList to my gatherTagsOf(aProject)
		
		set projectCompletionDate to completion date of aProject
		
		-- status: active/‌on hold/‌done/‌dropped. vs open completed canceled
		set projectStatus to status of aProject as string
		
		copy {areaName, projectName, projectNotes, projectStatus, projectCompletionDate, tagList} to end of projectList
	end repeat
	log "Processing " & (count of projectList) & " projects"
	
	tell application "OmniFocus"
		tell default document
			repeat with aProject in projectList
				set theFolderName to first item in aProject
				set theProjectName to second item in aProject
				set theProjectNotes to third item in aProject
				set theProjectStatus to fourth item in aProject
				set theProjectTags to sixth item in aProject
				set theProjectCompletionDate to fifth item in aProject
				
				if theProjectStatus is "completed" then
					set theProjectStatus to done
				else if theProjectStatus is "canceled" then
					set theProjectStatus to dropped
				else if theProjectStatus is "open" then
					set theProjectStatus to active
				end if
				
				if theFolderName is missing value then
					-- no area
					if (project theProjectName exists) then
						set theProject to project theProjectName
					else
						set theProject to make new project with properties {name:theProjectName, note:theProjectNotes}
					end if
					
					if theProjectStatus is done then
						if not (my isItemInList(completedProjectList, theProject)) then
							copy {theProject, theProjectCompletionDate} to end of completedProjectList
						end if
					end if
				else
					-- Project inside an area
					tell folder theFolderName
						if project theProjectName exists then
							set theProject to project theProjectName
						else
							-- add tags
							set theProject to make new project with properties {name:theProjectName, note:theProjectNotes}
						end if
						
						if theProjectStatus is done then
							if not (my isItemInList(completedProjectList, theProject)) then
								copy {theProject, theProjectCompletionDate} to end of completedProjectList
							end if
						end if
						
					end tell
					move theProject to (end of sections of (first folder whose name is theFolderName))
				end if
				
				-- Write out tags
				my writeTagsTo(theProject, theProjectTags)
			end repeat
		end tell
	end tell
	
	--
	--  Import T3 To Dos into OF3
	--
	
	-- Combine all the folders you want to search here
	-- Options are: Inbox, Today, Anytime, Upcoming, Someday, Lonely Projects, Logbook, Trash
	set theTodos to to dos of list "Inbox"  & to dos of list "Anytime" & to dos of list "Upcoming" & to dos of list "Someday" & to dos of list "Lonely Projects" & to dos of list "Logbook"
	
	-- Go through all the tasks in the combined lists
	log "Processing " & (count of theTodos) & " entries"
	repeat with aTodo in theTodos
		-- Get various attributes of Things task
		set theTitle to name of aTodo
		set theNote to notes of aTodo
		set theDueDate to due date of aTodo
		set theStartDate to activation date of aTodo -- aka "Defer Date"
		set theFlagStatus to false
		set theStatus to status of aTodo as string
		set theCompletionDate to completion date of aTodo
		set theCreationDate to creation date of aTodo
		
		-- Get project & area names
		set theFolderName to missing value
		set theProjectNote to ""
		set theProjectName to ""
		set processItemFlag to true
		set isInbox to false
		set isProject to false
		
		if class of aTodo is project then
			-- Is this task actually a project?			
			set isProject to true
		else if ((area of aTodo is missing value) and (project of aTodo is missing value)) then
			-- Is this todo in the Inbox? If so, it needs special treatment
			set isInbox to true
		else if (project of aTodo) is missing value then
			-- Just an orphaned task, no such thing in OF3 so put in a folder
			set theProjectName to noProjectTitle
		else
			-- Regular task inside a project
			set theProjectName to (name of project of aTodo)
			set theProjectNote to (notes of project of aTodo)
			
			-- With a folder
			if area of project of aTodo is missing value then
				set theFolderName to missing value
			else
				set theFolderName to (name of area of project of aTodo)
			end if
		end if
		
		-- Gather tags
		set allTagNames to my gatherTagsOf(aTodo)
		
		-- Create a new task in OmniFocus
		tell application "OmniFocus"
			tell default document
				if not isProject then
					-- Create the actual task - does not de-dupe
					-- Do it differently if inbox
					if isInbox then
						set newTask to make new inbox task with properties {name:theTitle, note:theNote, creation date:theCreationDate, due date:theDueDate, defer date:theStartDate, flagged:theFlagStatus}
					else
						if theFolderName is missing value then
							if project theProjectName exists then
								tell project theProjectName
									set newTask to make new task with properties {name:theTitle, note:theNote, creation date:theCreationDate, due date:theDueDate, defer date:theStartDate, flagged:theFlagStatus}
								end tell
							end if
						else
							tell folder theFolderName
								tell project theProjectName
									set newTask to make new task with properties {name:theTitle, note:theNote, creation date:theCreationDate, due date:theDueDate, defer date:theStartDate, flagged:theFlagStatus}
								end tell
							end tell
						end if
					end if
					
					-- handle completed
					if theStatus is "completed" then
						mark complete newTask
						set completion date of newTask to theCompletionDate
					else if theStatus is "canceled" then
						mark complete newTask
						set status of newTask to dropped
						set completion date of newTask to theCompletionDate
					else if theStatus is "open" then
						mark incomplete newTask
						set completion date of newTask to missing value
					end if
					
					-- Process tags
					my writeTagsTo(newTask, allTagNames)
					
				end if -- not a task
			end tell -- OF application
		end tell -- Document
	end repeat -- Things list
	
	-- Mark complete any projects that should be that way
	tell application "OmniFocus"
		tell default document
			repeat with completedProjectInfo in completedProjectList
				set completedProject to first item of completedProjectInfo
				set completedProjectDate to second item of completedProjectInfo
				mark complete completedProject
				set completion date of completedProject to completedProjectDate
			end repeat
		end tell
	end tell
end tell -- Things application

-- Clumsy way of seeing if an item is in the Inbox as Things doesn't expose a "list" property
on isItemInList(theList, theItem)
	set the matchFlag to false
	repeat with anItem from 1 to the count of theList
		if theList contains anItem then ¬
			set the matchFlag to true
	end repeat
	return the matchFlag
end isItemInList
-- Another hack for heirarchal tags to say "does tag exist inside this other tag?"
on isTagInList(theList, theItem)
	set the matchFlag to false
	repeat with anItem from 1 to the count of theList
		if item anItem of theList is theItem then ¬
			set the matchFlag to true
	end repeat
	return the matchFlag
end isTagInList
-- less clumsy inbox hack
on isInInbox(anItem)
	return ((area of anItem is missing value) and (project of anItem is missing value))
end isInInbox
-- gather tags
on gatherTagsOf(aTodo)
	set allTagNames to {}
	tell application "Things3"
		repeat with aTag in every tag of aTodo
			if (parent tag of aTag) is missing value then
				copy {null, name of aTag} to end of allTagNames
			else
				copy {name of parent tag of aTag, name of aTag} to end of allTagNames
			end if
		end repeat
	end tell
	return allTagNames
end gatherTagsOf
-- write tags
on writeTagsTo(aTask, tagList)
	tell application "OmniFocus"
		tell default document
			repeat with aTag in tagList
				
				set theParentTag to first item of aTag
				set theChildTag to second item of aTag
				
				if theParentTag is null then
					-- No Parent tag
					add tag theChildTag to tags of aTask
				else
					-- Has a parent tag
					set childTag to (first tag of tag theParentTag whose name is theChildTag)
					add childTag to tags of aTask
				end if
			end repeat -- tags
		end tell
	end tell
end writeTagsTo
