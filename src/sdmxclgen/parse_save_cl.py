# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

# parse_save_cl.py
import xml.etree.ElementTree as ET
import re
import pandas as pd
from .analyze_func import com_uniq_code, common_codes_def
from .get_analyze_func import get_prefix_name_version
from .templates import DF_CODE_COLUMNS, DF_CODE_LISTS_COLUMNS


def parse_codelist_v3(xml_file):
    """
    Parses an XML file containing a Codelist in SDMX format (version 3.0) and extracts basic information.

    Parameters
    ----------
    xml_file : str
        Path to the local XML file to be parsed.

    Returns
    -------
    tuple
        A tuple of 8 elements:
        (codelist_id, codelist_name, agency, cl_id, cl_ver, codelist_description, urn, codes), where:
        - codelist_id : str
            Full codelist identifier, e.g., "ESTAT:CL_COVERAGE_POP(1.1.0)".
        - codelist_name : str
            The Name of the codelist.
        - agency : str
            Agency identifier responsible for the codelist.
        - cl_id : str
            Short codelist identifier (from the "id" attribute).
        - cl_ver : str
            Codelist version extracted from the identifier.
        - codelist_description : str
            The Description of the codelist.
        - urn : str
            Full URN (if present in the Codelist attributes).
        - codes : list
            A list of lists, where each sublist describes a code:
            [codelist_id, agency, code_value, code_description].

    Raises
    ------
    Exception
        Raised in case of parsing or filesystem errors.

    Notes
    -----
    1. Uses `xml.etree.ElementTree` for parsing.
    2. The function searches for Codelist and Code elements along paths where
       the Codelist is expected under .//msg:Structures/str:Codelists/str:Codelist.
    3. If no Codelist element is found, a warning is printed and default "Unknown" fields are returned.
    4. The `analyze_func` module is used to parse the identifier via `get_prefix_name_version`.

    Examples
    --------
    >>> result = parse_codelist_v3("example_codelist.xml")
    >>> print(result[0])  # codelist_id
    ESTAT:CL_COVERAGE_POP(1.1.0)
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        namespace = {
            'str': 'http://www.sdmx.org/resources/sdmxml/schemas/v3_0/structure',
            'com': 'http://www.sdmx.org/resources/sdmxml/schemas/v3_0/common',
            'msg': 'http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message'
        }

        # Search for the codelists section
        codelists_section = root.find(".//msg:Structures/str:Codelists", namespace)
        if codelists_section is not None:
            codelist_elem = codelists_section.find(".//str:Codelist", namespace)
        else:
            codelist_elem = None

        if codelist_elem is not None:
            urn = codelist_elem.get("urn", "Unknown")
            match = re.search(r"Codelist=([^:]+:[^)]+\))", urn)
            codelist_id = match.group(1) if match else "Unknown"

            codelist_name_elem = codelist_elem.find("com:Name", namespace)
            codelist_name = codelist_name_elem.text if codelist_name_elem is not None else "No name available"

            agency = codelist_elem.get("agencyID", "Unknown")
            cl_id = codelist_elem.get("id", "Unknown")

            # Extract version from identifier
            _, _, _, cl_ver, _ = get_prefix_name_version(codelist_id)

            description_elem = codelist_elem.find("com:Description", namespace)
            codelist_description = description_elem.text if description_elem is not None else "Description not available"
        else:
            print(f"Warning! No <Codelist> element found in {xml_file}")
            codelist_id = "Unknown"
            codelist_name = "Unknown"
            agency = "Unknown"
            cl_id = "Unknown"
            codelist_description = "Description not available"

        codes = []
        if codelist_elem is not None:
            code_elems = codelist_elem.findall(".//str:Code", namespace)
        else:
            code_elems = []

        for code in code_elems:
            code_value = str(code.get("id", "Unknown"))
            name_elems = code.findall("com:Name", namespace)

            def lang_of(elem):
                return elem.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "").lower()

            # Prefer English names (en, en-GB, en-US, etc.)
            en_names = [e.text.strip() for e in name_elems
                        if e.text and (lang_of(e) == "en" or lang_of(e).startswith("en-"))]
            # Include names with no language
            no_lang_names = [e.text.strip() for e in name_elems
                             if e.text and lang_of(e) == ""]

            if en_names:
                description_text = " | ".join(en_names)
            elif no_lang_names:
                description_text = " | ".join(no_lang_names)
            else:
                # Fallback to any non-empty Name, otherwise "No description"
                any_names = [e.text.strip() for e in name_elems if e.text]
                description_text = " | ".join(any_names) if any_names else "No description"

            codes.append([codelist_id, agency, code_value, str(description_text)])

        return codelist_id, codelist_name, agency, cl_id, cl_ver, codelist_description, urn, codes

    except Exception as e:
        print(f"Error while processing {xml_file}: {e}")
        return None, "Unknown", "Description not available", []


def save_codelist_data(codelists, cl_data_csv, cl_table_csv, save_flag=True):
    """
     Processes and saves codelist (Codelist) information into CSV files.

     Parameters
     ----------
     codelists : dict
         Dictionary where the key is the codelist identifier (codelist_id),
         and the value is an object containing metadata and codes
         (name, agency, codes, etc.).
     cl_data_csv : str
         Path to the CSV file for saving detailed code data.
     cl_table_csv : str
         Path to the CSV file for saving summary codelist information.
     save_flag : bool
         If True (default), the generated data is saved into the specified CSV files.

     Returns
     -------
     tuple
         A tuple (common_codes, df_code_lists, df_codes), where:
         - common_codes : set
             Set of codes that occur in multiple codelists (common codes).
         - df_code_lists : pandas.DataFrame
             Table with codelist metadata.
         - df_codes : pandas.DataFrame
             Table with detailed codes per codelist.

     Notes
     -----
     1. First, the function computes the total number of codes and unique codes
        using `common_codes_def` from the `analyze_func` module.
     2. For each codelist, the set of its codes is computed, as well as duplicates.
        If duplicates are found, a warning is printed.
     3. Using `com_uniq_code` from `analyze_func`, unique, common, and intersecting codes are determined.
     4. Final data is written to two CSV files: `cl_data_csv` (code list) and `cl_table_csv` (summary table).
     5. If `save_flag=False`, no files are saved, but DataFrames are returned.

     Raises
     ------
     Exception
         In case of CSV writing errors.

    Examples
    --------
    >>> codelists_data = {
    ...     "ESTAT:CL_COVERAGE_POP(1.1.0)": {
    ...         "name": "Population Coverage",
    ...         "agency": "ESTAT",
    ...         "clid": "CL_COVERAGE_POP",
    ...         "ver": "1.1.0",
    ...         "description": "Coverage of population across ...",
    ...         "simcl": "Similar CL info ...",
    ...         "url": "http://example.com/coverage_pop",
    ...         "codes": [
    ...             ["ESTAT:CL_COVERAGE_POP(1.1.0)", "ESTAT", "POP1", "Population 1"],
    ...             ["ESTAT:CL_COVERAGE_POP(1.1.0)", "ESTAT", "POP2", "Population 2"]
    ...         ]
    ...     }
    ... }
    >>> common_codes, df_cl, df_codes = save_codelist_data(codelists_data,
    ...                                                    "codes.csv",
    ...                                                    "codelists.csv",
    ...                                                    save_flag=False)
    >>> print(df_codes.head())
    """
    # Collect all codes and identify common codes (e.g., _Z or numeric)
    all_codes, common_codes = common_codes_def(codelists)
    all_codes_count = len(all_codes)
    unique_codes_count = len(set(all_codes))

    print("Codelists:", len(codelists))
    print(f"Total number of codes: {all_codes_count}")
    print(f"Number of unique codes: {unique_codes_count}")
    s = list(common_codes)
    s.sort()
    print(f"Common codes: {s}")

    codes_data = []
    code_lists = []
    for codelist_id, data in codelists.items():
        if codelist_id is None:
            continue

        codelist_name = data["name"]
        agency = data["agency"]
        cl_id = data["clid"]
        cl_ver = data["ver"]
        codelist_description = data["description"]
        sim_cl = data["simcl"]
        url = data["url"]

        # Build the set of codes for the current codelist
        code_set = set()
        duplicates = set()
        for entry in data["codes"]:
            if entry[2] in code_set:
                duplicates.add(entry[2])
            else:
                code_set.add(entry[2])

        if duplicates:
            print(f"Warning: Duplicates found in {codelist_id}: {duplicates}")

        # Add code data for DataFrame
        codes_data.extend([[codelist_id, agency, entry[2], entry[3]] for entry in data["codes"]])

        total_codes_count = len(code_set)

        # Determine overlapping codes relative to other codelists
        code_set, common_code_set, unique_codes_set = com_uniq_code(codelists, common_codes,
                                                                    unique_codes_count, codelist_id,
                                                                    code_set)

        uniq_codes_count = len(unique_codes_set)
        common_codes_count = len(common_code_set)

        shared_codes_count = total_codes_count - uniq_codes_count - common_codes_count

        code_lists.append([
            codelist_id, "", "", codelist_name, codelist_description, agency, cl_id,
            cl_ver, total_codes_count, uniq_codes_count, common_codes_count,
            shared_codes_count, sim_cl, url
        ])

    # Create DataFrames
    df_codes = pd.DataFrame(codes_data, columns=DF_CODE_COLUMNS)
    df_code_lists = pd.DataFrame(code_lists, columns=DF_CODE_LISTS_COLUMNS)

    # Save to CSV files if required
    if save_flag:
        try:
            df_codes.to_csv(cl_data_csv, index=False, sep=";", columns=DF_CODE_COLUMNS)
            df_code_lists.to_csv(cl_table_csv, index=False, sep=";", columns=DF_CODE_LISTS_COLUMNS)
        except Exception as e:
            print(f"Error while saving CSV files: {e}")
        else:
            print(f"Files {cl_data_csv} and {cl_table_csv} have been saved successfully.")

    return common_codes, df_code_lists, df_codes
