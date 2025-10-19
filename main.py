import pandas as pd
import argparse
from pathlib import Path
from src.sdmxclgen.download_xml_gr_cl import download_xml
from src.sdmxclgen.analyze_sdmx_cl import cl_analysis
from src.sdmxclgen.get_analyze_func import get_multiple_codelists_per_agency
from src.sdmxclgen.gen_cl_ttl import sdmx_codelist_gen

#if __name__ == '__main__':
def main():
    """Main script for downloading, analyzing, and generating RDF models of SDMX codelists.

    Uses command-line flags to select stages:
    - Download XML files with codelists
    - Analyze downloaded codelists
    - Generate RDF model in Turtle format

    Input:
    - CSV file with codelist URLs

    Output:
    - XML files of codelists
    - CSV files with analysis results
    - RDF files in TTL format
    """
    parser = argparse.ArgumentParser(description='Download XML codelists')
    parser.add_argument('--enable_xml_download', type=bool, default=False, help='Flag to enable XML download')
    parser.add_argument('--enable_code_list_analysis', type=bool, default=False, help='Flag to enable codelist analysis')
    args = parser.parse_args()

    # Paths to data and directorie
    input_cl_path = Path("in/Code_Lists_GR_SDMX.csv")  # CSV file with codelist URLs
    xml_download_dir = Path("sdmx_codelists")  # Folder for downloaded XML

    # Load codelists from CSV
    df = pd.read_csv(input_cl_path, delimiter=";")

    if args.enable_xml_download:
        # Create folder for XML files
        xml_download_dir.mkdir(parents=True, exist_ok=True)
        # Download codelists
        successful_downloads = 1
        for row in df.itertuples(index=False):
            url = row.URL
            codelist_id = row.codelistID
            xml_filename = xml_download_dir / f"{successful_downloads}-{codelist_id}.xml"

            # Download
            if download_xml(url, str(xml_filename)):
                successful_downloads += 1

        print(f"Done! Saved {successful_downloads - 1} XML files in {xml_download_dir}")

    # Paths to analysis files
    analysis_dir = Path("analysis")     # Folder for storing analysis results
    full_cl_csv = analysis_dir / "all_cl_data.csv"      # Full table with codes in CSV format
    cl_table_csv = analysis_dir / "cl_table.csv"        # Codelist table with code counts
    filtered_cl_csv = analysis_dir / "filtered_cl_data.csv"     # Reduced table with codes
    filtered_cl_table_csv = analysis_dir / "filtered_cl_table.csv"      # Reduced codelist table with code counts

    # Analyze main characteristics of codelists (--enable_code_list_analysis)
    if args.enable_code_list_analysis:
        if not analysis_dir.exists() :
            analysis_dir.mkdir(parents=True, exist_ok=True)
        if cl_analysis(xml_download_dir, full_cl_csv, cl_table_csv, filtered_cl_csv, filtered_cl_table_csv):
            print("\nAnalysis completed successfully")

        # Groups of codelists
        group_multiple_codelists = get_multiple_codelists_per_agency()
        for group_id, multiple_codelists in group_multiple_codelists.items():
            if multiple_codelists:
                print(f"Group: {group_id}")
                for agency, cls in multiple_codelists.items():
                    print(f"  Agency {agency}: {cls}")

    # RDF model generation
    out_dir = Path("cl_out")
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
    sdmx_codelist_gen(cl_table_csv, full_cl_csv, out_dir)

if __name__ == '__main__':
    main()
