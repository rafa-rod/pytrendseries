# -*- coding: utf-8 -*-

import importlib

import pytrendseries


def test_all_entries_are_strings_and_exist():
    for name in pytrendseries.__all__:
        assert isinstance(name, str)
        assert hasattr(pytrendseries, name)


def test_star_import():
    namespace = {}
    exec("from pytrendseries import *", namespace)
    for name in ("detecttrend", "maxdrawdown", "plot_evolution", "plot_drawdowns", "plot_trend"):
        assert name in namespace


def test_version_matches_package_metadata():
    from importlib.metadata import version

    assert pytrendseries.__version__ == version("pytrendseries")
    assert importlib.import_module("pytrendseries.version").__version__ == pytrendseries.__version__
