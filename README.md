# Things 3 to OmniFocus

This project helps you migrate your Things 3 database into OmniFocus.

This is done with the use of the TaskPaper format. This script will convert each Area into a TaskPaper file.
There it's just a matter of copy-pasting the content of each file into a OmniFocus folder.

**The following is not supported:**

- Trashed items
- Projects NOT in an Area
- Repeating schedule on repeating tasks
    - Repeating tasks and projects _will_ be migrated, but their repeating schedule will have to be set manually in
      OmniFocus
    - See: [How to use](#how-to-use)

# How to use

## Install

1. Clone this repository
2. Install the dependencies with [Pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)
   ```
    pipenv install
    ```

## Run the script

1. Run the app
   ```
    pipenv run python app.py
    ```

Optionally, you can specify the path to your Things3 database file, or the output directory.

```
pipenv run python app.py --dbpath /path/to/things3/database/main.sqlite --output /path/to/output/dir
```

Note: `--dbpath` supports globbing (e.g. `~/**/main-*.sqlite`)

## Import into OmniFocus

### Import the TaskPaper files

1. Copy the content of each file/area into a OmniFocus folder

### Manually adjust

#### Repeating tasks and projects

1. Identify the repeating tasks and projects by looking at the `MANUALLY_CONVERT__REPEATING` tag
2. In Things3, go to the `Repeating` section
3. Set the repeating schedule for each task/project
4. Delete the `MANUALLY_CONVERT__REPEATING` tag

#### Someday projects

1. Identify the someday projects by looking at the `MANUALLY_CONVERT__SOMEDAY` tag
2. Set the status of each someday project to `On Hold`
3. Delete the `MANUALLY_CONVERT__SOMEDAY` tag

#### Someday tasks

1. Set the tag `SOMEDAY` to `On Hold`
2. _Optional:_ Rename the `SOMEDAY` tag

#### Tasks in Areas without a project

The tasks that were in an Area without a project will be in a project named `[AREA_NAME]`
(where `AREA_NAME` is the name of the area).
This is because OmniFocus does not allow tasks to live in a folder.

These projects are no real project, but are instead Single-Action lists.
Setting a project to be a Single-Action list is not possible via TaskPaper
(or at least I couldn't figure out how to do it), so these need to be set manually

1. Identify the projects by looking at the `MANUALLY_CONVERT__SINGLE-ACTIONS` tag
2. Convert each project to a Single-Action list
3. Delete the `MANUALLY_CONVERT__SINGLE-ACTIONS` tag

