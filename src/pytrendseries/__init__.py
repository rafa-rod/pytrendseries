from . import version
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
    # plots
    plot_evolution,
    plot_drawdowns,
    plot_trend,
]
