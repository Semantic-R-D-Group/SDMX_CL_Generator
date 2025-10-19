# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

import pandas as pd
from rdflib import Graph, URIRef, Namespace, RDF, Literal
from .templates import SDMX_SCHEME_CONCEPT_CL_ASS, SDMX_CONCEPT_SCHEMES, SDMX_CODES, SDMX_CODE_URI
from .gen_template import NEW_PREF, NEW_PREF_CODE

# Consider
# ESTAT:CL_INSTR_ASSET93(1.5) - ESTAT,1,INSTR_ASSET,1.5,(1,5)
# ESTAT:CL_SECTOR93(1.4) - ESTAT,1,SECTOR,1.4,(1,4)
# ESTAT:SCL_CL_WSTATUS(1.0)- ESTAT,1,CL_WSTATUS,1.0,(1,0)
# ESTAT:SCL_WSTATUS(1.0) - ESTAT,1,WSTATUS,1.0,(1,0)
# SDMX:CL_COFOG_1999(1.0) - SDMX,0,COFOG_,1.0,(1,0)
# SDMX:CL_COPNI_1999(1.0) -SDMX,0,COPNI_,1.0,(1,0)
# SDMX:CL_COPP_1999(1.0) -SDMX,0,COPP_,1.0,(1,0)

def get_concepts_by_scheme_id(key: str, glossary=SDMX_SCHEME_CONCEPT_CL_ASS) -> list:
    """Retrieves a list of concepts linked to a given scheme identifier from the glossary.

    Parameters
    ----------
    key : str
        Scheme identifier (usually in the format 'AGENCY:CL_ID(VERSION)') used as a key in the glossary.
    glossary : dict, optional
        Dictionary mapping codelist schemes to concept descriptions.
        Dictionary format:
        {
            "<scheme_id>": {
                "concept": Union[str, List[str]],
                ...
            },
            ...
        }

    Returns
    -------
    list of str
        A list of concepts associated with the given key. If there is only one concept,
        a list with one element is returned. If the key is not found, an empty list is returned.

    Examples
    --------
    >>> get_concepts_by_scheme_id("SDMX:CL_FREQ(2.1)")
    ['freq']

    Notes
    -----
    The function is intended to retrieve concepts related to a specific codelist
    from the predefined glossary of SDMX schemes. Useful for building models based on codelists.
    """
    if key in glossary:
        concept = glossary[key]['concept']
        return concept if isinstance(concept, list) else [concept]
    else:
        # print(f"Key '{key}' not found in glossary.")
        return []

def get_singles_template(df: pd.DataFrame, template_file="analysis/gen_template.py") -> None:
    """Generates and saves the Python dictionary SINGLES from codelists of type 'SINGLE'.

    Parameters
    ----------
    df : pandas.DataFrame
        Table with metadata of codelists. Must contain the following columns:
        - 'GroupType' : str — grouping type, filtered by value 'SINGLE'.
        - 'CL Name' : str — human-readable name of the codelist.
        - 'CodelistID' : str — codelist identifier (e.g., 'SDMX:CL_FREQ(2.1)').
        - 'Codelist Description' : str — description of the codelist.

    template_file : str, optional
        Path to the file where the `SINGLES` dictionary will be saved.
        Default: "analysis/gen_template.py".

    Returns
    -------
    None
        The result is saved as a Python file. Returns nothing.

    Notes
    -----
    - For each row with `GroupType = 'SINGLE'`, a record is created in the SINGLES dictionary.
    - If a SchemeID has already been encountered, an index is added to avoid duplicate keys.
    - The output file contains a ready-to-use dictionary that can be imported into other modules.

    Examples
    --------
    >>> df = pd.read_csv("all_cl_data.csv")
    >>> get_singles_template(df, "output_template.py")
    # -> Creates a Python file with the SINGLES dictionary based on SINGLE codelists.
    """

    # Filter rows with groupType = SINGLE
    filtered_df = df[df['GroupType'] == 'SINGLE']

    # Build the SINGLES dictionary
    singles = {}
    seen_scheme_ids = set()

    index = 0
    for _, row in filtered_df.iterrows():
        scheme_id = get_scheme_id(row['CL Name'])
        if scheme_id in seen_scheme_ids:
            print(f"Duplicate SchemeID found: {scheme_id}")
            scheme_id = str(index) + scheme_id
            index += 1
        seen_scheme_ids.add(scheme_id)

        singles[scheme_id] = {
            "codelist": row['CodelistID'],
            "label": row['CL Name'],
            "description": row['Codelist Description']
        }

    # Write dictionary to Python file with formatted output
    with open(template_file, "w") as f:
        f.write("SINGLES = {\n    ")
        for key, value in singles.items():
            f.write(f"    '{key}': {{\n    ")
            f.write(f"        'codelist': '{value['codelist']}',\n    ")
            f.write(f"        'label': '{value['label']}',\n    ")
            f.write(f"        'description': \"\"\"{value['description']}\"\"\"\n    ")
            f.write("    },\n    ")
        f.write("}")

def get_scheme_id(cl_label: str) -> str:
    """Generates a scheme identifier from the codelist label, excluding prepositions.

    Parameters
    ----------
    cl_label : str
        Codelist label (e.g., "Frequency of Reporting").
        Used to extract a unique, standardized scheme identifier.

    Returns
    -------
    str
        A string composed of the first two significant words of the label in `camelCase`.
        Returns an empty string if there are no significant words.

    Notes
    -----
    - English prepositions are ignored (e.g., 'of', 'in', 'for').
    - The first word is lowercase, the second capitalized.
    - Used to create keys in concept glossaries like `SINGLES` in `gen_template.py`.

    Examples
    --------
    >>> get_scheme_id("Frequency of Reporting")
    'frequencyReporting'

    >>> get_scheme_id("Currency")
    'currency'

    >>> get_scheme_id("Of the country")
    ''
    """

    # List of English prepositions
    prepositions = {"of", "in", "on", "at", "for", "with", "about", "against", "between", "into", "through", "during",
                    "before", "after", "above", "below", "under", "over", "to", "from", "by", "as", "like", "since",
                    "until", "within", "without", "among", "along", "behind", "beyond", "but", "except", "up", "down",
                    "off", "onto", "out", "upon"}

    # Remove prepositions and split into words
    words = [word for word in cl_label.split() if word.lower() not in prepositions]

    # Keep only first two words
    if len(words) == 0:
        return ""
    elif len(words) == 1:
        return words[0].lower()
    else:
        first, second = words[0], words[1]
        return first.lower() + second.capitalize()

def get_sdmx_schemes_codes(file_path: str) -> tuple[set, dict]:
    """Extracts concept scheme identifiers and existing codes from an RDF graph in Turtle format.

    Parameters
    ----------
    file_path : str
        Path to the Turtle (TTL) file containing codelist and concept definitions.

    Returns
    -------
    tuple
        Tuple of two elements:
        1. set of str — set of concept scheme names (by URI identifier).
        2. dict[str, set[str]] — dictionary mapping scheme URI to a set of codes (by `skos:notation`).

    Notes
    -----
    - Uses RDFLib to load and traverse the graph.
    - Assumes concepts and schemes are represented using the SKOS ontology.
    - `ConceptScheme` is defined via type `skos:ConceptScheme`.
    - Codes are extracted from triples of the form:
        (?concept, skos:notation, ?code)
        (?concept, skos:inScheme, ?scheme)

    Examples
    --------
    >>> schemes, codes = get_sdmx_schemes_codes("cl_out/example_codelist.ttl")
    >>> print(schemes)
    {'FREQ', 'AGE', 'CURRENCY'}
    >>> print(codes['http://example.org/codelist#FREQ'])
    {'A', 'M', 'Q', 'Y'}
    """
    # Load the TTL file
    g = Graph()
    g.parse(file_path, format='turtle')

    # Define the SKOS namespace
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

    concept_schemes_names = set()
    for s, p, o in g.triples((None, RDF.type, SKOS.ConceptScheme)):
        uri = str(s)
        name = uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]
        concept_schemes_names.add(name)

    # Extract all codes
    existing_codes = {}
    for s, p, o in g.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#notation"), None)):
        scheme = next(g.objects(s, URIRef("http://www.w3.org/2004/02/skos/core#inScheme")), None)
        if scheme:
            existing_codes.setdefault(str(scheme), set()).add(str(o))
    return concept_schemes_names, existing_codes

def get_scheme_dict(df: pd.DataFrame, scheme_id: str) -> dict:
    """Builds a dictionary with descriptions of codelists related to a given scheme.

    Parameters
    ----------
    df : pandas.DataFrame
        Table with metadata of codelists. Must contain the following columns:
        - 'CodelistID' : str — codelist identifier.
        - 'CL Name' : str — human-readable name of the codelist.
        - 'SchemeID' : str — scheme identifier used for filtering.
        - 'Codelist Description' : str — codelist description.
        - 'URL' : str — source link for the codelist.

    scheme_id : str
        The scheme identifier used to select rows in the table.

    Returns
    -------
    dict
        Dictionary of the format:
        {
            "scheme_id": [
                {
                    "codelistID": str,
                    "label": str,
                    "codelistDescription": str,
                    "URL": str
                },
                ...
            ]
        }

        If no matches for the given `scheme_id`, returns an empty dictionary.

    Raises
    ------
    ValueError
        If required columns are missing in the DataFrame.

    Examples
    --------
    >>> get_scheme_dict(df, \"SDMX:CL_FREQ(2.1)\")
    {
        \"SDMX:CL_FREQ(2.1)\": [
            {
                \"codelistID\": \"SDMX:CL_FREQ(2.1)\",
                \"label\": \"Frequency\",
                \"codelistDescription\": \"Frequency of observation\",
                \"URL\": \"http://example.org/freq.xml\"
            }
        ]
    }
    """

    # Check for required columns
    required_columns = {"CodelistID", "CL Name", "SchemeID", "Codelist Description", "URL"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain the following columns: {required_columns}")

    # Filter DataFrame by SchemeID
    filtered_df = df[df["SchemeID"] == scheme_id]

    if filtered_df.empty:
        return {}  # If no data for the scheme, return empty dictionary

    # Build dictionary grouped by SchemeID
    description_dict = {
        scheme_id: [
            {
                "codelistID": row['CodelistID'],
                "label": row['CL Name'],
                "codelistDescription": row['Codelist Description'],
                "URL": row['URL']
            }
            for _, row in filtered_df.iterrows()
        ]
    }

    return description_dict

def get_from_scheme_dict(scheme_dict: dict, scheme_id: str) -> tuple:
    """Extracts labels, descriptions, IDs, and URLs of codelists from a scheme dictionary by `scheme_id`.

    Parameters
    ----------
    scheme_dict : dict
        Dictionary containing scheme descriptions and associated codelists.
        Format:
        {
            "<scheme_id>": [
                {
                    "codelistID": str,
                    "label": str,
                    "codelistDescription": str,
                    "URL": str
                },
                ...
            ],
            ...
        }

    scheme_id : str
        The scheme identifier for which to extract data.

    Returns
    -------
    tuple
        A tuple of four elements:
        - set of str: unique labels (`label`)
        - set of str: description strings including ID (format: `"codelistID: description"`)
        - list of str: codelist identifiers (`codelistID`)
        - list of str: source URLs (`URL`)

        If `scheme_id` is not found, returns four empty structures.
    Notes
    -----
    Used as a helper function for analyzing and displaying the contents of codelist schemes
    based on a dictionary created, for example, by the `get_scheme_dict` function.

    Examples
    --------
    >>> get_from_scheme_dict(scheme_dict, "SDMX:CL_FREQ(2.1)")
    (
        {'Frequency'},
        {'SDMX:CL_FREQ(2.1): Frequency of observation'},
        ['SDMX:CL_FREQ(2.1)'],
        ['http://example.org/freq.xml']
    )
    """

    # Check if scheme_id exists in dictionary
    if scheme_id not in scheme_dict:
        print(f"Scheme ID '{scheme_id}' not found in scheme dictionary.")
        return ()

    # Extract labels and build sets/lists
    labels =  {item.get("label") for item in scheme_dict[scheme_id] if "label" in item}
    descriptions = {f"{item['codelistID']}: {item['codelistDescription']}" for item in scheme_dict[scheme_id]}
    source_codelists = [item.get("codelistID") for item in scheme_dict[scheme_id] if "codelistID" in item]
    source_urls = [item.get("URL") for item in scheme_dict[scheme_id] if "URL" in item]

    return labels, descriptions, source_codelists, source_urls
#   labels, descriptions, source_codelists, source_urls = get_from_scheme_dict(scheme_dict, scheme_id)

def get_concept_scheme_str(concept_scheme_name: str, in_scheme_dict: dict, sdmx_scheme_uri: str) -> tuple:
    """
    Generates an RDF graph string (Turtle format) defining a ConceptScheme and its class,
    including labels, descriptions, links, and alignment with the SDMX scheme.

    Parameters
    ----------
    concept_scheme_name : str
        Short name of the concept scheme (e.g., 'freq', 'currency').

    in_scheme_dict : dict
        Dictionary with scheme information and associated codelists.
        Format:
        {
            "scheme_name": [
                {
                    "codelistID": str,
                    "label": str,
                    "codelistDescription": str,
                    "URL": str
                },
                ...
            ],
            ...
        }

    sdmx_scheme_uri : str
        Full URI of the scheme in the SDMX model used for `skos:exactMatch`.

    Returns
    -------
    tuple
        A tuple of three elements:
        1. str: Turtle text of the `skos:ConceptScheme` and related `rdfs:Class`
        2. str: `n3` literal of the main scheme label (prefLabel)
        3. str: `skos:definition` string (if generated, otherwise empty)

    Notes
    -----
    - Matching is performed by `concept_scheme_name`, which must be a key in `in_scheme_dict`.
    - If the scheme is known as an SDMX concept (`SDMX_CONCEPT_SCHEMES`), a `skos:exactMatch` is added.
    - Labels, descriptions, links (`rdfs:seeAlso`), and relations with concepts (`skos:related`) are added based on the data.
    - Missing descriptions/labels are marked and logged, but do not interrupt execution.

    Examples
    --------
    >>> ttl_str, label, definition = get_concept_scheme_str("freq", scheme_dict, "http://purl.org/.../CL_FREQ")
    >>> print(ttl_str)
    # skos:ConceptScheme and rdfs:Class description in Turtle format

    See Also
    --------
    - get_from_scheme_dict
    - get_concepts_by_scheme_id
    """

    exact = concept_scheme_name in SDMX_CONCEPT_SCHEMES
    concept_class_name = concept_scheme_name[0].upper() + concept_scheme_name[1:]
    concept_scheme_id = f"{NEW_PREF_CODE}:{concept_scheme_name}"
    concept_class_id = f"{NEW_PREF_CODE}:{concept_class_name}"

    # Find labels and descriptions
    labels, descriptions, source_codelists, source_urls = get_from_scheme_dict(in_scheme_dict, concept_scheme_name)

    # Optional validation
    for label in labels:
        if label == "Label no accessible":
            print(f"ERROR (get_concept_scheme_str): For {concept_scheme_name} {label}")
    for description in descriptions:
        if description == "Description no accessible":
            print(f"ERROR (get_concept_scheme_str): For {concept_scheme_name} {description}")

    concept_scheme_title = f"""
#####################################################
# CL_{concept_scheme_name.upper()} Scheme Definition
#####################################################\n\n"""

    # Scheme beginning
    #------------------------
    concept_scheme_beg = f"""{concept_scheme_id} a skos:ConceptScheme ;
    rdfs:subClassOf sdmx-code:ConceptScheme ;\n"""

    index = 0
    label_concept  = concept_scheme_labels = ""
    for label in labels:
        index += 1
#        label_concept = label
        label_n3 = Literal(label + " - codelist scheme").n3()
        if index == 1:
            label_concept = label
            concept_scheme_labels = f"""    skos:prefLabel {label_n3}@en ;
    rdfs:label {label_n3}@en ;\n"""
        else:
            concept_scheme_labels = concept_scheme_labels + f"    skos:altLabel {label_n3}@en ;\n"

    concept_scheme_notation = f"""    skos:notation "CL_{concept_scheme_name.upper()}" ;\n"""

    concept_scheme_beg = concept_scheme_beg + concept_scheme_labels + concept_scheme_notation
    concept_scheme_str = concept_scheme_title + concept_scheme_beg

    index = 0
    concept_scheme_notes = concept_scheme_class_end_comm = ""
    description_concept_n3 = ""
    for description in descriptions:
        description_n3 = Literal(description).n3()
        index += 1
        if index == 1:
            if description.split(':')[2] != " Description not available":
                description_concept_n3 = description_n3
                concept_scheme_notes = f"    skos:note {description_n3}@en ;\n"
        else:
            if description.split(':')[2] != " Description not available":
                concept_scheme_notes = concept_scheme_notes +  f"    skos:note {description_n3}@en ;\n"

    if len(source_codelists) > 1:
        cls = ", ".join(source_codelists)
        concept_scheme_def = f"""\"A reference {concept_scheme_name} codelist combining {cls}\"@en ;\n"""
        concept_scheme_comb = "    skos:definition " + concept_scheme_def
    elif len(source_codelists) == 1:
        cls = source_codelists[0]
        concept_scheme_def = f"""\"A reference {concept_scheme_name} codelist based on {cls}\"@en ;\n"""
        concept_scheme_comb = "    skos:definition " + concept_scheme_def
    else:
        concept_scheme_def = concept_scheme_comb = ""

    for url in source_urls:
        concept_scheme_comb = concept_scheme_comb + f"""    rdfs:seeAlso <{url}> ;\n"""

    concept_scheme_concept = ""
    concepts = get_concepts_by_scheme_id(concept_scheme_name)
    if len(concepts) > 0:
        concept_str = f"{NEW_PREF}-concept:" + f", {NEW_PREF}-concept:".join(concepts)
        concept_scheme_concept = f"    rdfs:seeAlso " + concept_str + " ;\n"
        concept_scheme_concept = concept_scheme_concept + f"    skos:related " + concept_str + " ;\n"

    concept_scheme_end = f"""    rdfs:seeAlso {NEW_PREF_CODE}:{concept_class_name} .\n\n"""

    concept_scheme_str = concept_scheme_str + concept_scheme_comb + concept_scheme_notes + concept_scheme_concept + concept_scheme_end

    if exact:
        concept_scheme_str = concept_scheme_str + f"{concept_scheme_id} skos:exactMatch {sdmx_scheme_uri} .\n\n"

    # Class definition
    #------------------------
    label_n3 = Literal(label_concept + " - codelist class").n3()

    concept_scheme_class_str = f"""{concept_class_id} a rdfs:Class ;
    rdfs:subClassOf skos:Concept ;
    skos:prefLabel {label_n3}@en ;
    rdfs:label {label_n3}@en ;\n"""

    if len(concept_scheme_class_end_comm)>0:
        concept_scheme_class_str = concept_scheme_class_str + f"    rdfs:comment {concept_scheme_class_end_comm}"

    concept_scheme_class_end = f"""    rdfs:isDefinedBy {concept_scheme_id} ;
    skos:inScheme {concept_scheme_id} .\n\n"""

    concept_scheme_class_str = concept_scheme_class_str + concept_scheme_class_end

    return concept_scheme_str + concept_scheme_class_str, Literal(label_concept).n3(), concept_scheme_def #description_concept_n3

def get_concept_str(concept_scheme_name: str, code: str, agencies: list, agency_labels: list) -> str:
    """Generates a Turtle RDF string for a concept belonging to a given scheme and code.

    Parameters
    ----------
    concept_scheme_name : str
        Name of the concept scheme (e.g., 'freq', 'currency').

    code : str
        Concept code value to be used as `skos:notation`.

    agencies : list of dict
        List of agency dictionaries with at least:
        - 'codeDescription' : str — main label of the concept.

    agency_labels : list of str
        List of `n3` formatted strings representing additional labels from agencies.
        If empty, only `rdfs:label` with the first label is used.

    Returns
    -------
    str
        Turtle text describing:
        - The concept as an instance of `skos:Concept` and custom class;
        - Relations `skos:notation`, `skos:prefLabel`, `rdfs:label`;
        - Optionally `:hasAgencyLabel` and `skos:exactMatch`;
        - `skos:hasTopConcept` relation for the scheme.

    Notes
    -----
    - If the concept is aligned with SDMX (`SDMX_CODES` contains a mapping), a `skos:exactMatch` is added.
    - Identifier format: `prefix:schemeName-codeValue`.
    - Uses the global variable `NEW_PREF_CODE` and the prefixes `NEW_PREF`, `SDMX_CODE_URI`.

    Examples
    --------
    >>> agencies = [{'codeDescription': 'Monthly'}]
    >>> agency_labels = ['"Monthly (IMF)"@en', '"Monthly (ESTAT)"@en']
    >>> get_concept_str("freq", "M", agencies, agency_labels)
    # => Turtle string of the concept with multiple agency labels and exactMatch
    """

    concept_id = f"{NEW_PREF_CODE}:{concept_scheme_name}-{code}"
    concept_class_name = concept_scheme_name[0].upper() + concept_scheme_name[1:]

    # Debug: temporarily removed sdmx-concept:Concept
#   concept_str = f"""{concept_id} a skos:Concept, sdmx-concept:Concept, {NEW_PREF_CODE}:{concept_class_name};
    concept_str = f"""{concept_id} a skos:Concept, {NEW_PREF_CODE}:{concept_class_name};
    skos:topConceptOf {NEW_PREF_CODE}:{concept_scheme_name} ;
    skos:inScheme {NEW_PREF_CODE}:{concept_scheme_name} ;
    skos:notation \"{code}\" ;
    skos:prefLabel {Literal(agencies[0]['codeDescription']).n3()}@en ;\n"""

    if len(agency_labels) == 0:
        concept_str = concept_str + f"    rdfs:label {Literal(agencies[0]['codeDescription']).n3()}@en .\n\n"
    else:
        concept_str = concept_str + f"    {NEW_PREF}:hasAgencyLabel {',\n                      '.join(agency_labels)} .\n\n"

    # Add skos:exactMatch if the concept is aligned with SDMX
    if (concept_scheme_name in SDMX_CODES.keys()) and (code in SDMX_CODES[concept_scheme_name]):
        concept_str = concept_str + f"{concept_id} skos:exactMatch <{SDMX_CODE_URI}-{code}> .\n"

    concept_str = concept_str + f"{NEW_PREF_CODE}:{concept_scheme_name} skos:hasTopConcept {concept_id} .\n\n"

    return concept_str

def get_code_description_dict(df: pd.DataFrame, codelists: list) -> dict:
    """Builds a dictionary of code descriptions for the given codelists.

    Parameters
    ----------
    df : pandas.DataFrame
        Table with codelist data. Required columns:
        - 'CodelistID' : str — codelist identifier.
        - 'Agency' : str — agency responsible for the code.
        - 'Code' : str — code value.
        - 'Code Description' : str — description of the code.

    codelists : list of str
        List of codelist identifiers for which code descriptions should be extracted.

    Returns
    -------
    dict
        Dictionary where the key is the code value, and the value is a list of description dictionaries.
        Format:
        {
            "CODE1": [
                {
                    "agencyID": str,
                    "codeDescription": str
                },
                ...
            ],
            ...
        }

    Raises
    ------
    ValueError
        If the input DataFrame does not contain the required columns.

    Notes
    -----
    - For each codelist, rows are filtered and grouped by the 'Code' field.
    - The same code may be described by multiple agencies (different records).
    - Dictionary merging (|) is used to accumulate results for each codelist.

    Examples
    --------
    >>> codelists = ['SDMX:CL_FREQ(2.1)', 'IMF:CL_CURRENCY(1.6)']
    >>> get_code_description_dict(df, codelists)
    {
        'M': [{'agencyID': 'IMF', 'codeDescription': 'Monthly'}],
        'Q': [{'agencyID': 'SDMX', 'codeDescription': 'Quarterly'}],
        ...
    }
    """

    description_dict = {}
    # Check required columns
    required_columns = {"CodelistID", "Agency", "Code", "Code Description"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    filtered_df = df[df['CodelistID'].isin(codelists)]
    for code, group in filtered_df.groupby('Code'):
        # Build dictionary in required structure for all unique codes
        group_dict = {
            code: [
                {
                    "agencyID": row['Agency'],
                    "codeDescription": row['Code Description']
                }
                for _, row in group.iterrows()
            ]
        }

        description_dict |= group_dict

    return description_dict
