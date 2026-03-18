from . import version
from .current_drawdown import calculate_current_drawdown
from .detecttrend import detecttrend
from .maximum_drawdown import maxdrawdown
from .time_under_water import calculate_time_under_water
from .vizplot import plot_drawdowns, plot_evolution, plot_trend

__version__ = version.__version__
__author__ = "Rafael Rodrigues, rafael.rafarod@gmail.com"

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Trend
    "detecttrend",
    "get_trends_labels",
    # maxdd and tuw
    "maxdrawdown",
    "calculate_time_under_water",
    "calculate_current_drawdown",
    # plots
    plot_evolution,
    plot_drawdowns,
    plot_trend,
]
