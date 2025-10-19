# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

import re
from collections import defaultdict

from src.sdmxclgen.analyze_templates import GROUP_CODELISTS
from src.sdmxclgen.templates import AGENCY


def get_multiple_codelists_per_agency():
    """
    Analyzes the GROUP_CODELISTS dictionary, grouping codelists by agencies
    and identifying agencies that have more than one codelist within each group.

    Returns
    -------
    dict
        Dictionary of the form:
        {
            <group_id>: {
                <agency>: [<codelist_1>, <codelist_2>, ...],
                ...
            },
            ...
        }
        where:
        - group_id : str
            Group identifier in the GROUP_CODELISTS dictionary.
        - agency : str
            Agency name (extracted from the prefix).
        - [<codelist_1>, <codelist_2>, ...] : list
            List of codelists belonging to the agency.
            Included only if the agency has more than one codelist in the group.

    Notes
    -----
    1. Uses the global GROUP_CODELISTS dictionary, which contains information
       about groups and their codelists.
    2. For each codelist, `get_prefix_name_version(cl)` is called to determine the agency.
    3. If an agency has more than one codelist in a group, that agency-codelists pair
       is included in the result.

    Examples
    --------
    >>> result = get_multiple_codelists_per_agency()
    >>> for group_id, agencies in result.items():
    ...     print(group_id, agencies)
    """
    group_multiple_codelists = {}
    for group_id, group_data in GROUP_CODELISTS.items():
        codelists = group_data["codelists"]
        agency_dict = defaultdict(list)

        for cl in codelists:
            agency, _, cl_id, _, _ = get_prefix_name_version(cl)
            agency_dict[agency].append(cl)

        # Filter agencies with more than one codelist in the group
        multiple_codelists = {agency: cls for agency, cls in agency_dict.items() if len(cls) > 1}
        group_multiple_codelists[group_id] = multiple_codelists

    return group_multiple_codelists


def get_prefix_name_version(input_string):
    """
    Extracts the prefix (agency), name, and version from a codelist identifier string.

    Parameters
    ----------
    input_string : str
        String describing a codelist, usually formatted as:
        "<prefix>:SCL_<NAME>(<version>)" or "<prefix>:CL_<NAME>(<version>)".
        Example: "ESTAT:SCL_COVERAGE_POP(1.1.0)" or "ESTAT:CL_COVERAGE_POP(1.1.0)"

    Returns
    -------
    tuple
        (prefix, prefix_index, name, version, version_tuple):
        - prefix : str
            Prefix indicating the agency (e.g., 'ESTAT').
        - prefix_index : int
            Index of the prefix in the AGENCY list, or len(AGENCY) if not found.
        - name : str
            Codelist name (e.g., 'COVERAGE_POP').
        - version : str
            Codelist version as a string, e.g., '1.1.0'.
        - version_tuple : tuple
            Version converted into a tuple of integers, e.g., (1, 1, 0).

    Notes
    -----
    1. Regex looks for strings in the format: <prefix>:S?CL_<NAME>(<version>).
    2. If the format does not match expectations, an error message is printed and
       ((None, None, None), (len(AGENCY), (0,))) is returned.

    Examples
    --------
    >>> get_prefix_name_version("ESTAT:SCL_COVERAGE_POP(1.1.0)")
    ('ESTAT', 0, 'COVERAGE_POP', '1.1.0', (1, 1, 0))

    >>> get_prefix_name_version("ESTAT:CL_EMPLOYMENT_DATA(2.0)")
    ('ESTAT', 0, 'EMPLOYMENT_DATA', '2.0', (2, 0))
    """
    match = re.match(r"(.*?):S?CL_([A-Z_]+?)(?:\d+)?\(([^)]+)\)", input_string)
    if match:
        prefix = match.group(1)
        name = match.group(2)
        version = match.group(3)

        prefix_index = AGENCY.index(prefix) if prefix in AGENCY else len(AGENCY)
        version_tuple = tuple(map(int, version.split('.'))) if version else (0,)

        return prefix, prefix_index, name, version, version_tuple
    else:
        print(f"Error: Input string '{input_string}' does not match expected format.")
        return (None, None, None), (len(AGENCY), (0,))


def get_pref_ver_key(codelist_id):
    """
    Forms a tuple key (prefix_index, version_tuple) for use in sorting/comparisons.

    Parameters
    ----------
    codelist_id : str
        Full codelist identifier. Expected to be a string acceptable to `get_prefix_name_version`.

    Returns
    -------
    tuple
        Tuple (prefix_index, version_tuple). For example, (0, (1, 1, 0)).

    Notes
    -----
    1. Calling `get_prefix_name_version` extracts the indices and versions.
    2. The prefix_index value is based on the position of the agency in the AGENCY list.

    Examples
    --------
    >>> get_pref_ver_key("ESTAT:CL_COVERAGE_POP(1.1.0)")
    (0, (1, 1, 0))
    """
    _, prefix_index, _, _, version_tuple = get_prefix_name_version(codelist_id)
    return (prefix_index, version_tuple)
