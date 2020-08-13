from pathlib import Path
import argparse
import PyPDF2
import nxttxt
import time


# "Procedural" functions(called once each)
def authenticate_instructional_validity(input_dir: str, output_dir: str) -> list:
    print("Authenticate validity of entered paths...")
    input_path = Path(input_dir)
    if nxttxt.is_valid_path(input_path, True) and (not nxttxt.is_valid_path(Path(output_dir), True)):
        result = [False, "The specified output path is not valid."]
    elif not nxttxt.is_valid_path(input_path, False):
        result = [False, "The specified output path is not valid."]
    elif not nxttxt.is_valid_path(input_path, True):
        result = [False, "The specified input path is not a directory."]
    else:
        result = [True, None]
    return result


def determine_pdfs(input_dir: str) -> list:
    print("Reading input directory...")
    input_path = Path(input_dir)
    pdfs_working_list: list = []
    print("    Identifying PDF files...")
    for child in input_path.iterdir():
        try:
            PyPDF2.PdfFileReader(str(child))

        except (PyPDF2.utils.PdfReadError, IsADirectoryError):
            print("       ", str(child), "is not a PDF file.")
        else:
            print("       ", str(child), "is a PDF file.")
            pdfs_working_list.append(child.absolute())

    print("PDFs list compiled.")
    return pdfs_working_list


def generate_output_path(input_dir: str, manual_path: str, new_dir: bool) -> Path:
    print("Generating Output Path...")
    input_path = Path(input_dir)
    final_path: Path
    if manual_path:
        final_path = Path(manual_path)
    elif new_dir:
        test_path = input_path.parent / (input_path.stem + " extracted pdfs")
        final_path = nxttxt.enumerate_duplicate_paths(test_path)
    else:
        final_path = input_path
    print("    Output path generated as", final_path, ".")
    return final_path


def create_output_directory(output_path: Path, pdfs_list: list):
    print("Creating output directory...")
    pdfs_list_count: int = len(pdfs_list)
    if pdfs_list_count > 0 and args.nd:
        output_path.mkdir()
        print("Output directory created.")
    elif not (pdfs_list_count > 0):
        print("No PDFs found in", args.input)
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts text from all PDFs in a directory.")
    parser.add_argument("input", metavar="Input directory path", type=str, help="Path of directory with PDFs to "
                                                                                "extract.")
    parser.add_argument("-output", metavar="Output directory path", type=str, help="Path of directory to extract "
                                                                                   "files to (Defaults to same as "
                                                                                   "input).")
    parser.add_argument("-nd", action="store_true", help="Places extracted text files into new directory with same "
                                                         "name as pdf file(Defaults to false).")
    parser.add_argument("-timeout", metavar="Extraction time limit", type=float, help="Restricts the time for the "
                                                                                      "extraction of each PDF to the "
                                                                                      "inputted value in seconds.")
    args = parser.parse_args()

    auth = authenticate_instructional_validity(args.input, args.output)
    if auth[0]:
        pdfs = determine_pdfs(args.input)
        output_dir_path = generate_output_path(Path(args.input), args.output, args.nd)

        create_output_directory(output_dir_path, pdfs)
        extract_text(pdfs, output_dir_path, args.input, args.timeout)
    else:
        print(auth[1])
