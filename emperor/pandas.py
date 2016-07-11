r"""
Pandas Interface for Emperor
============================

This module provides a simple interface to visualize a Pandas DataFrame using
the Emperor.

.. currentmodule:: emperor.pandas

Functions
---------
.. autosummary::
    :toctree: generated/

    scatterplot
"""
# ----------------------------------------------------------------------------
# Copyright (c) 2013--, emperor development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.md, distributed with this software.
# ----------------------------------------------------------------------------
from __future__ import division

import numpy as np
import pandas as pd

from emperor.core import Emperor
from skbio import OrdinationResults


def scatterplot(df, x=None, y=None, z=None, remote=True):
    """Create an Emperor scatter plot from a Pandas DataFrame

    Parameters
    ----------
    df : pd.DataFrame
        Pandas DataFrame with the data to display
    x, y, z : str
        Column names in `df`, these will represent the order of the axes in the
        final visualization.
    remote : bool
        Whether the JavaScript resources should be loaded locally or from
        GitHub

    Raises
    ------
    ValueError
        If `df` is not a PandasDataFrame
        If `x`, `y` or `z` are missing from `df` or if they are not numeric
        columns.
        If after removing rows with missing data there are fewer than 3
        samples.

    Notes
    -----
    If a row has missing data, that data pont will be removed from the
    visualization.

    See Also
    --------
    emperor.core.Emperor
    """

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The argument is not a Pandas DataFrame")

    for col in [z, y, x]:
        if col is None:
            continue

        if col not in df.columns:
            raise ValueError("'%s' is not a column in the DataFrame" % col)

        if not np.issubdtype(df[col].dtype, np.number):
            raise ValueError("'%s' is not a numeric column" % col)

    # remove NAs
    samples = df.select_dtypes(include=[np.number]).copy()
    samples.dropna(axis=0, how='any', inplace=True)

    if len(samples) < 3:
        raise ValueError("Not enough rows without missing data")

    # sort columns by variance
    variance = samples.var().sort_values(ascending=False)
    samples = samples[variance.index].copy()

    # re-order x, y and z
    ordered = samples.columns.tolist()
    for col in [z, y, x]:
        if col is not None:
            ordered.remove(col)
            ordered = [col] + ordered
    samples = samples[ordered].copy()

    # match up the metadata and coordinates
    df = df.loc[samples.index].copy()

    ores = OrdinationResults(short_method_name='Ax', long_method_name='Axis',
                             eigvals=np.zeros_like(samples.columns),
                             samples=samples, proportion_explained=variance)

    df.index.name = '#SampleID'

    # HACK: scale the position of the samples to fit better within the screen
    ores.samples = ores.samples / ores.samples.max(axis=0)

    return Emperor(ores, df, dimensions=8, remote=remote)
