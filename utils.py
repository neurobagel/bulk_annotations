import contextlib
import logging
import re
from pathlib import Path
import json
import warnings

import pandas as pd
from rich.logging import RichHandler


def bulk_annotation_logger(log_level: str = "INFO"):
    FORMAT = "%(message)s"

    logging.basicConfig(
        level=log_level,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    return logging.getLogger("rich")


def output_dir() -> Path:
    return Path(__file__).parent / "outputs"


def dt_inplace(df: pd.DataFrame) -> pd.DataFrame:
    """Automatically detect and convert (in place!) each dataframe column \
    of datatype 'object' to a datetime just \
    when ALL of its non-NaN values can be successfully parsed by pd.to_datetime().

    Also returns a ref. to df for convenient use in an expression.

    from :
    https://towardsdatascience.com/auto-detect-and-set-the-date-datetime-datatypes-when-reading-csv-into-pandas-261746095361
    """
    from pandas.errors import ParserError

    for c in df.columns[df.dtypes == "object"]:  # don't convert num
        with contextlib.suppress(ParserError, ValueError, TypeError):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df[c] = pd.to_datetime(df[c])
    return df


def read_csv_autodetect_date(*args, **kwargs) -> pd.DataFrame:
    """Drop-in replacement for Pandas pd.read_csv.

    It invokes pd.read_csv() (passing its arguments)
    and then auto-matically detects and converts each column
    whose datatype is 'object' to a datetime just when ALL of the column's
    non-NaN values can be successfully parsed by pd.to_datetime(),
    and returns the resulting dataframe.

    from :
    https://towardsdatascience.com/auto-detect-and-set-the-date-datetime-datatypes-when-reading-csv-into-pandas-261746095361
    """
    return dt_inplace(pd.read_csv(*args, **kwargs))


def is_yes_no(levels: pd.Series) -> bool:
    """Return True if all levels are either 'yes' or 'no'.

    NaN are dropped before checking.
    """
    levels = levels.dropna()
    return all(
        isinstance(x, str) and x.lower() in ["no", "yes"]
        for x in levels.values
    )


def is_euro_format(levels: pd.Series) -> bool:
    """Return True if all values are numbers in with a comma as decimal separator."""
    levels = levels.dropna()
    return all(
        isinstance(x, str) and re.match("[-]?[ ]?[0-9]*,[0-9]*", x)
        for x in levels.unique()
    )

def new_row_template(dataset_name: str, nb_rows: int) -> dict[str, str | int | bool]:
    return {
        "dataset": dataset_name,
        "nb_rows": nb_rows,
        "column": "n/a",
        "type": "n/a",
        "nb_levels": 0,
        "description": "n/a",
        "controlled_term": "n/a",
    }

def init_output(include_levels: bool = False) -> dict[str, list]:
    if include_levels:
        return {
            "dataset": [],
            "nb_rows": [],
            "column": [],
            "value": [],
            "type": [],
            "nb_levels": [],
            "is_row": [],
            "description": [],
            "controlled_term": [],
            "units": [],
        }
    else:
        return {
            "dataset": [],
            "nb_rows": [],
            "column": [],
            "type": [],
            "nb_levels": [],
            "description": [],
            "controlled_term": [],
        }

def exclude_datasets(dataset: pd.Series):
    return (
            not dataset.has_mri.values[0]
            or not dataset.has_participant_tsv.values[0]
        )


def get_participants_dict(datasets, dataset_name, src_pth):
    mask = datasets.name == dataset_name
    participants_dict = {}
    if datasets[mask].has_participant_json.values[0]:
        participant_json = src_pth / dataset_name / "participants.json"
        with open(participant_json) as f:
            participants_dict = json.load(f)
    return participants_dict

def get_column_description(participants_dict, column):
    if participants_dict and participants_dict.get(column):
        return participants_dict[column].get("Description", "n/a")
    return "n/a"

def get_column_type(column: pd.Series):
    col_type = column.dtype
    if col_type == "object":
        if is_yes_no(column):
            col_type = "yes_no"
        elif is_euro_format(column):
            col_type = "nb:euro"
    return col_type

CONTROLLED_TERMS = {
    "participant_id": "nb:ParticipantID",
}

def update_row_with_column_info(this_row, column, participants, participants_dict):
    this_row["column"] = column
    this_row["is_row"] = True
    if column == "participant_id":
        this_row["controlled_term"] = "nb:ParticipantID"
    this_row["description"] = get_column_description(participants_dict, column)
    this_row["type"] = get_column_type(participants[column])
    this_row["nb_levels"] = len(participants[column].unique())
    return this_row