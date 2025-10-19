# SDMX Semantic Code List Generator (TTL)

Generation of semantic models of SDMX code lists in RDF/Turtle (TTL) format with the ability to load source SDMX XML and analysis utilities.

The project automates three stages:

1. **Download** XML code list files from SDMX endpoints specified in a CSV.
2. **Analyze** downloaded code lists and generate summary CSV tables.
3. **Generate** cleaned RDF/Turtle ConceptSchemes and Concepts for each code list (as well as a combined `code.ttl`).

---

## Features

- **CSV input** (`in/Code_Lists_GR_SDMX.csv`, delimiter `;`)
- **XML download** with error handling (via `requests`)
- **Advanced analysis**: CSV tables for codes and codelists; grouping of "multiple codelists per agency"
- **RDF/Turtle generation** using `rdflib`, consistent prefixes, and new persistent URIs
- **Quality check** of TTL (prefixes, labels, schema consistency). Ratings are displayed and a `codelists_with_hasAgencyLabel.csv` file is generated for audit.

---

## Project Structure

```
SDMX_CL_Generator/
├── in/
│   └── Code_Lists_GR_SDMX.csv          # Input table with SDMX codelist sources (agency_id;codelistID;Name;URL)
├── sdmx_codelists/                      # (created) Downloaded SDMX XML codelists
├── analysis/                            # (created) CSV analysis results
│   ├── all_cl_data.csv                  # Full code table
│   ├── cl_table.csv                     # Summary codelist table (counts, etc.)
│   ├── filtered_cl_data.csv             # Filtered codes
│   └── filtered_cl_table.csv            # Summary table of filtered codelists
├── cl_out/                         # (created) TTL files (per scheme and general code.ttl)
├── src/sdmxclgen/                       # Library package
│   ├── analyze_sdmx_cl.py               # Main analysis pipeline
│   ├── analyze_func.py                  # Helper analysis functions
│   ├── analyze_templates.py             # Codelist grouping templates
│   ├── download_xml_gr_cl.py            # `download_xml()` and helper functions
│   ├── gen_cl_ttl.py                    # TTL generation (`sdmx_codelist_gen()`, `generation_ttl()`)
│   ├── gen_template.py                  # Prefixes, NEW_* constants, SINGLES definition
│   ├── get_analyze_func.py              # Helpers (prefix parsing, grouping, etc.)
│   ├── get_funcs.py                     # RDF generation (schemes, concepts, URIs)
│   ├── quality_check.py                 # TTL quality checks
│   └── templates.py                     # Constants: column names, SDMX namespaces
├── main.py                              # CLI entry point for three stages
└── requirements.txt
```

> **Note:** The project may contain IDE/virtual environment artifacts (e.g., `.idea/`, `.venv/`) and previously generated outputs (`analysis/`, `cl_out/`, `sdmx_codelists/`). They are not needed for a clean run.

---

## Installation

The project requires **Python 3.11+** (tested with 3.12).

```bash
# 1) Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: source .venv\Scripts\activate

# 2) Update pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `requirements.txt` was exported from another platform and contains extra symbols,
list the packages manually (minimal set):

```text
certifi
charset-normalizer
idna
numpy
pandas
pyparsing
python-dateutil
pytz
rdflib
requests
six
tzdata
urllib3
```

---

## Input Data

A CSV file with delimiter `;` must be prepared at `in/Code_Lists_GR_SDMX.csv` with **exactly these** columns (header required):

| Column      | Description                                    |
|-------------|------------------------------------------------|
| `agency_id` | Agency identifier (e.g., `ESTAT`, `SDMX`)      |
| `codelistID`| SDMX codelist identifier                       |
| `Name`      | Human-readable codelist name                   |
| `URL`       | SDMX endpoint for XML retrieval                |

> Column names are defined in `src/sdmxclgen/templates.py` (`DF_CL_SOURCE`).

---

## Usage

First set the project folder and file paths in `main.py`:

```python
    # Paths to data and directories
    input_cl_path = Path("in/Code_Lists_GR_SDMX.csv")  # CSV file with codelist URLs
    xml_download_dir = Path("sdmx_codelists")  # Folder for downloaded XML
    ...
    # Paths to analysis files
    analysis_dir = Path("analysis")     
    full_cl_csv = analysis_dir / "all_cl_data.csv"      
    cl_table_csv = analysis_dir / "cl_table.csv"        
    filtered_cl_csv = analysis_dir / "filtered_cl_data.csv"     
    filtered_cl_table_csv = analysis_dir / "filtered_cl_table.csv"      
    ...
    # RDF model generation
    out_dir = Path("cl_out")
```

Run **all** stages of the SDMX code list semantic model generation cycle through `main.py`. Use the following flags:

* `--enable_xml_download` - Flag to enable XML download
* `--enable_code_list_analysis` - Flag to enable codelist analysis

Example:

```bash
# Download XML + Analyze + Generate TTL
python main.py --enable_xml_download True --enable_code_list_analysis True
```

You can also run separate stages:

1) **Only XML download**

```bash
python main.py --enable_xml_download True --enable_code_list_analysis False
```

Files are saved in `sdmx_codelists/` as `N-CODELISTID.xml`.

2) **Only analysis** (if XML already downloaded)

```bash
python main.py --enable_xml_download False --enable_code_list_analysis True
```

Creates/updates CSVs in `analysis/` and prints "multiple codelists per agency" groupings.

### **TTL Generation**

Generation always runs at the end of `main.py`. It uses CSV analysis results and writes to `cl_out/`:

- TTL files of enriched semantic models of code lists
- Combined `code.ttl` (all code lists with consistent prefixes)

---

## Results

- `sdmx_codelists/*.xml` — raw SDMX XML codelists
- `analysis/all_cl_data.csv` — denormalized table of codes
- `analysis/cl_table.csv` — one row per codelist with basic statistics
- `analysis/filtered_cl_data.csv` / `analysis/filtered_cl_table.csv` — filtered versions (per analysis logic)
- `cl_out/*.ttl` — generated ConceptSchemes and SKOS concepts
- `cl_out/code.ttl` — combined TTL with all codes and prefixes
- (optional) `codelists_with_hasAgencyLabel.csv` — audit of `sip-sdmx:hasAgencyLabel` values

> TTL generation is performed by `sdmx_codelist_gen()` in `src/sdmxclgen/gen_cl_ttl.py`. The module collects prefixes from `gen_template.PREF_COM_SET` and SDMX constants from `templates.py`, and applies quality checks from `quality_check.py` (ratings are printed to the console).

---

## Key Prefixes

Generated TTL files use stable URIs predefined in `src/sdmxclgen/gen_template.py`. For example:

- `NEW_PREF` = `sip-sdmx`
- `NEW_PURL` = `https://purl.semanticip.org/linked-data/sdmx`
- `NEW_PREF_CODE` = `sip-sdmx-code`
- `NEW_PURL_CODE` = `https://purl.semanticip.org/linked-data/sdmx/code/`

When generating semantic models of SDMX code lists, `skos:exactMatch` links are established with codes from the [sdmx-code:](http://purl.org/linked-data/sdmx/2009/code#) namespace.

All prefixes and URIs are defined in `src/sdmxclgen/gen_template.py` and `src/sdmxclgen/templates.py`.

---

## Development

- Project code is located in `src/sdmxclgen`. Entry point is `main.py`.
- Column name constants must be synchronized with writing functions (see comments in `parse_save_cl.py`).
- To add new codelist families or grouping rules, extend `analyze_templates.py` and helper functions.
- For new prefixes/URIs, update `gen_template.py` and `templates.py`.

### Linters and formatting (recommended)

```bash
pip install ruff black
ruff check src
black src
```

### Mini-tests

The project includes checks in `quality_check.py`, which can be called directly:

```bash
python -c "from src.sdmxclgen.quality_check import check_rdf_quality; print(check_rdf_quality('cl_out/code.ttl'))"
```

---

## License

### Code
The source code of this project is licensed under the **Apache License 2.0**.  
See the [LICENSE](LICENSE) file for details.

### Generated data
The generated datasets, RDF/TTL files, and code lists produced by this tool
are licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.  
See the [DATA_LICENSE](DATA_LICENSE) file or visit  
<https://creativecommons.org/licenses/by/4.0/> for the full license text.

**Attribution:**  
This project includes or derives from materials © [SDMX Community](https://sdmx.org)  
(Statistical Data and Metadata eXchange).  
Original materials are licensed under CC BY 4.0.  
Modifications by © 2025 *Semantic R&D Group* —  
automatic RDF/TTL generation and semantic enrichment.

### Third-party libraries
This project uses open-source Python packages under permissive licenses  
(BSD, MIT, Apache 2.0, MPL 2.0).  
See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for details.

---

**Summary**

| Component | License | File |
|------------|----------|------|
| Code | Apache-2.0 | [`LICENSE`](LICENSE) |
| Generated data | CC BY 4.0 | [`DATA_LICENSE`](DATA_LICENSE) |
| Third-party libraries | BSD / MIT / Apache / MPL 2.0 | [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) |