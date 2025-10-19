# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

# templates.py
# Configuration module: contains definitions of columns, prefixes, URIs, and glossaries for working with SDMX models

from rdflib import Namespace

# from site import PREFIXES

# Columns of the source file with codelists (in/Code_Lists_GR_SDMX.csv)
DF_CL_SOURCE = ["agency_id", "codelistID", "Name", "URL"]

# Columns for DataFrames with codes and codelists.
# Must be updated synchronously with save_codelist_data in parse_save_cl.py !!!
DF_CODE_COLUMNS = ["CodelistID", "Agency", "Code", "Code Description"]
# For codelists
DF_CODE_LISTS_COLUMNS = ["CodelistID", "GroupType", "SchemeID", "CL Name", "Codelist Description", "Agency", "CLID", "Ver", "Total Codes", "Unique Codes",
                        "Common codes", "Shared Codes", "Similar Codelists", "URL"]

# Order of agency prefixes (used in generation and analysis)
AGENCY = ["SDMX", "ESTAT", "IMF", "UNSD", "IAEG-SDGs", "UIS"]

# Prefix and URI for SDMX codes
SDMX_PREF_CODE = "sdmx-code"
SDMX_CODE_URI = "http://purl.org/linked-data/sdmx/2009/code#"

# Set of SDMX ConceptSchemes (used for skos:exactMatch)
SDMX_CONCEPT_SCHEMES = {'confStatus', 'obsStatus', 'area', 'decimals', 'currency',
                        'sex', 'timeFormat', 'unitMult', 'freq'
}

# Dictionary of valid SDMX codes by concept
SDMX_CODES = {
    'decimals': {'6', '1', '4', '8', '3', '5', '9', '7', '0', '2'},
    'unitMult': {'6', '12', '1', '15', '4', '3', '9', '0', '2'},
    'freq': {'S', 'M', 'Q', 'W', 'N', 'B', 'D', 'A'},
    'obsStatus': {'B', 'E', 'M', 'P', 'F', 'S', 'A', 'I'},
    'confStatus': {'S', 'C', 'N', 'F', 'D'},
    'sex': {'T', 'M', 'N', 'F', 'U'},
    'timeFormat': {'P1D', '702', '610', 'P3M', '602', '102', 'P1M', '711', 'P6M', 'PT1M', '716',
                   '704', '616', 'P1Y', '708', '604', 'P7D', '608', '710', '203', '719'}
}

# Grouping of SDMX schemes and related codelists (used when generating CL and TTL)
SDMX_ConceptSchemes = {
    "sdmx-code:currency": {"GroupType": "SINGLE", "codelists": ["IMF:CL_CURRENCY(1.6)"]},
    "sdmx-code:area": {"GroupType": "AREA", "codelists": ["SDMX:CL_AREA(2.0.1)", "ESTAT:CL_AREA(1.8)",
                                                        "IAEG-SDGs:CL_AREA(1.17)", "IMF:CL_AREA(1.17.0)",
                                                        "UIS:CL_AREA(1.0)", "UNSD:CL_AREA(1.0)"]},
    "sdmx-code:decimals": {"GroupType": "SINGLE", "codelists": ["SDMX:CL_DECIMALS(1.0)"]},
    "sdmx-code:freq": {"GroupType": "SINGLE", "codelists": ["SDMX:CL_FREQ(2.1)"]},
    "sdmx-code:confStatus": {"GroupType": "SINGLE", "codelists": ["SDMX:CL_CONF_STATUS(1.3)"]},
    "sdmx-code:obsStatus": {"GroupType": "OBSERVATION", "codelists": ["SDMX:CL_OBS_STATUS(2.2)", "ESTAT:CL_OBS_STATUS(2.3)"]},
    "sdmx-code:sex": {"GroupType": "SEX", "codelists": ["SDMX:CL_SEX(2.1)", "IAEG-SDGs:CL_SEX(1.1)"]},
    "sdmx-code:timeFormat": {"GroupType": "SINGLE", "codelists": ["SDMX:CL_TIME_FORMAT(1.0)"]},
    "sdmx-code:unitMult": {"GroupType": "SINGLE", "codelists": ["SDMX:CL_UNIT_MULT(1.1)"]},
}

# Mapping of schemes at the user level to concepts (for generating rdfs:seeAlso and skos:related)
SDMX_SCHEME_CONCEPT_CL_ASS = {
    "activity": {"concept":"ACTIVITY", "codelists": ["CL_ACTIVITY"]},
    "age": {"concept":"AGE", "codelists": ["CL_AGE"]},
    "agency": {"concept":"AGENCY", "codelists": ["CL_AGENCY"]}, # reflect in agency
    "area": {"concept":["REF_AREA", "COUNTERPART_AREA"], "codelists": ["CL_AREA"]},          # 2 concepts
    "basePer": {"concept":"BASE_PER", "codelists": ["CL_BASE_PER"]},      # missing
    "baseWeight": {"concept":"BASE_WEIGHT", "codelists": ["CL_BASE_WEIGHT"]},    # missing
    "civilStatus": {"concept":"CIVIL_STATUS", "codelists": ["CL_CIVIL_STATUS"]},
    "expenditureCofog": {"concept":"EXPENDITURE", "codelists": ["CL_COFOG"]},
    "expenditureCoicop": {"concept": "EXPENDITURE", "codelists": ["CL_COICOP"]},   # missing
    "expenditureCopni": {"concept": "EXPENDITURE", "codelists": ["CL_COPNI"]},
    "expenditureCopp": {"concept": "EXPENDITURE", "codelists": ["CL_COPP"]},
    "confStatus": {"concept":"CONF_STATUS", "codelists": ["CL_CONF_STATUS"]},
    "currency": {"concept":"CURRENCY", "codelists": ["CL_CURRENCY"]},
    "decimals": {"concept":"DECIMALS", "codelists": ["CL_DECIMALS"]},
    "educationLev": {"concept":"EDUCATION_LEV", "codelists": ["CL_EDUCATION_LEVEL"]},
    "freq": {"concept":["FREQ_COLL", "FREQ_DISS", "FREQ"], "codelists": ["CL_FREQ"]},     #3 concepts
    "obsStatus": {"concept":"OBS_STATUS", "codelists": ["CL_OBS_STATUS"]},
    "occupation": {"concept":"OCCUPATION", "codelists": ["CL_OCCUPATION"]},
    "compilingOrg": {"concept":["COMPILING_ORG","DATA_PROVIDER", "REP_AGENCY"], "codelists": ["CL_ORGANISATION"]}, #3 concepts
    "priceAdjust": {"concept":"PRICE_ADJUST", "codelists": ["CL_PRICE_ADJUST"]},  # missing
    "seasonalAdjust": {"concept":"SEASONAL_ADJUST", "codelists": ["CL_SEASONAL_ADJUST"]},
    "sex": {"concept":"SEX", "codelists": ["CL_SEX"]},
    "timeFormat": {"concept":"TIME_FORMAT", "codelists": ["CL_TIME_FORMAT"]},
    "timePerCollect": {"concept":"TIME_PER_COLLECT", "codelists": ["CL_TIME_PER_COLLECT"]},
    "transformation": {"concept":"TRANSFORMATION", "codelists": ["CL_TRANSFORMATION"]},
    "unitMeasure": {"concept":"UNIT_MEASURE", "codelists": ["CL_UNIT_MEASURE"]},
    "unitMult": {"concept":"UNIT_MULT", "codelists": ["CL_UNIT_MULT"]},
    "valuation": {"concept":"VALUATION", "codelists": ["CL_VALUATION"]}
}

# Standard RDF/SDMX/OWL namespaces
STANDARD_NAMESPACES = {
    "qb": "http://purl.org/linked-data/cube#",

    "sdmx-concept": "http://purl.org/linked-data/sdmx/2009/concept#",  #SKOS Concepts for each COG defined concept
    "sdmx-code": "http://purl.org/linked-data/sdmx/2009/code#",
    #SKOS Concepts and ConceptSchemes for each COG defined code list
    "sdmx-dimension": "http://purl.org/linked-data/sdmx/2009/dimension#",
    #component properties corresponding to each COG concept that can be used as a dimension
    "sdmx-attribute": "http://purl.org/linked-data/sdmx/2009/attribute#",
    #component properties corresponding to each COG concept that can be used as an attribute
    "sdmx-measure": "http://purl.org/linked-data/sdmx/2009/measure#",
    #component properties corresponding to each COG concept that can be used as a measure

    "dct": "http://purl.org/dc/terms/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "owl": "http://www.w3.org/2002/07/owl#"
    # Add other standard namespaces if needed
}

# RDFLib namespaces
old_model_url = "http://purl.org/linked-data/sdmx/2009/concept"
SDMX = Namespace("http://www.sdmx.org/resources/sdmxml/schemas/v3_0/structure")
SDMX_CONCEPT = Namespace(old_model_url)
SDMX_COMMON = Namespace("http://www.sdmx.org/resources/sdmxml/schemas/v3_0/common")
DCTERMS = Namespace("http://purl.org/dc/terms/")


# Namespaces for processing logic (str → structure, com → common types)
NAMESPACES = {'str': SDMX, 'com': SDMX_COMMON}

# 4. Preparing prefixes for the Turtle file of the new model

