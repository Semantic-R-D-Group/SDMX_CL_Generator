# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

import requests
import re

def download_xml(url, filename):
    """
    Function for downloading an XML file from a given URL and saving it to a local file.

    Parameters
    ----------
    url : str
        The link to the XML file to download.
    filename : str
        The name of the local file where the downloaded content will be saved.

    Returns
    -------
    bool
        Returns True if the file was successfully downloaded and saved, otherwise False.

    Raises
    ------
    requests.RequestException
        Raised in case of HTTP request issues (invalid URL,
        timeout, no connection, etc.).

    Notes
    -----
    1. Uses the `requests.get` method for downloading.
    2. On failure, prints an error message to the console.

    Examples
    --------
    >>> success = download_xml("https://example.com/data.xml", "data.xml")
    >>> print(success)
    True
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(response.content)
        return True
    except requests.RequestException as e:
        print(f"Download error {url}: {e}")
        return False


def urn_to_sdmx_url(urn):
    """
    Converts an SDMX-style URN string into a URL for the SDMX REST API.

    Parameters
    ----------
    urn : str
        The URN string representing an SDMX structure.
        The format must match the pattern:
        'urn:sdmx:org.sdmx.infomodel.codelist.Codelist=AGENCY:ID(version)'

    Returns
    -------
    str
        URL generated from the given URN, used to query the SDMX REST API.

    Raises
    ------
    ValueError
        If the URN format does not match the expected regex.

    Notes
    -----
    - A regular expression is used to parse the URN parts.
    - Currently designed for the new SDMX REST API format.

    Examples
    --------
    >>> urn_example = "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=ESTAT:CL_COVERAGE_POP(1.1.0)"
    >>> print(urn_to_sdmx_url(urn_example))
    https://registry.sdmx.org/sdmx/v2/structure/codelist/ESTAT/CL_COVERAGE_POP/1.1.0
    """
    pattern = r"urn:sdmx:org\.sdmx\.infomodel\.codelist\.Codelist=([^:]+):([^()]+)\(([\d.]+)\)"
    match = re.match(pattern, urn)

    if not match:
        raise ValueError("Invalid URN format")

    agency, id_code, version = match.groups()

    base_url = "https://registry.sdmx.org/sdmx/v2/structure/codelist"
    url = f"{base_url}/{agency}/{id_code}/{version}"
    return url


def get_sdmx_object(urn):
    """
    Requests an SDMX object by converting the given URN to a URL.
    Local function for conversion testing.

    Parameters
    ----------
    urn : str
        The URN string used to form the SDMX request URL.

    Returns
    -------
    str
        The text response (usually XML) from the SDMX server if the request succeeds.
        If an error occurs (status code not 200), an error message is returned.

    Notes
    -----
    1. Calls `urn_to_sdmx_url` inside to convert the URN into a URL.
    2. Uses the header Accept: application/xml, expecting XML in response.
    3. If the response code is not 200, a message
       "Error: status_code - status_code - response_text" is returned.

    Examples
    --------
    >>> urn = "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=ESTAT:CL_COVERAGE_POP(1.1.0)"
    >>> result = get_sdmx_object(urn)
    >>> print(result)  # Prints XML data or error message.
    """
    url = urn_to_sdmx_url(urn)
    print(f"Requesting URL: {url}")
    response = requests.get(url, headers={"Accept": "application/xml"})
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code} - {response.status_code} - {response.text}"


if __name__ == '__main__':
    # Example URN
    urn = "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=ESTAT:CL_COVERAGE_POP(1.1.0)"

    sdmx_data = get_sdmx_object(urn)
    print(sdmx_data)
