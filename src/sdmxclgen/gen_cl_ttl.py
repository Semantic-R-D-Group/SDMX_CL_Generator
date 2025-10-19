# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

# gen_cl_ttl.py
from datetime import date
import pandas as pd
from .templates import SDMX_ConceptSchemes, SDMX_PREF_CODE, SDMX_CODE_URI
from .gen_template import NEW_PREF, NEW_PURL, NEW_PREF_CODE, NEW_PURL_CODE, PREF_COM_SET
from .get_funcs import (
    get_concept_str,
    get_code_description_dict,
    get_concept_scheme_str,
    get_scheme_dict,
    get_from_scheme_dict
)
from .quality_check import check_rdf_quality

def generation_ttl(in_dict, in_scheme_dict, output_file, concept_scheme: str):
    """
    Generates an RDF/Turtle file with descriptions of a codelist based on the provided data.

    Parameters
    ----------
    in_dict : dict
        Dictionary where the key is the code (str), and the value is a list/dict of data about the agency,
        code description, etc. (format used inside ``get_code_description_dict``).
    in_scheme_dict : dict
        Dictionary with metadata about the scheme (e.g., label, description),
        formed by the function ``get_scheme_dict``.
    output_file : str
        Path to the resulting TTL file where the generated codelist will be written.
    concept_scheme : str
        Identifier of the codelist (e.g., "ESTAT:CL_COVERAGE_POP(1.1.0)").

    Returns
    -------
    tuple
        (label_n3, description_concept_n3), where:
        - label_n3 (str) — prepared string for rdfs:label.
        - description_concept_n3 (str) — prepared string for dct:description.

    Notes
    -----
    1. Defines a set of prefixes, combining PREF_COM_SET and prefixes for SDMX (sdmx-concept, etc.).
    2. Calls ``get_concept_scheme_str`` to form the main part of the TTL file about the scheme (ConceptScheme).
    3. For each code (code, agencies), generates SKOS concept blocks using ``get_concept_str``.
    4. If a code has multiple agencies, additional structures are generated for their description.
    5. Writes the final TTL file.

    Examples
    --------
    >>> codes_dict = {
    ...     "POP1": [{"agencyID": "ESTAT", "codeDescription": "Population 1 desc"}],
    ...     "POP2": [{"agencyID": "ESTAT", "codeDescription": "Population 2 desc"}]
    ... }
    >>> scheme_dict = {"label": "Population Coverage", "description": "Coverage of population..."}
    >>> generation_ttl(codes_dict, scheme_dict, "output.ttl", "ESTAT:CL_COVERAGE_POP(1.1.0)")
    ('"Population Coverage"', '"Coverage of population..."')
    """
    conceptscheme_name = concept_scheme.split(":")[-1]
    sdmx_conceptscheme_name = f"{SDMX_PREF_CODE}:{conceptscheme_name}"

    # Additional prefixes
    pref_cl = {
        "sdmx-concept": "http://purl.org/linked-data/sdmx/2009/concept#",
        f"{SDMX_PREF_CODE}": f"{SDMX_CODE_URI}",
        f"{NEW_PREF}-concept": f"{NEW_PURL}/concept/",
        f"{NEW_PREF_CODE}": f"{NEW_PURL_CODE}",
        f"{NEW_PREF}": f"{NEW_PURL}"
    }

    # Merge common prefix set
    prefixes = PREF_COM_SET | pref_cl

    # Get part with ConceptScheme description
    concept_scheme_str, label_n3, description_concept_n3 = get_concept_scheme_str(
        conceptscheme_name,
        in_scheme_dict,
        sdmx_conceptscheme_name
    )

    # Title for code block
    concepts = []
    concepts_title = f"""
########################################
# CL_{conceptscheme_name.upper()} Codes
########################################
    """
    concepts.append(concepts_title)

    # UPD. Check for codes with multiple agencies
    # agencies_fl = False
    agencies_fl = any(len(agencies) > 1 for agencies in in_dict.values())

    for code, agencies in in_dict.items():
        agency_labels = []

        # UPD. If codes with multiple agencies are present, form Blank nodes
        # if len(agencies) > 1:
        if agencies_fl:

            agency_label_groups = {}
            for agency in agencies:
                agency_description = agency['codeDescription']
                if agency_description not in agency_label_groups:
                    agency_label_groups[agency_description] = []
                agency_label_groups[agency_description].append(f"{NEW_PREF}-agency:{agency['agencyID']}")

            for label, agency_list in agency_label_groups.items():
                agency_group = ", ".join(agency_list)
                agency_labels.append(
                    f"[{NEW_PREF}-agency:agenciesID {agency_group} ; "
                    f'rdfs:label """{label}"""@en ]'
                )

        # Generate block of a specific concept (code)
        concept = get_concept_str(conceptscheme_name, code, agencies, agency_labels)
        concepts.append(concept)

    # If codes with multiple agencies are present, add corresponding prefix
    if agencies_fl:
        prefixes |=  {f"{NEW_PREF}-agency":f"{NEW_PURL}/agency/"}

    # Form prefix text
    prefixes_str = "\n".join(
        f"@prefix {key}: <{value}> ."
        for key, value in prefixes.items()
    ) + "\n\n"

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(prefixes_str)
        f.write(concept_scheme_str)
        f.write("\n".join(concepts))

    return label_n3, description_concept_n3, agencies_fl


def sdmx_codelist_gen(cl_table_csv, cl_data_csv, out_dir):
    """
    Creates a set of Turtle files (one for each codelist), as well as a general code.ttl
    file with summary information about all codelists.

    Parameters
    ----------
    cl_table_csv : str
        CSV file with summary information about codelists (e.g., label, version, scheme identifier).
    cl_data_csv : str
        CSV file with detailed code data.
    out_dir : str
        Directory where generated Turtle files will be saved.

    Returns
    -------
    None
        The function writes files to disk and does not return a value.

    Notes
    -----
    1. Loads two CSVs (df_code_lists and df_codes), forms a general file code.ttl.
    2. For each unique SchemeID, creates a separate TTL file using the function generation_ttl.
    3. After creating each file, calls check_rdf_quality to assess the quality of the RDF model.
    4. The final code.ttl file contains a summary (skos:ConceptScheme) of all existing codelists.

    Examples
    --------
    >>> sdmx_codelist_gen("all_codelists.csv", "all_codes.csv", "./out_ttl/")
    # Generates files like ./out_ttl/new-code-CL_COVERAGE_POP.ttl and ./out_ttl/code.ttl,
    # performs RDF quality check (quality_score).
    """
    # Load CSV into DataFrames
    df_code_lists = pd.read_csv(cl_table_csv, sep=";", dtype=str, keep_default_na=False)
    df_codes = pd.read_csv(cl_data_csv, sep=";", dtype=str, keep_default_na=False)

    # list of codelists with multiple agencies
    has_agency_label_ttls = []

    # Prepare prefixes
    pref_code = {
        "dct": "http://purl.org/dc/terms/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        f"{NEW_PREF_CODE}": f"{NEW_PURL_CODE}",
    }
    code_prefixes = PREF_COM_SET | pref_code

    current_date = date.today().isoformat()

    # Description block for code.ttl
    code_scheme = [
        f"\n\n{NEW_PREF_CODE}: a skos:ConceptScheme ;\n",
        f"    rdfs:label \"List of available code lists\"@en ;\n",
        f"    dct:creator \"SemanticPro SDMX Extension\" ;\n",
        f"    dct:issued \"{current_date}\"^^<http://www.w3.org/2001/XMLSchema#date> ;\n",
        f"    dct:description \"A general code list with links to all available code schemes.\"@en .\n"
        "\n# CODE LISTS\n"
    ]

    # Initial text of code.ttl
    code_str = "\n".join(
        f"@prefix {key}: <{value}> ."
        for key, value in code_prefixes.items()
    ) + "\n " + "".join(code_scheme)

    from itertools import islice

    # For each unique SchemeID create a separate TTL
    # (limited to 1000 schemes via islice, by default — for demonstration)
    for concept_scheme in islice(df_code_lists["SchemeID"].unique(), 1000):
        scheme_description_dict = get_scheme_dict(df_code_lists, concept_scheme)
        _, _, codelists, _ = get_from_scheme_dict(scheme_description_dict, concept_scheme)
        code_description_dict = get_code_description_dict(df_codes, codelists)

        scheme_name = concept_scheme.split(":")[-1]
        output_file = f"{str(out_dir)}/{NEW_PREF}-code-{scheme_name}.ttl"

        label_n3, description_concept_n3, agencies_fl = generation_ttl(
            code_description_dict,
            scheme_description_dict,
            output_file,
            concept_scheme
        )
        # if codelist has multiple agencies, add to the list
        if agencies_fl:
            has_agency_label_ttls.append((output_file, label_n3))
        # Add to summary code.ttl
        code_ttl_cl = (
            f"\n{NEW_PREF_CODE}:{concept_scheme} a skos:ConceptScheme ;\n"
            f"    rdfs:label {label_n3}@en ;\n"
        )
        if len(description_concept_n3) > 0:
            code_ttl_cl += f"    dct:description {description_concept_n3}"
        code_ttl_cl += f"    dct:source <{NEW_PURL}/code/{scheme_name}> .\n"

        code_str += code_ttl_cl

        # Check quality of generated TTL
        print(f"\n{output_file}")
        result = check_rdf_quality(output_file)
        # Extract quality_score_10 and value_score_10
        quality_score_10 = result.get("quality_score_10")
        value_score_10 = result.get("value_score_10")

        # Form CSV file of codelists with multiple agencies
        df_agency_labels = pd.DataFrame(has_agency_label_ttls, columns=["TTL File", "ConceptScheme Label"])
        df_agency_labels["ConceptScheme Label"] = df_agency_labels["ConceptScheme Label"].str.strip('"')
        df_agency_labels.to_csv(f"codelists_with_hasAgencyLabel.csv", index=False)

        # If scores are high, print short message, otherwise full report
        if (quality_score_10 and value_score_10) and (quality_score_10 > 9.5 and value_score_10 > 9.5):
            print(f"quality_score_10: {quality_score_10}\nvalue_score_10: {value_score_10}")
        else:
            for key, value in result.items():
                print(f"{key}: {value}")

    # Create/overwrite general code.ttl
    file_name = f"{str(out_dir)}/code.ttl"
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(code_str)

    # Check quality of general code.ttl
    _ = check_rdf_quality(file_name)
