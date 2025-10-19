# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

# analyze_sdmx_cl.py
import os
import pandas as pd
from .parse_save_cl import parse_codelist_v3, save_codelist_data
from .analyze_func import tech_analisys, evaluate_code_uniqueness, analyze_groups
from .get_analyze_func import get_prefix_name_version, get_pref_ver_key
from .analyze_templates import SINGLE_CODELISTS, GROUP_CODELISTS
from .get_funcs import get_singles_template, get_scheme_id
from .gen_template import SINGLES
from .download_xml_gr_cl import urn_to_sdmx_url


def cl_analysis(codelist_folder, all_cl_data_csv, cl_table_csv, filtered_cl_data_csv, filtered_cl_table_csv):
    """
     Main function for loading, analyzing, and filtering codelists,
     represented as SDMX XML files.

     Parameters
     ----------
     codelist_folder : str
         Path to the directory containing XML files of codelists.
     all_cl_data_csv : str
         Path to a CSV file where detailed data about all codes (unfiltered) will be saved.
     cl_table_csv : str
         Path to a CSV file with summary information about codelists (unfiltered).
     filtered_cl_data_csv : str
         Path to a CSV file where detailed data about codes after filtering will be saved.
     filtered_cl_table_csv : str
         Path to a CSV file with summary information about codelists after filtering.

     Returns
     -------
     bool
         Returns True upon completion if the script executes without critical errors.

     Notes
     -----
     1. The function recursively scans the directory `codelist_folder` for XML files.
        For each file, `parse_codelist_v3` is called to extract the codelist structure.
     2. Data is collected into the dictionary `codelists_data`, after which `save_codelist_data`
        is invoked to form two main DataFrames:
         - df_code_lists: metadata about codelists (summary table).
         - df_codes: detailed data for each code.
     3. During processing:
        - "Similar" codelists are identified (having the same name but different versions).
        - Certain codelists are excluded according to SINGLE_CODELISTS and GROUP_CODELISTS,
          as well as codelists in which all codes are "unique" (do not overlap with others).
        - Additional technical analysis is performed through `tech_analisys`.
        - The number of codes, share of unique ones, etc., are calculated via `evaluate_code_uniqueness`.
     4. As a result, the following files are created:
        - Full list of codelists (all_cl_data_csv, cl_table_csv).
        - Filtered list of codelists (filtered_cl_data_csv, filtered_cl_table_csv).
        - Data on group and single codelists is updated, using `analyze_groups`.

     Examples
     --------
     >>> cl_analysis(
     ...     "path/to/xml_folder",
     ...     "all_codes.csv",
     ...     "all_codelists.csv",
     ...     "filtered_codes.csv",
     ...     "filtered_codelists.csv"
     ... )
     # After execution, analysis results will be printed to the console,
     # and the CSV files will contain the corresponding tables.
     """
    # 1. Build dictionary of CL with codes from XML files
    codelists_data = {}
    for filename in os.listdir(codelist_folder):
        xml_path = os.path.join(codelist_folder, filename)
        if xml_path.endswith(".xml"):
            try:
                (codelist_id,
                 codelist_name,
                 agency,
                 cl_id,
                 ver,
                 codelist_description,
                 urn,
                 codes) = parse_codelist_v3(xml_path)

                url = urn_to_sdmx_url(urn)
                if codelist_id and codes:
                    codelists_data[codelist_id] = {
                        "name": codelist_name,
                        "agency": agency,
                        "clid": cl_id,
                        "ver": ver,
                        "description": codelist_description,
                        "codes": codes,
                        "simcl": "",
                        "url": url
                    }
            except Exception as e:
                print(f"Error while processing {xml_path}: {e}")
                continue

    print("Codelists successfully loaded. Starting table generation.\n")

    # Identify "similar" codelists (same name, different version)
    codelist_names = {cl_id: get_prefix_name_version(cl_id)[2] for cl_id in codelists_data.keys()}
    for codelist_id, data in codelists_data.items():
        extracted_name = get_prefix_name_version(codelist_id)[2]
        if extracted_name is None:
            data["simcl"] = None
            continue
        similar = [
            clid for clid, clname in codelist_names.items()
            if clid != codelist_id and clname == extracted_name
        ]
        if similar:
            similar.append(codelist_id)
            similar = sorted(similar, key=get_pref_ver_key)
        data["simcl"] = similar if similar else None

    # Print lists of similar codelists
    unique_simcl_set = set()
    for data in codelists_data.values():
        if data["simcl"] is not None:
            unique_simcl_set.add(tuple(data["simcl"]))

    unique_simcl_lists = [list(simcl_set) for simcl_set in unique_simcl_set]
    print("Similar CL lists:")
    for idx, simcl_list in enumerate(sorted(unique_simcl_lists), 1):
        print(f"{idx}. {simcl_list}")

    # Save data to CSV
    common_codes, df_code_lists, df_codes = save_codelist_data(codelists_data, all_cl_data_csv, cl_table_csv)
    print("------------------------------------------------")

    # 2. Technical analysis
    print("\n1. Technical analysis of initial codelist tables")
    tech_analisys(df_code_lists, df_codes, 10, 20, 4)
    print("------------------------------------------------")

    # 3. Exclude group and unique codelists
    print("\n2. Excluding group and unique codelists from analysis")

    group_codelists = []
    group_codelists_dict = {}
    for group_id, group in GROUP_CODELISTS.items():
        if "codelists" in group:
            codelists = group["codelists"]
            if len(codelists) > len(set(codelists)):
                print(f"Duplicate names in {group_id}")
            uniq_codelists = list(set(codelists))
            group_codelists.extend(uniq_codelists)
            group_codelists_dict[group_id] = uniq_codelists

    single_codelists = []
    dubl_single_codelists = []
    for single_codelist in SINGLE_CODELISTS:
        if len(single_codelists) == 0:
            single_codelists.append(single_codelist)
        else:
            if single_codelist in single_codelists:
                dubl_single_codelists.append(single_codelist)
            else:
                single_codelists.append(single_codelist)
    if len(dubl_single_codelists) > 0:
        print("Duplicates found in SINGLE_CODELISTS:")
        for dublicate in dubl_single_codelists:
            print(dublicate)

    excluded_codelists = single_codelists + group_codelists
    print("Excluded codelists from SINGLE_CODELISTS:", len(single_codelists))
    print("Excluded codelists from GROUP_CODELISTS:", len(group_codelists))
    print("\nAutomatically excluding codelists with unique codes")

    df_filtered_code_lists = []
    total_filtered_codelists = []
    while True:
        # Find codelists with 'Shared Codes' == 0
        if len(df_filtered_code_lists) == 0:
            filtered_codelists = df_code_lists[df_code_lists['Shared Codes'] == 0]['CodelistID'].tolist()
        else:
            filtered_codelists = df_filtered_code_lists[df_filtered_code_lists['Shared Codes'] == 0]['CodelistID'].tolist()

        # Exclude already excluded
        f_cl = set(filtered_codelists) - set(excluded_codelists)
        if len(f_cl) == 0:
            break

        print(f"\nExcluding codelists ({len(f_cl)})")
        excluded_codelists = list(set(excluded_codelists + filtered_codelists))

        # Create new dictionary without excluded codelists
        filtered_codelists_data = {}
        for codelist_id, data in codelists_data.items():
            if codelist_id is None or codelist_id in excluded_codelists:
                continue
            filtered_codelists_data[codelist_id] = data

        filtered_common_codes, df_filtered_code_lists, df_filtered_codes = save_codelist_data(
            filtered_codelists_data,
            filtered_cl_data_csv,
            filtered_cl_table_csv,
            save_flag=False
        )

    total_filtered_codelists = excluded_codelists.copy()
    for item in single_codelists + group_codelists:
        if item in total_filtered_codelists:
            total_filtered_codelists.remove(item)

    if len(total_filtered_codelists) > 0:
        print(f"\nAutomatically excluded codelists with unique codes ({len(total_filtered_codelists)}):")
        total_filtered_codelists.sort()
        for f_codelist in total_filtered_codelists:
            print(f_codelist)

    print(f"\nTotal excluded codelists - ({len(excluded_codelists)})")
    excluded_codelists.sort()
    print("------------------------------------------------")

    # Count remaining codelists
    cl_count = len(codelists_data) - len(excluded_codelists)
    print(f"\n3. Technical analysis (unlabeled codelists - {cl_count})")

    # Update GroupType and SchemeID fields in df_code_lists for group and single CL
    for group_id, codelists in group_codelists_dict.items():
        for codelist_id in codelists:
            df_code_lists.loc[df_code_lists['CodelistID'] == codelist_id, 'GroupType'] = "GROUP"
            df_code_lists.loc[df_code_lists['CodelistID'] == codelist_id, 'SchemeID'] = str(group_id)
    for codelist_id in (set(excluded_codelists) - set(group_codelists)):
        df_code_lists.loc[df_code_lists['CodelistID'] == codelist_id, 'GroupType'] = "SINGLE"
        for short_name, value in SINGLES.items():
            if value["codelist"] == codelist_id:
                df_code_lists.loc[df_code_lists['CodelistID'] == codelist_id, 'SchemeID'] = str(short_name)

    df_code_lists.to_csv(cl_table_csv, index=False, sep=";")
    df_code_lists = pd.read_csv(cl_table_csv, sep=";")
    print(f"\nnFile {cl_table_csv} successfully saved.")

    # Check for missing values
    print(f"\nNumber of missing values in {cl_table_csv}:")
    missing_values_code_lists = df_code_lists.isnull().sum()
    missing_values_code_lists = missing_values_code_lists[missing_values_code_lists > 0]
    if not missing_values_code_lists.empty:
        print(missing_values_code_lists.to_string(index=True, header=False))
    else:
        print("No missing values")

    if cl_count <= 0:
        print("\nAll codelists labeled")
    else:
        # Additional analysis for remaining codelists
        if cl_count > 6:
            most_cl_percent = 50
        else:
            most_cl_percent = 100

        tech_analisys(df_filtered_code_lists, df_filtered_codes, most_cl_percent, 50, 1)

        total_codes, unique_codes, uniqueness_ratio = evaluate_code_uniqueness(filtered_codelists_data, filtered_common_codes)
        print(f"\nTotal codes - {total_codes}, non-repeated - {unique_codes} ({int(uniqueness_ratio * 100)}%)")

        # Save filtering results
        df_filtered_codes.to_csv(filtered_cl_data_csv, index=False, sep=";")
        df_filtered_code_lists.to_csv(filtered_cl_table_csv, index=False, sep=";")

        print(f"\nnFiles {cl_table_csv}, {filtered_cl_data_csv} and {filtered_cl_table_csv} successfully saved.")

    # Generate additional data for SINGLE_CODELISTS
    get_singles_template(df_code_lists)

    # Analyze groups and single codelists
    total_groups, total_cl_in_groups, group_counts_dict, single_count = analyze_groups(df_code_lists)
    print(f"Codelists grouped ({total_cl_in_groups}) into groups ({total_groups}), "
          f"number of single codelists - {single_count}")

    return True
