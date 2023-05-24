"""Contains code and constants to detect certain column "type" participants.tsv.

Constants can either be either for neurobagel terms or
variables that are under different names but probably mean the same thing.


"""

import re

import pandas as pd

NEUROBAGEL = {
    "nb:ParticipantID": ("participant"),
    "nb:SessionID": ("session", "session_id"),
    "nb:Sex": (
        "gender",
        "gender_f",
        "gender_identity_f",
        "gender_identity_m",
        "jsex",
        "rat_sex",
        "sex",
    ),
    # TODO: check if this does not not lead
    # to more than one column being being flagged as nb:Age
    "nb:Age": (
        "age",
        "age (years)",
        "age_at_first_scan_years",
        "ageAtFirstScanYears",
        "age (5-year bins)",
        "age (years)",
        "age at baseline ",
        "age at onset first cb use",
        "age at onset frequent cb use",
        "age_at_first_scan_years",
        "age_exam_ses01",
        "age_group",
        "age_ses-t1",
        "age_ses-t1_aanonword_run-01",
        "age_ses-t1_aanonword_run-02",
        "age_ses-t1_aaword_run-01",
        "age_ses-t1_aaword_run-02",
        "age_ses-t1_avnonword_run-01",
        "age_ses-t1_avnonword_run-02",
        "age_ses-t1_avword_run-01",
        "age_ses-t1_avword_run-02",
        "age_ses-t1_dwi",
        "age_ses-t1_phenotype",
        "age_ses-t1_t1w",
        "age_ses-t1_vvnonword_run-01",
        "age_ses-t1_vvnonword_run-02",
        "age_ses-t1_vvword_run-01",
        "age_ses-t1_vvword_run-02",
        "age_ses-t2",
        "age_ses-t2_phenotype",
        "age_ses-t2_t1w",
        "age_ses-t2_vvnonword_run-01",
        "age_ses-t2_vvnonword_run-02",
        "age_ses-t2_vvword_run-01",
        "age_ses-t2_vvword_run-02",
        "age_ses02",
        "age_sess1",
        "age_sess2",
        "ageatfirstscanyears",
        "agegroup",
        "rat_age",
    ),
    "handedness": (
        "ehi",
        "edinburgh",
        "edinburgh_hand_l",
        "edinburgh_hand_r",
        "edinburgh_handedness",
        "edinburgh_lq",
        "hand",
        "handedness",
    ),
    "nb:Diagnosis": ("diagnosis"),
    "purl:NCIT_C94342": ("healthy_control"),
    "nb:Assessment": ("assessment_tool"),
}

# the following is more manually curated to avoid indexing
# the labels of columns that should not be.
COLUMNS_TO_SKIP = {
    "a_date",
    "birthdate_shifted",
    "dataset_id",
    "date",
    "date_of_scan",
    "date_run",
    "dob",
    "ftcd-fmri-delay-days",
    "guid",
    "height",
    "height_in",
    "height_ft",
    "height_inches",
    "height (cm)",
    "hf (/min)",
    "scan_time",
    "time",
    "time_after_stroke",
    "weight",
    "weight (lbs)",
    "weight (kg)",
    "years_of_education",
}

MAX_NB_LEVELS = 15


def skip_column(this_row: dict) -> bool:
    """Return True if column should be skipped.

    The value returned depends on:
    - the column name,
    - its controlled term,
    - its type,
    - the number of levels it has.
    """
    return (
        this_row["column"].lower() in COLUMNS_TO_SKIP
        or this_row["controlled_term"] in ["nb:ParticipantID", "nb:Age"]
        or this_row["type"]
        in {
            "datetime64[ns]",
            "float64",
            "int64",
            "yes_no",
            "bool",
            "int",
            "float",
            "nb:range",
            "nb:bounded",
            "nb:euro",
        }
        or this_row["nb_levels"] > MAX_NB_LEVELS
    )


def get_column_type(col: pd.Series):
    """Return column type.

    Will run most of the heuristics to detect the column type.
    """
    col_type = str(col.dtype)
    if col_type in {"object", "n/a"}:
        if is_yes_no(col):
            col_type = "yes_no"
        elif is_euro_format(col):
            col_type = "nb:euro"
        elif is_int(col):
            col_type = "int"
        elif is_float(col):
            col_type = "float"
        elif is_bounded(col):
            col_type = "nb:bounded"
        elif is_range(col):
            col_type = "nb:range"
        elif is_age_with_Y(col):
            col_type = "ageY"
    return col_type


def is_yes_no(col: pd.Series) -> bool:
    """Return True for 'binary' columns.

    NaN are dropped before checking.
    """
    col = col.dropna()
    return (
        all(
            isinstance(x, str)
            and x.strip().lower() in ["no", "yes", "y", "n", "0", "1"]
            for x in col.unique()
        )
        or all(isinstance(x, int) and x in [0, 1] for x in col.unique())
        or all(isinstance(x, float) and x in [0.0, 1.0] for x in col.unique())
    )


def is_euro_format(col: pd.Series) -> bool:
    """Return True if all values are floats  with a comma as decimal separator.

    NaN are dropped before checking.
    """
    col = col.dropna()
    return all(
        isinstance(x, str) and re.match("[- 0-9,]*", x.strip())
        for x in col.unique()
    ) and any(
        re.match("[-]?[ ]?[0-9]*,[0-9]*", x.strip()) for x in col.unique()
    )


def is_age_with_Y(col: pd.Series) -> bool:
    col = col.dropna()
    return all(
        isinstance(x, str) and re.match("^[0-9]+Y$", x.strip())
        for x in col.unique()
    )


def is_bounded(col: pd.Series) -> bool:
    """Return true if the values are floats with at least one value that ends with +.

    NaN are dropped before checking.
    """
    col = col.dropna()
    return all(
        isinstance(x, str) and re.match("[+0-9.]*", x.strip())
        for x in col.unique()
    ) and any(re.match("[0-9]*[.]?[0-9]*[+]", x.strip()) for x in col.unique())


def is_range(col: pd.Series) -> bool:
    """Return true if the values are integers \
    with at least one value that where 2 integers are separated by a dash.

    NaN are dropped before checking.
    """
    col = col.dropna()
    return all(
        isinstance(x, str) and re.match("[-0-9]*", x.strip())
        for x in col.unique()
    ) and any(re.match("[0-9]+-[0-9]+", x.strip()) for x in col.unique())


def is_participant_id(df: pd.DataFrame, column: str) -> bool:
    """Return True if column is a participant_id column.

    NaN are dropped before checking.
    """
    if column.strip().lower() != "participant_id":
        return False
    levels = df[column]
    levels = levels.dropna()
    return levels.dtype in ["object", "n/a"] and all(
        isinstance(x, str) and re.match("^sub-[a-zA-Z0-9]*", x.strip())
        for x in levels.unique()
    )


def is_age(this_row: dict):
    if this_row["column"].lower() not in NEUROBAGEL["nb:Age"]:
        return False
    if this_row["column"] in [
        "float64",
        "int64",
        "int",
        "float",
        "nb:bounded",
        "nb:euro",
        "ageY",
    ]:
        return True


def is_sex(column: str):
    if column.strip().lower() in NEUROBAGEL["nb:Sex"]:
        return True


def is_int(levels):
    """Return true if the values are integers or strings that are integers.

    Will also return true if the values just either a dot or a dash.
    """
    levels = levels.dropna()
    return all(isinstance(x, (int)) for x in levels.unique()) or all(
        isinstance(x, (str)) and re.match("^[0-9]*$|^[.-]{1}$", x.strip())
        for x in levels.unique()
    )


def is_float(levels):
    levels = levels.dropna()
    return all(isinstance(x, (float)) for x in levels.unique())
