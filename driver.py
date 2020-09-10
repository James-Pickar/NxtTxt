import unzip
import extract
import poster
import argparse
import nxttxt
from pathlib import Path


def unzip_drive(unzip_input: str, cache: str, output):
    cache_path = Path(cache)
    if not cache_path.exists():
        cache_path.mkdir()
    else:
        nxttxt.clear_directory(cache_path, False)

    auth = unzip.authenticate_instructional_validity(unzip_input, output)
    if auth[0]:
        unzip.unzip_file(unzip_input, cache_path, True)
    else:
        nxttxt.clear_directory(cache_path, True)
        print(auth[1])
        raise auth[2]


def extract_drive(extract_input: str, timeout: int) -> list:
    if Path(extract_input).exists() and Path(extract_input).is_dir():
        # Extract text from PDF cache
        pdfs = extract.determine_pdfs(extract_input)
        paths_list = extract.create_path_objects(pdfs, Path(""))
        extractions_paths = extract.extract_text(paths_list, timeout)

        # Empty and delete PDF cache
        nxttxt.clear_directory(Path(extract_input), True)

        return extractions_paths
    else:
        print("Analysis failed due to missing pdf cache.")
        raise nxttxt.exceptions.NoPDFsLocated


def poster_drive(poster_inputs: list, origin_path: str, output: str, nd: bool, port: int, address: str):
    poster_list = []
    for poster_input in poster_inputs:
        poster_list.append({
            "txt_path": Path(poster_input["pdf"].name),
            "data": poster_input["extractions"]
        })
    output_url = poster.determine_url(address, port)
    analysis = poster.analyze_txts(poster_list, output_url)
    output_path = poster.determine_output_path(origin_path, output, nd)

    poster.create_output_dir(output_path)
    poster.create_files(analysis, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts text from all PDFs in a directory.")
    parser.add_argument("input", metavar="Input directory path", type=str, help="Path of directory with PDF Zips to "
                                                                                "analyze.")
    parser.add_argument("address", metavar="Server address", type=str, help="Address of server on which the sa-engine "
                                                                            "is running.")
    parser.add_argument("-output", metavar="Output directory path", type=str, help="Path of directory to place "
                                                                                   "analysis files into (Defaults to "
                                                                                   "same as input).")
    parser.add_argument("-p", metavar="Server port", type=int, help="Port of server on which the sa-engine is running "
                                                                    "(Defaults to 8080).")
    parser.add_argument("-nd", action="store_true", help="Places analyzed text files into new directory with same "
                                                         "name as original directory but with 'analyzed txts' on the "
                                                         "end(Defaults to false).")
    parser.add_argument("-timeout", metavar="Extraction time limit", type=int, help="Restricts the time for the "
                                                                                    "extractions of each PDF to the "
                                                                                    "inputted value in seconds.")

    args = parser.parse_args()
    pdfs_cache_path = Path("nxttxt_driver cache/")

    unzip_drive(args.input, pdfs_cache_path, args.output)
    extractions = extract_drive(pdfs_cache_path, args.timeout)
    poster_drive(extractions, args.input, args.output, args.nd, args.p, args.address)
