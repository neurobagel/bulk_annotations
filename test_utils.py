from pathlib import Path

import pytest

from utils import is_euro_format, is_yes_no, read_csv_autodetect_date


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
