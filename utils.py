import contextlib
import json
import warnings
from pathlib import Path

import pandas as pd

from heuristics import get_column_type


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


def new_row_template(
    dataset_name: str, nb_rows: int, include_levels: False
) -> dict[str, str | int | bool]:
    if include_levels:
        return {
            "dataset": dataset_name,
            "nb_rows": nb_rows,
            "column": "n/a",
            "type": "n/a",
            "nb_levels": 0,
            "value": "n/a",
            "is_row": "n/a",
            "description": "n/a",
            "controlled_term": "n/a",
            "units": "n/a",
            "term_url": "n/a",
        }
    return {
        "dataset": dataset_name,
        "nb_rows": nb_rows,
        "column": "n/a",
        "type": "n/a",
        "nb_levels": 0,
        "description": "n/a",
        "controlled_term": "n/a",
        "units": "n/a",
        "term_url": "n/a",
    }


def init_output(include_levels: bool = False) -> dict[str, list]:
    """Return a dict with keys corresponding to the columns of the output tsv."""
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
            "term_url": [],
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
            "units": [],
            "term_url": [],
        }


def exclude_datasets(dataset: pd.DataFrame):
    """Detect if the dataset should be excluded from further analysis."""
    return not dataset["has_mri"] or not dataset["has_participant_tsv"]


def get_participants_dict(dataset: pd.DataFrame, src_pth: Path):
    """Load participants.json if it exists."""
    participants_dict = {}
    if dataset["has_participant_json"]:
        participant_json = src_pth / dataset["name"] / "participants.json"
        with open(participant_json) as f:
            participants_dict = json.load(f)
    return participants_dict


def get_column_description(participants_dict, column):
    """Get the column description from participants.json \
        if the file and description exist."""
    if participants_dict and participants_dict.get(column):
        return participants_dict[column].get("Description", "n/a")
    return "n/a"


def get_column_unit(participants_dict, column):
    """Get the column unit from participants.json \
        if the file and unit description exist."""
    if participants_dict and participants_dict.get(column):
        return participants_dict[column].get("Unit", "n/a")
    return "n/a"


def get_column_term_url(participants_dict, column):
    """Get the column unit from participants.json \
        if the file and TermURL description exist."""
    if participants_dict and participants_dict.get(column):
        return participants_dict[column].get("TermURL", "n/a")
    return "n/a"


def update_row_with_column_info(
    this_row: dict,
    column: str,
    participants: pd.DataFrame,
    participants_dict: dict,
):
    this_row["column"] = column.strip()
    this_row["is_row"] = True
    if column == "participant_id":
        this_row["controlled_term"] = "nb:ParticipantID"
    this_row["description"] = get_column_description(participants_dict, column)
    this_row["unit"] = get_column_unit(participants_dict, column)
    this_row["term_url"] = get_column_term_url(participants_dict, column)
    this_row["type"] = get_column_type(participants[column])
    this_row["nb_levels"] = len(participants[column].unique())
    return this_row
