"""String mismatch functions."""
from typing import Union, Iterable

import pandas as pd

from mlchecks import CheckResult, Dataset, ensure_dataframe_type, CompareDatasetsBaseCheck
from mlchecks.base.dataframe_utils import filter_columns_with_validation
from mlchecks.base.string_utils import get_base_form_to_variants_dict, is_string_column

__all__ = ['string_mismatch_comparison', 'StringMismatchComparison']


def percentage_in_series(series, values):
    count = sum(series.isin(values))
    return f'{count / series.size:.2%} ({count})'


def string_mismatch_comparison(dataset: Union[pd.DataFrame, Dataset],
                               baseline_dataset: Union[pd.DataFrame, Dataset],
                               columns: Union[str, Iterable[str]] = None,
                               ignore_columns: Union[str, Iterable[str]] = None) -> CheckResult:
    """Detect different variants of string categories between the same categorical column in two datasets.

    This check compares the same categorical column within a dataset and baseline and checks whether there are variants
    of similar strings that exists only in dataset and not in baseline.
    Specifically, we define similarity between strings if they are equal when ignoring case and non-letter characters.
    Example:
    We have a baseline dataset with similar strings 'string' and 'St. Ring', which have different meanings.
    Our tested dataset has the strings 'string', 'St. Ring' and a new phrase, 'st.  ring'.
    Here, we have a new variant of the above strings, and would like to be acknowledged, as this is obviously a
    different version of 'St. Ring'.

    Args:
        dataset (Union[pd.DataFrame, Dataset]): A dataset or pd.FataFrame object.
        baseline_dataset (Union[pd.DataFrame, Dataset]): A dataset or pd.FataFrame object.
        columns (Union[str, Iterable[str]]): Columns to check, if none are given checks all columns except ignored ones.
        ignore_columns (Union[str, Iterable[str]]): Columns to ignore, if none given checks based on columns variable
    """
    # Validate parameters
    df: pd.DataFrame = ensure_dataframe_type(dataset)
    df = filter_columns_with_validation(df, columns, ignore_columns)
    baseline_df: pd.DataFrame = ensure_dataframe_type(baseline_dataset)

    mismatches = []

    # Get shared columns
    columns = set(df.columns).intersection(baseline_df.columns)

    for column_name in columns:
        tested_column: pd.Series = dataset[column_name]
        baseline_column: pd.Series = baseline_df[column_name]
        # If one of the columns isn't string type, continue
        if not is_string_column(tested_column) or not is_string_column(baseline_column):
            continue

        tested_baseforms = get_base_form_to_variants_dict(tested_column.unique())
        baseline_baseforms = get_base_form_to_variants_dict(baseline_column.unique())

        common_baseforms = set(tested_baseforms.keys()).intersection(baseline_baseforms.keys())
        for baseform in common_baseforms:
            tested_values = tested_baseforms[baseform]
            baseline_values = baseline_baseforms[baseform]
            # If at least one unique value in tested dataset, add the column to results
            if len(tested_values - baseline_values) > 0:
                # Calculate all values to be shown
                variants_only_in_dataset = tested_values - baseline_values
                variants_only_in_baseline = baseline_values - tested_values
                common_variants = tested_values & baseline_values
                percent_variants_only_in_dataset = percentage_in_series(tested_column, variants_only_in_dataset)
                percent_variants_in_baseline = percentage_in_series(baseline_column, variants_only_in_baseline)

                mismatches.append([column_name, baseform, common_variants,
                                   variants_only_in_dataset, percent_variants_only_in_dataset,
                                   variants_only_in_baseline, percent_variants_in_baseline])

    # Create result dataframe
    df_graph = pd.DataFrame(mismatches,
                            columns=['Column name', 'Base form', 'Common variants', 'Variants only in dataset',
                                     '% Unique variants out of all dataset samples (count)',
                                     'Variants only in baseline',
                                     '% Unique variants out of all baseline samples (count)'])
    df_graph = df_graph.set_index(['Column name', 'Base form'])
    # For display transpose the dataframe
    display = df_graph.T if len(df_graph) > 0 else None

    return CheckResult(df_graph, check=string_mismatch_comparison, display=display)


class StringMismatchComparison(CompareDatasetsBaseCheck):
    """Detect different variants of string categories between the same categorical column in two datasets."""

    def run(self, dataset, baseline_dataset, model=None) -> CheckResult:
        """Run string_mismatch_comparison check.

        Args:
            dataset (Dataset): A dataset object.
            baseline_dataset (Dataset): A dataset object.
            model: Not used in this check.
        """
        return string_mismatch_comparison(dataset,
                                          baseline_dataset,
                                          columns=self.params.get('columns'),
                                          ignore_columns=self.params.get('ignore_columns'))