from pathlib import Path

import pytest

from heuristics import (
    get_column_type,
    is_euro_format,
    is_participant_id,
    is_sex,
    is_yes_no,
)
from utils import read_csv_autodetect_date


@pytest.fixture
def input_tsv():
    return Path(__file__).parent / "tests" / "data" / "participants.tsv"


def test_read_csv(input_tsv):
    df = read_csv_autodetect_date(input_tsv, sep="\t")
    assert df.acq_date.dtype == "datetime64[ns]"


def test_is_yes_no(input_tsv):
    df = read_csv_autodetect_date(input_tsv, sep="\t")

    assert ~is_yes_no(df["acq_date"])
    assert is_yes_no(df["yes_no_nan"])


def test_is_euro_format(input_tsv):
    df = read_csv_autodetect_date(input_tsv, sep="\t")

    assert ~is_euro_format(df["acq_date"])
    assert ~is_euro_format(df["participant_id"])
    assert ~is_euro_format(df["age"])
    assert ~is_euro_format(df["height"])
    assert is_euro_format(df["euro_format"])


def test_get_column_type(input_tsv):
    df = read_csv_autodetect_date(input_tsv, sep="\t")

    assert get_column_type(df["participant_id"]) == "object"
    assert get_column_type(df["sex"]) == "object"
    assert get_column_type(df["euro_format"]) == "nb:euro"
    assert get_column_type(df["age (years)"]) == "int64"
    assert get_column_type(df["acq_date"]) == "datetime64[ns]"
    assert get_column_type(df["height"]) == "float64"
    assert get_column_type(df["bounded"]) == "nb:bounded"
    assert get_column_type(df["yes_no_nan"]) == "yes_no"
    assert get_column_type(df["ranged"]) == "nb:range"
    assert get_column_type(df["is_int"]) == "int"


def test_is_sex():
    assert is_sex("sex")


def test_is_participant_id(input_tsv):
    df = read_csv_autodetect_date(input_tsv, sep="\t")
    assert is_participant_id(df, "participant_id")
    assert not is_participant_id(df, "acq_date")
