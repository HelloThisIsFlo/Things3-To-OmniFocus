from glob import glob
from pathlib import Path
from os.path import expanduser

import click

from src import taskpaper
from src.things3.db import DB, AreaInfo
from src.things3.hierarchy import Area

DEFAULT_DB_PATH = (
    "~/Library/Group Containers"
    "/JLMPQHK86H.com.culturedcode.ThingsMac"
    "/**/Things Database.thingsdatabase/"
    "main.sqlite"
)

OUTPUT_DIR = Path(__file__).parent / "output"


class Main:
    def __init__(self, db_path: Path, output_dir: Path):
        self.db = DB(db_path)
        self.output_dir = output_dir

    def export_all(self):
        self.output_dir.mkdir(exist_ok=True)
        print("")
        for area in self.db.list_areas():
            self.export_area(area)

    def export_area(self, area: AreaInfo):
        output_path = self.output_dir / f"{area.title}.taskpaper"

        print(
            f"Exporting '{area.title}' to "
            f"'{self.output_dir}/{area.title}.taskpaper'"
        )
        area = self.db.fetch_area(area.uuid)
        area_as_taskpaper = taskpaper.convert_area(area)
        with open(output_path, "w") as output_file:
            output_file.write(area_as_taskpaper)


@click.command()
@click.option(
    "--dbpath",
    default=DEFAULT_DB_PATH,
    help="Path to the Things 3 database file. "
    "Can use globbing (e.g. `~/**/main-*.sqlite`)",
)
@click.option(
    "--output",
    default=OUTPUT_DIR,
    help="Directory where the exported TaskPaper files should be written",
    type=click.Path(file_okay=False),
)
def main(dbpath, output):
    if not (matching_db_paths := glob(expanduser(dbpath))):
        raise ValueError(f"Invalid DB Path: {dbpath}")

    Main(Path(matching_db_paths[0]), output).export_all()


if __name__ == "__main__":
    main()
