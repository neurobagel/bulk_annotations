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

from pathlib import Path
from warnings import warn

import pandas as pd

from logger import bulk_annotation_logger
from utils import (
    exclude_datasets,
    get_participants_dict,
    init_output,
    new_row_template,
    output_dir,
    read_csv_autodetect_date,
    update_row_with_column_info,
)

LOG_LEVEL = "INFO"

log = bulk_annotation_logger(LOG_LEVEL)


def main():
    datalad_superdataset = Path("/home/remi/datalad/datasets.datalad.org")
    openneuro = datalad_superdataset / "openneuro"

    datasets = pd.read_csv(output_dir() / "openneuro.tsv", sep="\t")

    output = init_output()

    for dataset_name in datasets.name:
        mask = datasets.name == dataset_name

        log.info(f"dataset '{dataset_name}'")

        if exclude_datasets(datasets[mask]):
            continue

        participant_tsv = openneuro / dataset_name / "participants.tsv"
        try:
            participants = read_csv_autodetect_date(participant_tsv, sep="\t")
        except pd.errors.ParserError:
            warn(f"Could not parse: {participant_tsv}")
            continue

        participants_dict = get_participants_dict(
            datasets, dataset_name, openneuro
        )

        log.debug(
            f"dataset {dataset_name} has columns: {participants.columns.values}"
        )

        row_template = new_row_template(
            dataset_name, nb_rows=len(participants), include_levels=False
        )

        for column in participants.columns:
            this_row = row_template.copy()

            this_row = update_row_with_column_info(
                this_row, column, participants, participants_dict
            )

            for key in output.keys():
                output[key].append(this_row[key])

    output = pd.DataFrame.from_dict(output)
    output_filename = output_dir() / "bulk_annotation_columns.tsv"
    output.to_csv(
        output_filename,
        index=False,
        sep="\t",
    )

    output.column = output.column.str.lower()
    count = output.column.value_counts()
    count.to_csv(output_dir() / "unique_columns.tsv", sep="\t")


if __name__ == "__main__":
    main()
