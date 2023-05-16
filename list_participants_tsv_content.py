import json
import logging
import re
from pathlib import Path
from warnings import warn

import numpy as np
import pandas as pd
from rich import print
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


CONTROLLED_TERMS = {
    "participant_id": "nb:ParticipantID",
}

# columns whose levels do not need to be listed
# probably better handled by some fuzzy matching
COLUMNS_TO_SKIP = (
    "participant_id",
    "participant_ID",
    "date",
    "time",
    "age",
    "Age",
    "DOB",
    "session_id",
    "date_of_scan",
    "age_at_first_scan_years",
    "ageAtFirstScanYears",
    "height",
    "weight",
    "scan_time",
    "years_of_education",
    "dataset_id",
    "date_run",
    "ftcd-fmri-delay-days",
    "time_after_stroke" "HF (/min)",
    "age (years)",
    "a_date",
    "birthdate_shifted",
)

MAX_NB_LEVELS = 100


def main():
    datalad_superdataset = Path("/home/remi/datalad/datasets.datalad.org")
    openneuro = datalad_superdataset / "openneuro"

    datasets = pd.read_csv(Path(__file__).resolve().parent / "openneuro.tsv", sep="\t")

    output = {
        "dataset": [],
        "column": [],
        "value": [],
        "is_row": [],
        "description": [],
        "controlled_term": [],
        "units": [],
    }

    for dataset_name in datasets.name:
        mask = datasets.name == dataset_name

        log.info(f"dataset '{dataset_name}'")

        if (
            not datasets[mask].has_mri.values[0]
            or not datasets[mask].has_participant_tsv.values[0]
        ):
            continue

        row_template = new_row(dataset_name)

        participant_tsv = openneuro / dataset_name / "participants.tsv"
        try:
            participants = pd.read_csv(participant_tsv, sep="\t")
        except pd.errors.ParserError:
            warn(f"Could not parse: {participant_tsv}")
            continue

        participants_dict = {}
        if datasets[mask].has_participant_json.values[0]:
            participant_json = openneuro / dataset_name / "participants.json"
            with open(participant_json, "r") as f:
                participants_dict = json.load(f)

        log.debug(f"dataset {dataset_name} has columns: {participants.columns.values}")

        for column in participants.columns:
            this_row = row_template.copy()

            this_row["column"] = column
            this_row["is_row"] = True
            if column in CONTROLLED_TERMS.keys():
                this_row["controlled_term"] = CONTROLLED_TERMS[column]
            if participants_dict and participants_dict.get(column):
                this_row["description"] = participants_dict[column].get(
                    "Description", "n/a"
                )
            for key in this_row.keys():
                output[key].append(this_row[key])

            output = list_levels(
                output, participants, participants_dict, column, row_template
            )

    output = pd.DataFrame.from_dict(output)

    output.to_csv(
        Path(__file__).resolve().parent / "bulk_annotation_source.tsv",
        index=False,
        sep="\t",
    )


def new_row(dataset_name: str) -> dict[str, str]:
    return {
        "dataset": dataset_name,
        "column": "n/a",
        "value": "n/a",
        "is_row": "n/a",
        "description": "n/a",
        "controlled_term": "n/a",
        "units": "n/a",
    }


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

    Skips columns in COLUMNS_TO_SKIP
    or columns that only contain "no" and "yes" values.
    """
    if column in COLUMNS_TO_SKIP:
        log.info(f"  column '{column}': skipping column")
        return output

    levels = {}
    if (
        participants_dict
        and participants_dict.get(column)
        and participants_dict[column].get("Levels")
    ):
        levels = participants_dict[column]["Levels"]
        output = append_levels(output, levels, column, row_template)

    if not is_categorical(participants[column]):
        log.info(f"  column '{column}': skipping non categorical column")
        log.info(f"  column '{column}': {participants[column].unique()}")
        return output

    actual_levels = []
    for x in participants[column].unique():
        if isinstance(x, str):
            if x.endswith(",") or x.endswith(", ") or x.endswith(" "):
                log.info(f"  column '{column}': cleaning level '{x}'")
            actual_levels.append(x.rstrip().rstrip(","))
        else:
            actual_levels.append(x)
    undefined_levels = set(actual_levels) - set(levels.keys())

    if len(undefined_levels) > MAX_NB_LEVELS:
        log.info(
            f"  column '{column}': skipping column with {len(undefined_levels)} levels"
        )
        return output

    log.info(f"  column '{column}': defined levels: {set(levels.keys())}")
    log.info(f"  column '{column}': undefined levels: {undefined_levels}")

    if is_yes_no(undefined_levels):
        log.info(f"  column '{column}': skipping yes/no column")
        return output

    output = append_levels(output, undefined_levels, column, row_template)

    return output


def is_yes_no(levels):
    return all(isinstance(x, str) and x.lower() in ["no", "yes", "nan"] for x in levels)


def is_categorical(series):
    if series.dtype == "float64":
        return False
    elif any(isinstance(x, (float)) for x in series.unique()):
        return False
    if series.dtype == "int64":
        return True
    elif all(isinstance(x, (int)) for x in series.unique()):
        return True
    elif is_yes_no(series):
        return True
    elif all(isinstance(x, (str)) for x in series.unique()):
        if all(re.match("([0-9]*[,]{0-1}[0-9]*)", x) for x in series.unique()):
            log.info(
                f"  series with comma instead of dot for decimal separator: {series}"
            )
            print("foo")
            return False
        if all(re.match("([- ]{0-1}[0-9]*)", x) for x in series.unique()):
            log.info(f"  series of int with n/a values: {series}")
            return False
    else:
        for x in series.unique():
            print(x)
        return True


def append_levels(
    output: pd.DataFrame, levels: set | dict, column: str, row_template: dict[str, str]
):
    for level_ in levels:
        if level_ in ("n/a", "nan"):
            log.info(f"  column '{column}': skipping level '{level_}'")
            continue

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
