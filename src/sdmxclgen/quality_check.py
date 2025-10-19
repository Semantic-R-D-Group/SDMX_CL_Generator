# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

# quality_check.py
import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDFS, SKOS
from .gen_template import NEW_PREF_CODE, NEW_PURL
# OWL is not explicitly used but may be useful. Keep it if needed:
# from rdflib.namespace import OWL


def check_rdf_quality(file_path):
    """
    Checks the quality of an RDF model for compliance with basic requirements:
    correctness of prefixes, presence of labels, concept consistency, etc.

    Parameters
    ----------
    file_path : str
        Path to the Turtle file (.ttl) containing the RDF model to be checked.

    Returns
    -------
    dict
        A dictionary (report) with the following keys:
        - "missing_prefixes": list
            Prefixes that should have been declared but were not found.
        - "unused_prefixes": list
            Prefixes that were declared but not actually used in the graph.
        - "missing_labels": list
            Concepts missing SKOS.prefLabel.
        - "missing_agency_links": list
            Elements expected to have agency links but missing RDFS.label.
        - "inconsistent_concepts": list
            Concepts missing the SKOS.inScheme property.
        - "diverse_notation_count": int
            Number of distinct SKOS.notation values.
        - "descriptive_labels_count": int
            Number of concepts that have RDFS.comment.
        - "external_links_count": int
            How many times RDFS.seeAlso or SKOS.exactMatch occur in the graph.
        - "unique_subjects_count": int
            Total number of unique subjects (subject-predicate-object triples).
        - "unique_predicates_count": int
            Number of unique predicates.
        - "unique_objects_count": int
            Number of unique objects.
        - "quality_score": int
            Final “percentage” quality score (0–100).
        - "quality_score_10": float
            Quality score scaled to a 10-point system.
        - "value_score_10": int
            “Value” score, calculated based on unique subjects, predicates, and objects.

    Notes
    -----
    1. Loads the RDF graph using rdflib (format "turtle").
    2. Checks required prefixes ("rdfs", "skos", "NEW_PREF_CODE").
       - If not declared, registers them in missing_prefixes.
       - If declared but never used, registers them in unused_prefixes.
    3. Checks concept consistency: presence of SKOS.prefLabel, SKOS.inScheme, etc.
    4. Produces final scores (score, quality_score_10, value_score_10), reducing points for “problems”
       and considering diversity (SKOS.notation), external links (RDFS.seeAlso, SKOS.exactMatch), etc.

    Examples
    --------
    >>> report = check_rdf_quality("example_model.ttl")
    >>> print(report["quality_score"], report["missing_prefixes"])
    85 ['NEW_PREF_CODE']
    """
    g = Graph()
    g.parse(file_path, format="turtle")

    NEW_NS = Namespace(f"{NEW_PURL}")

    # Check 1: Required prefixes
    required_prefixes = {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        f"{NEW_PREF_CODE}": f"{NEW_PURL}/code#"
    }
    declared_prefixes = {prefix: uri for prefix, uri in g.namespaces()}
    missing_prefixes = []
    for ns, uri in required_prefixes.items():
        if ns not in declared_prefixes and uri not in declared_prefixes.values():
            missing_prefixes.append(ns)

    # Check 2: Prefix usage
    unused_prefixes = [ns for ns, uri in required_prefixes.items()
                       if all(uri not in str(s) for s in g)]

    # Check 3: Concept structure
    concepts = list(g.subjects(RDFS.subClassOf, SKOS.Concept))
    missing_labels = [concept for concept in concepts if not list(g.objects(concept, SKOS.prefLabel))]

    # Check 4: Agency links (NEW_NS.hasAgencyLabel)
    agency_labels = list(g.objects(None, NEW_NS.hasAgencyLabel))
    missing_agency_links = [label for label in agency_labels if not list(g.objects(label, RDFS.label))]

    # Check 5: Presence of skos:inScheme
    inconsistent_concepts = [concept for concept in concepts if not list(g.objects(concept, SKOS.inScheme))]

    # Check 6: Diversity (SKOS.notation)
    diverse_notations = len(set(g.objects(None, SKOS.notation)))

    # Check 7: Descriptive labels (RDFS.comment)
    descriptive_labels = len([concept for concept in concepts if list(g.objects(concept, RDFS.comment))])

    # Check 8: Interoperability (RDFS.seeAlso, SKOS.exactMatch)
    external_links = len(list(g.objects(None, RDFS.seeAlso))) + len(list(g.objects(None, SKOS.exactMatch)))

    # Count unique subjects, predicates, objects
    unique_subjects = set(g.subjects())
    unique_predicates = set(g.predicates())
    unique_objects = set(g.objects())

    # Final quality score calculation
    score = 100
    if missing_prefixes:
        score -= 10
    if unused_prefixes:
        score -= 10
    if missing_labels:
        score -= 30
    if missing_agency_links:
        score -= 20
    if inconsistent_concepts:
        score -= 30
    if diverse_notations < 5:
        score -= 10
    if descriptive_labels == 0:
        score -= 15
    if external_links == 0:
        score -= 15

    # Scale score to 10-point system (quality_score_10)
    quality_score_10 = round(
        (100 - (
            len(missing_prefixes) * 1
            + len(unused_prefixes) * 1
            + len(missing_labels) * 3
            + len(inconsistent_concepts) * 2
        ))
        / 10,
        1
    )

    # Calculate value_score_10 based on unique entities
    value_score_10 = min(10, int((len(unique_predicates) + len(unique_subjects) + len(unique_objects)) / 10))

    if quality_score_10 > 10:
        quality_score_10 = 10
    if value_score_10 > 10:
        value_score_10 = 10

    report = {
        "missing_prefixes": missing_prefixes,
        "unused_prefixes": unused_prefixes,
        "missing_labels": missing_labels,
        "missing_agency_links": missing_agency_links,
        "inconsistent_concepts": inconsistent_concepts,
        "diverse_notation_count": diverse_notations,
        "descriptive_labels_count": descriptive_labels,
        "external_links_count": external_links,
        "unique_subjects_count": len(unique_subjects),
        "unique_predicates_count": len(unique_predicates),
        "unique_objects_count": len(unique_objects),
        "quality_score": score,
        "quality_score_10": quality_score_10,
        "value_score_10": value_score_10
    }

    return report


def process_all_models(directory):
    """
    Iterates over the given directory and runs quality checks for all .ttl RDF models.

    Parameters
    ----------
    directory : str
        Path to the directory containing Turtle files to check.

    Returns
    -------
    dict
        A dictionary where the key is the filename (str),
        and the value is the final quality report (dict) (see check_rdf_quality).

    Notes
    -----
    1. Detects files with the .ttl extension and passes them to `check_rdf_quality`.
    2. Returns a summary report containing information about all checked models.

    Examples
    --------
    >>> reports = process_all_models("/path/to/rdf_folder")
    >>> for filename, report in reports.items():
    ...     print(filename, report["quality_score"])
    """
    reports = {}
    for filename in os.listdir(directory):
        if filename.endswith(".ttl"):
            file_path = os.path.join(directory, filename)
            report = check_rdf_quality(file_path)
            reports[filename] = report
    return reports
