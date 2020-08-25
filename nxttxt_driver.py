import unzip
import extract
import poster
import argparse
from pathlib import Path


def unzip_drive(unzip_input: str, output: str, nd: bool):
    auth = unzip.authenticate_instructional_validity(unzip_input, output)
    if auth[0]:
        output_path: Path = unzip.generate_output_path(unzip_input, output, nd)
        unzip.create_output_directory(output_path, output, nd)
        unzip.unzip_file(unzip_input, output_path, nd)
    else:
        print(auth[1])
        exit(1)


def extract_drive(extract_input: str) -> list:
    if Path(extract_input).exists() and Path(extract_input).is_dir():
        pdfs = extract.determine_pdfs(extract_input)
        paths_list = extract.create_path_objects(pdfs, Path(""))
        extractions_paths = extract.extract_text(paths_list, None)
        for file in Path(extract_input).iterdir():
            file.unlink()
        Path(extract_input).rmdir()
        return extractions_paths
    else:
        print("Analysis failed due to missing pdf cache.")
        exit(1)


def poster_drive(poster_input: str, output: str, nd: bool, port: int, address: str):
    output_url = poster.determine_url(address, port)
    analysis = poster.analyze_txts(files, output_url)
    output_path = poster.determine_output_path(poster_input, output, nd)

    poster.create_output_dir(output_path)
    poster.create_files(analysis, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts text from all PDFs in a directory.")
    parser.add_argument("input", metavar="Input directory path", type=str, help="Path of directory with PDF Zips to "
                                                                                "analyze.")
    parser.add_argument("-output", metavar="Output directory path", type=str, help="Path of directory to place "
                                                                                   "analysis files into (Defaults to "
                                                                                   "same as input).")
    parser.add_argument("-address", metavar="Server address", type=str, help="Address of server on which the sa-engine "
                                                                             "is running.")
    parser.add_argument("-p", metavar="Server port", type=int, help="Port of server on which the sa-engine is running "
                                                                    "(Defaults to 8080).")
    parser.add_argument("-nd", action="store_true", help="Places analyzed text files into new directory with same "
                                                         "name as original directory but with 'analyzed txts' on the "
                                                         "end(Defaults to false).")

    args = parser.parse_args()

    pdfs_cache_path = Path("nxttxt_driver cache/")
    if not pdfs_cache_path.exists():
        pdfs_cache_path.mkdir()

    unzip_drive(args.input, pdfs_cache_path, args.nd)
    extraction = extract_drive(pdfs_cache_path)
    print(extraction)
