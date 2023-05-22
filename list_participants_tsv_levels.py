from pathlib import Path
from warnings import warn

import pandas as pd

from heuristics import is_age, is_participant_id, is_sex, skip_column
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

    output = init_output(include_levels=True)

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
            dataset_name, nb_rows=len(participants), include_levels=True
        )

        for column in participants.columns:
            this_row = row_template.copy()

            this_row = update_row_with_column_info(
                this_row, column, participants, participants_dict
            )

            if is_participant_id(participants, column):
                this_row["controlled_term"] = "nb:ParticipantID"
            elif is_age(this_row):
                this_row["controlled_term"] = "nb:Age"
            elif is_sex(column):
                this_row["controlled_term"] = "nb:Sex"

            for key in output.keys():
                output[key].append(this_row[key])

            if skip_column(this_row):
                log.debug(f"  column '{column}': skipping column")
                continue

            output = list_levels(
                output, participants, participants_dict, column, row_template
            )

    output = pd.DataFrame.from_dict(output)
    output_filename = output_dir() / "bulk_annotation_levels.tsv"
    output.to_csv(
        output_filename,
        index=False,
        sep="\t",
    )


def list_levels(
    output: pd.DataFrame,
    participants: pd.DataFrame,
    participants_dict: dict,
    column: str,
    row_template: dict[str, str],
) -> pd.DataFrame:
    """Get levels from data dictionary first, then from the data itself, \
    and appends them to the output dictionary.

    Adds any undefined level not found in the data dictionary.
    """
    levels = {}
    if (
        participants_dict
        and participants_dict.get(column)
        and participants_dict[column].get("Levels")
    ):
        levels = participants_dict[column]["Levels"]
        output = append_levels(output, levels, column, row_template)

    actual_levels = list(participants[column].unique())
    defined_levels = set(levels.keys())
    undefined_levels = set(actual_levels) - defined_levels

    if len(undefined_levels) == 0:
        return output

    if len(defined_levels):
        log.info(f"  column '{column}': defined levels: {set(levels.keys())}")
    log.info(f"  column '{column}': undefined levels: {undefined_levels}")

    output = append_levels(output, undefined_levels, column, row_template)

    return output


def append_levels(
    output: pd.DataFrame,
    levels: set | dict,
    column: str,
    row_template: dict[str, str],
):
    for level_ in levels:
        log.debug(f"  column '{column}': appending level '{level_}'")

        this_row = row_template.copy()
        this_row["column"] = column
        this_row["is_row"] = False
        this_row["value"] = level_
        if isinstance(levels, dict):
            this_row["description"] = levels.get(level_, "n/a")
        for key in this_row:
            output[key].append(this_row[key])
    return output


if __name__ == "__main__":
    main()
