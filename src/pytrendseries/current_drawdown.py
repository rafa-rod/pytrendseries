import numpy as np
import pandas as pd

from .detecttrend import _treat_parameters


def calculate_current_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the current drawdown from a DataFrame with datetime index
    and a single price column.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with datetime index and a single price column.

    Returns
    -------
    pd.DataFrame
        DataFrame with current_price, last_peak, current_drawdown,
        last_peak_date, and time_in_drawdown (number of records).

    Examples
    --------
    >>> dates = pd.date_range(start='2024-01-01', periods=10, freq='B')
    >>> prices = [100, 105, 103, 108, 106, 104, 107, 102, 100, 98]
    >>> df = pd.DataFrame({'price': prices}, index=dates)
    >>> result = calculate_current_drawdown(df)
    >>> print(result)
    """

    # Validations
    if df.empty:
        return _create_empty_result()

    _treat_parameters(df, trend="downtrend", limit=1, window=1)

    # Ensure data is sorted chronologically by index
    df_sorted: pd.DataFrame = df.sort_index()
    price_series: pd.Series = df_sorted.iloc[:, 0]  # Get the only available column

    # Current price (last available record)
    current_price: float = float(price_series.iloc[-1])
    current_date: pd.Timestamp = price_series.index[-1]

    # Last peak maximum and its date
    last_peak: float = float(price_series.max())
    last_peak_date: pd.Timestamp = price_series.idxmax()

    # Calculate drawdown in percentage
    if last_peak > 0:
        current_drawdown: float = (current_price / last_peak - 1) * 100
    else:
        current_drawdown: float = np.nan

    # Time in drawdown (number of records between peak and current price)
    # Counts actual records, not calendar days
    mask: pd.Series = (df_sorted.index > last_peak_date) & (
        df_sorted.index <= current_date
    )
    time_in_drawdown: int = len(df_sorted[mask])

    # Create and return DataFrame with results
    result_df: pd.DataFrame = pd.DataFrame(
        {
            "current_price": [current_price],
            "last_peak": [last_peak],
            "current_drawdown": [current_drawdown],
            "last_peak_date": [last_peak_date],
            "time_in_drawdown": [time_in_drawdown],
        }
    )

    return result_df


def _create_empty_result() -> pd.DataFrame:
    """
    Creates an empty result DataFrame with NaN values.

    Returns
    -------
    pd.DataFrame
        DataFrame with NaN/NaT values for all columns.
    """
    return pd.DataFrame(
        {
            "current_price": [np.nan],
            "last_peak": [np.nan],
            "current_drawdown": [np.nan],
            "last_peak_date": [pd.NaT],
            "time_in_drawdown": [np.nan],
        }
    )
