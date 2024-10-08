# ----------------------------------------------------------------------------
# Copyright (C) 2021-2023 Deepchecks (https://www.deepchecks.com)
#
# This file is part of Deepchecks.
# Deepchecks is distributed under the terms of the GNU Affero General
# Public License (version 3 or later).
# You should have received a copy of the GNU Affero General Public License
# along with Deepchecks.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------
#
"""Module containing widget serializer for the pandas.DataFrame type."""

import typing as t

from deepchecks.core.serialization.abc import WidgetSerializer

from . import html

import pandas as pd
from ipywidgets import HTML
from pandas.io.formats.style import Styler

__all__ = ["DataFrameSerializer"]


DataFrameOrStyler = t.Union[pd.DataFrame, Styler]


class DataFrameSerializer(WidgetSerializer[DataFrameOrStyler]):
    """Serializes pandas.DataFrame instance into ipywidgets.Widget instance.

    Parameters
    ----------
    value : Union[pd.DataFrame, Styler]
        DataFrame instance that needed to be serialized.
    """

    def __init__(self, value: DataFrameOrStyler, **kwargs):
        if not isinstance(value, (pd.DataFrame, Styler)):
            raise TypeError(f'Expected "Union[DataFrame, Styler]" but got "{type(value).__name__}"')
        super().__init__(value=value)
        self._html_serializer = html.DataFrameSerializer(self.value)

    def serialize(self, **kwargs) -> HTML:
        """Serialize pandas.DataFrame instance into ipywidgets.Widget instance."""
        # Need this in order to create kernel see https://github.com/jupyter-widgets/ipywidgets/issues/3729
        import ipykernel.ipkernel  # pylint: disable=unused-import,import-outside-toplevel # noqa: F401

        return HTML(value=self._html_serializer.serialize())
