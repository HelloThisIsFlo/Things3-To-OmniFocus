#!/bin/bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

DB_DIR="$HOME/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac/ThingsData-TS977/Things Database.thingsdatabase"
cp "$DB_DIR"/* ./tests/things3/example_db/


cd - >/dev/null
