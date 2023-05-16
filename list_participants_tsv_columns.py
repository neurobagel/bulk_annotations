"""List all columns in participants.tsv files in openneuro datasets.

Tries to identify columns:
- that are all dates or timestamps
- controlled terms
- have a description in participants.json
- columns data type
- nb of levels in that column
- nb of rows in the dataset

This is saved in:
- bulk_annotation_columns.tsv

Also saved:
- unique_columns.tsv counts the number of for column name
"""


import json
from pathlib import Path
from warnings import warn

import pandas as pd

from utils import bulk_annotation_logger, is_yes_no, output_dir, read_csv, is_euro_format

LOG_LEVEL = "INFO"

log = bulk_annotation_logger(LOG_LEVEL)


CONTROLLED_TERMS = {
    "participant_id": "nb:ParticipantID",
}


def init_output() -> dict[str, list]:
    return {
        "dataset": [],
        "nb_rows": [],
        "column": [],
        "type": [],
        "nb_levels": [],
        "description": [],
        "controlled_term": [],
    }


def new_row(dataset_name: str) -> dict[str, str | int | bool]:
    return {
        "dataset": dataset_name,
        "column": "n/a",
        "type": "n/a",
        "nb_levels": 0,
        "description": "n/a",
        "controlled_term": "n/a",
    }


def main():
    datalad_superdataset = Path("/home/remi/datalad/datasets.datalad.org")
    openneuro = datalad_superdataset / "openneuro"

    datasets = pd.read_csv(output_dir() / "openneuro.tsv", sep="\t")

    output = init_output()

    for dataset_name in datasets.name:
        mask = datasets.name == dataset_name

        log.info(f"dataset '{dataset_name}'")

        if not datasets[mask].has_mri.values[0] or not datasets[mask].has_participant_tsv.values[0]:
            continue

        row_template = new_row(dataset_name)

        participant_tsv = openneuro / dataset_name / "participants.tsv"
        try:
            participants = read_csv(participant_tsv, sep="\t")
        except pd.errors.ParserError:
            warn(f"Could not parse: {participant_tsv}")
            continue

        participants_dict = {}
        if datasets[mask].has_participant_json.values[0]:
            participant_json = openneuro / dataset_name / "participants.json"
            with open(participant_json) as f:
                participants_dict = json.load(f)

        log.debug(f"dataset {dataset_name} has columns: {participants.columns.values}")

        for column in participants.columns:
            this_row = row_template.copy()

            this_row["column"] = column

            this_row["nb_rows"] = len(participants)

            this_row["is_row"] = True

            if column in CONTROLLED_TERMS.keys():
                this_row["controlled_term"] = CONTROLLED_TERMS[column]

            if participants_dict and participants_dict.get(column):
                this_row["description"] = participants_dict[column].get("Description", "n/a")

            this_row["type"] = participants[column].dtype
            if this_row["type"] == "object":
                if is_yes_no(participants[column]):
                    this_row["type"] = "yes/no"
                elif is_euro_format(participants[column]):
                    this_row["type"] = "euro"

            this_row["nb_levels"] = len(participants[column].unique())

            for key in output.keys():
                output[key].append(this_row[key])

    output = pd.DataFrame.from_dict(output)

    output_filename = output_dir() / "bulk_annotation_columns.tsv"

    output.to_csv(
        output_filename,
        index=False,
        sep="\t",
    )

    count = output.column.value_counts()
    count.to_csv(output_dir() / "unique_columns.tsv", sep="\t")


if __name__ == "__main__":
    main()
