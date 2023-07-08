import json
from pathlib import Path
import logging

import typer


logger = logging.getLogger(__name__)


def main(in_json: Path):
    """Add a description to a data dictionary."""
    with open(in_json, "r") as f:
        data_dict = json.load(f)

    have_written = False
    for k, v in data_dict.items():
        if "Description" not in v:
            data_dict[k]["Description"] = "added description for Neurobagel"
            have_written = True

    logger.warning(f"Have written: {have_written}")

    with open(in_json, "w") as f:
        json.dump(data_dict, f, indent=2)


if __name__ == "__main__":
    typer.run(main)