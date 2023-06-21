"""Fetch and print the name of a BIDS dataset."""

from pathlib import Path

import typer
from bids import BIDSLayout
from bids.exceptions import BIDSValidationError


def main(
    ds: Path = typer.Option(
        ...,
        help="Path to a BIDS dataset directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
    )
):
    """Fetch and print the name of a BIDS dataset from the dataset_description.json."""
    # NOTE: Validation will fail if dataset lacks a dataset_description.json or if the "Name" key is missing.
    try:
        layout = BIDSLayout(ds, validate=True)
    except BIDSValidationError:
        print("None")
        return

    name = layout.get_dataset_description().get("Name")
    if name == "":
        print("None")
    else:
        print(name)


if __name__ == "__main__":
    typer.run(main)
