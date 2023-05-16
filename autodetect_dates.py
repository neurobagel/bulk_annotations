"""

from :
https://towardsdatascience.com/auto-detect-and-set-the-date-datetime-datatypes-when-reading-csv-into-pandas-261746095361
"""


import contextlib
import pandas as pd

def dt_inplace(df):
    """Automatically detect and convert (in place!) each dataframe column \
    of datatype 'object' to a datetime just 
    when ALL of its non-NaN values can be successfully parsed by pd.to_datetime().  
    
    Also returns a ref. to df for convenient use in an expression.
    """
    from pandas.errors import ParserError
    for c in df.columns[df.dtypes=='object']: # don't convert num
        with contextlib.suppress(ParserError, ValueError, TypeError):
            df[c]=pd.to_datetime(df[c])
    return df

def read_csv(*args, **kwargs):
    """Drop-in replacement for Pandas pd.read_csv. 
    
    It invokes pd.read_csv() (passing its arguments) 
    and then auto-matically detects and converts each column 
    whose datatype is 'object' to a datetime just when ALL of the column's
    non-NaN values can be successfully parsed by pd.to_datetime(),
    and returns the resulting dataframe.
    """
    return dt_inplace(pd.read_csv(*args, **kwargs))
