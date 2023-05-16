import contextlib
import logging
import re
from pathlib import Path

import pandas as pd
from rich.logging import RichHandler


def bulk_annotation_logger(log_level: str = "INFO"):
    FORMAT = "%(message)s"

    logging.basicConfig(level=log_level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

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
            df[c] = pd.to_datetime(df[c])
    return df


def read_csv(*args, **kwargs) -> pd.DataFrame:
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
    return all(isinstance(x, str) and x.lower() in ["no", "yes"] for x in levels.values)


def is_euro_format(levels: pd.Series) -> bool:
    """Return True if all values are numbers in with a comma as decimal separator."""
    levels = levels.dropna()
    return all(isinstance(x, str) and re.match("[-]?[ ]?[0-9]*,[0-9]*", x) for x in levels.unique())
