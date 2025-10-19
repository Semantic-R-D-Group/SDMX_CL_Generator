# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

import re
from collections import Counter


def analyze_groups(df_code_lists):
    """
    Analyzes a DataFrame containing information about code lists and returns grouping statistics.

    Parameters
    ----------
    df_code_lists : pandas.DataFrame
        DataFrame with expected columns:
        - "GroupType" (e.g., GROUP, SINGLE)
        - "SchemeID" (group scheme identifier)
        - "CodelistID"

    Returns
    -------
    tuple
        A tuple of four elements:
        (total_groups, total_codelists_in_groups, group_counts_dict, single_count), where:
        - total_groups : int
            Number of unique groups (GroupType == 'GROUP').
        - total_codelists_in_groups : int
            Total number of code lists across all groups (excluding SINGLE).
        - group_counts_dict : dict
            Dictionary of the form { SchemeID: count }, where count = number of CodelistID in the group.
        - single_count : int
            Total number of code lists in SINGLE categories.

    Notes
    -----
    1. Grouping is performed under the condition "GroupType == 'GROUP'".
    2. For SINGLE, the total number of CodelistID is counted.
    3. The groupby method groups the DataFrame by the SchemeID column.

    Examples
    --------
    >>> import pandas as pd
    >>> data = {
    ...     "GroupType": ["GROUP", "GROUP", "SINGLE", "GROUP"],
    ...     "SchemeID": ["SCH1", "SCH1", "SCH2", "SCH3"],
    ...     "CodelistID": ["CL1", "CL2", "CL3", "CL4"]
    ... }
    >>> df_code_lists = pd.DataFrame(data)
    >>> analyze_groups(df_code_lists)
    (2, 3, {'SCH1': 2, 'SCH3': 1}, 1)
    """
    group_counts = df_code_lists[df_code_lists["GroupType"] == "GROUP"].groupby("SchemeID")["CodelistID"].count()

    single_counts = df_code_lists[df_code_lists["GroupType"] == "SINGLE"]["CodelistID"].count()
    single_count = single_counts.sum()

    total_groups = group_counts.shape[0]
    total_codelists_in_groups = group_counts.sum()

    return total_groups, total_codelists_in_groups, group_counts.to_dict(), single_count


def evaluate_code_uniqueness(codelists, common_codes):
    """
    Calculates the total number of codes, the number of unique codes, and the ratio of unique codes
    (not included in the common_codes set) across all code lists.

    Parameters
    ----------
    codelists : dict
        Dictionary where the key is the codelist identifier,
        and the value is a dictionary with key "codes" containing a list of codes.
        Each code inside "codes" is represented as [codelist_id, agency, code_value, code_description].
    common_codes : set
        Set of "common" codes to exclude when calculating unique codes.

    Returns
    -------
    tuple
        (total_codes, unique_codes, uniqueness_ratio), where:
        - total_codes : int
            Total number of codes (excluding those in common_codes).
        - unique_codes : int
            Number of unique codes that occurred only once.
        - uniqueness_ratio : float
            Ratio of unique codes = unique_codes / total_codes.

    Examples
    --------
    >>> sample_codelists = {
    ...     "CL1": {"codes": [["CL1", "AG1", "CODE1", "desc1"], ["CL1", "AG1", "CODE2", "desc2"]]},
    ...     "CL2": {"codes": [["CL2", "AG2", "CODE2", "desc2"], ["CL2", "AG2", "CODE3", "desc3"]]}
    ... }
    >>> common_codes_set = {"COMMON1", "COMMON2"}
    >>> evaluate_code_uniqueness(sample_codelists, common_codes_set)
    (3, 2, 0.6666666666666666)
    """
    all_codes = []
    for codelist_id, data in codelists.items():
        if codelist_id is None:
            continue
        for entry in data["codes"]:
            # entry[2] — it`s a code
            if entry[2] in common_codes:
                continue
            all_codes.append(entry[2])

    code_counts = Counter(all_codes)

    total_codes = len(all_codes)
    unique_codes = sum(1 for count in code_counts.values() if count == 1)

    uniqueness_ratio = (unique_codes / total_codes) if total_codes > 0 else 0

    return total_codes, unique_codes, uniqueness_ratio


def common_codes_def(codelists):
    """
    Defines the overall set of codes (all_codes) and a set of typical codes (common_codes),
    including patterns like '_Z' and numbers from 1 to 10.

    Parameters
    ----------
    codelists : dict
        Dictionary where the key is the codelist identifier,
        and the value contains key 'codes' with lists [codelist_id, agency, code_value, code_description].

    Returns
    -------
    tuple
        (all_codes, common_codes), where:
        - all_codes : list
            List (not set) of all code values across all codelists.
        - common_codes : set
            Set of codes matching the format (e.g., '_Z') or
            being numbers from '1' to '10'.

    Examples
    --------
    >>> codelists_example = {
    ...     "CL1": {"codes": [["CL1", "AG1", "_A", "some desc"], ["CL1", "AG1", "5", "desc2"]]},
    ...     "CL2": {"codes": [["CL2", "AG2", "_B", "another desc"], ["CL2", "AG2", "XYZ", "desc3"]]}
    ... }
    >>> all_codes, common_codes = common_codes_def(codelists_example)
    >>> print(all_codes)
    ['_A', '5', '_B', 'XYZ']
    >>> print(common_codes)
    {'_A', '_B', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'}
    """
    all_codes = []
    for codelist_id, data in codelists.items():
        if codelist_id is None:
            continue
        for entry in data["codes"]:
            all_codes.append(entry[2])

    common_codes = set()

    # Find codes like '_\w' (e.g., '_Z')
    for code in all_codes:
        if re.fullmatch(r"_\w", code):
            common_codes.add(code)

    # Add numbers from 1 to 10
    common_codes.update(map(str, range(1, 11)))

    return all_codes, common_codes


def com_uniq_code(codelists, common_codes, unique_codes_count, codelist_id, code_set):
    """
    Determines for a given codelist (codelist_id) the set of codes, dividing them into:
    (1) "common" (common_code_set), (2) unique relative to other CLs (unique_codes_set),
    (3) intersecting codes.

    Parameters
    ----------
    codelists : dict
        All code lists, where key = codelist_id, and value = metadata with codes.
    common_codes : set
        Set of "common" codes (see common_codes_def).
    unique_codes_count : int
        Number of unique codes (used as a conditional "upper bound").
    codelist_id : str
        Current codelist being analyzed.
    code_set : set
        Set of codes belonging to codelist_id before removing "common" codes.

    Returns
    -------
    tuple
        (updated_code_set, common_code_set, unique_codes_set), where:
        - updated_code_set : set
            Set of codes for the current CL, already cleaned from "common".
        - common_code_set : set
            Codes that were marked as "common" and removed from code_set.
        - unique_codes_set : set
            Codes not appearing in other codelists (i.e., unique).

    Notes
    -----
    1. Remove from code_set all codes present in common_codes.
    2. Collect all codes from other codelists and compare to find truly unique codes.

    Examples
    --------
    >>> codelists_mock = {
    ...     "CL1": {
    ...         "codes": [
    ...             ["CL1", "AG1", "_A", "desc"],
    ...             ["CL1", "AG1", "CODE1", "desc"]
    ...         ]
    ...     },
    ...     "CL2": {
    ...         "codes": [
    ...             ["CL2", "AG2", "_B", "desc"],
    ...             ["CL2", "AG2", "CODE2", "desc"]
    ...         ]
    ...     }
    ... }
    >>> common_codes_set = {"_A", "_B"}
    >>> code_set_CL1 = {"_A", "CODE1"}
    >>> com_uniq_code(codelists_mock, common_codes_set, 100, "CL1", code_set_CL1)
    ({'CODE1'}, {'_A'}, {'CODE1'})
    """
    common_code_set = common_codes & code_set
    code_set = code_set - common_code_set

    other_codes_list = []
    for cl_id, ot_entry in codelists.items():
        if cl_id is None:
            continue
        if cl_id != codelist_id:
            for codes in ot_entry["codes"]:
                other_codes_list.append(codes[2])
    other_codes = set(other_codes_list)

    if len(other_codes) > unique_codes_count:
        print(f"{codelist_id}: ERROR! Total number of codes in other codelists = ", len(other_codes))

    unique_codes_set = set()
    for code in code_set:
        if code not in other_codes:
            unique_codes_set.add(code)

    return code_set, common_code_set, unique_codes_set


def tech_analisys(df_code_lists, df_codes, most_codelists_percent: int, most_frequent: int, n_times: int):
    """
    Performs several types of analysis on code lists based on provided DataFrames:
    1) Identifies the largest code lists (by percentage),
    2) Finds the most frequent codes,
    3) Finds "nonspecific" codes occurring more than a given threshold.

    Parameters
    ----------
    df_code_lists : pandas.DataFrame
        Table containing columns, including 'Total Codes' for each codelist (CodelistID).
    df_codes : pandas.DataFrame
        Table with all codes. Expected column 'Code' — the code value.
    most_codelists_percent : int
        Number (in range 1..100) defining what percentage of the largest code lists to output.
    most_frequent : int
        Number of most frequent codes to output.
    n_times : int
        Threshold for "nonspecific" codes. Codes occurring more than n_times and meeting the criteria are output.

    Returns
    -------
    None
        The function prints analysis results to the console without returning a value.

    Notes
    -----
    1. "Largest code lists" are determined by 'Total Codes' (see df_code_lists).
    2. "Most frequent codes" — by frequency in column 'Code' (df_codes).
    3. "Nonspecific" codes are defined as either numeric (code.isdigit()) or starting with '_' and containing uppercase letters (e.g., '_A').

    Examples
    --------
    >>> # Assume we have two DataFrames: df_code_lists and df_codes.
    >>> tech_analisys(df_code_lists, df_codes, 20, 5, 10)
    >>> # Will print top 20% of the largest code lists, 5 most frequent codes,
    >>> # and nonspecific codes occurring more than 10 times.
    """
    if most_codelists_percent in range(1, 101):
        top_percent_codelists = df_code_lists.nlargest(
            int(len(df_code_lists) * most_codelists_percent / 100),
            'Total Codes'
        )
        if most_codelists_percent == 100:
            print("\nCode lists:")
        else:
            print(f"\n{most_codelists_percent}% of the largest code lists:")
        print(top_percent_codelists[['CodelistID', 'Total Codes']])

    if most_frequent > 0:
        most_frequent_top = df_codes['Code'].value_counts().head(most_frequent)
        print(f"\n{most_frequent} most frequent codes:")
        print(most_frequent_top.to_string(index=True, header=False))

    # Helper function for nonspecific check
    def is_nonspecific(code):
        return (
            isinstance(code, str)
            and (code.isdigit() or (code.startswith('_') and any(c.isupper() for c in code[1:])))
        )

    df_codes['Code'] = df_codes['Code'].fillna('')   # Replace NaN with empty string
    nonspecific_codes_series = df_codes[df_codes['Code'].apply(is_nonspecific)]['Code'].value_counts()

    # Keep only codes occurring more than n_times
    nonspecific_codes_series = nonspecific_codes_series[nonspecific_codes_series > n_times]

    if len(nonspecific_codes_series) > 0:
        print(f"\nNonspecific codes (count: {len(nonspecific_codes_series)}, occurrences > {n_times}):")
        print(nonspecific_codes_series.to_string(index=True, header=False))
    else:
        print(f"\nNo nonspecific codes with occurrences > {n_times}")
