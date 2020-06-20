import argparse
import PyPDF2
from pathlib import Path
from colorama import Fore, Back, Style


def determine_pdfs(input_path: Path):

    print("Reading input directory.")
    print("    Verifying input path is a readable directory...")
    if not input_path.exists():
        print(Back.RED + Fore.BLACK + Style.BRIGHT + str(input_path), "is not a valid file path." + Style.RESET_ALL)
        exit(1)
    elif not input_path.is_dir():
        print(Back.RED + Fore.BLACK + Style.BRIGHT + str(input_path), "is not a directory, it is either a file, or it "
                                                                      "is a broken symbolic link." + Style.RESET_ALL)
        exit(1)

    pdfs_working_list: list = []
    print("    Identifying PDF files...")
    for child in input_path.iterdir():
        try:
            PyPDF2.PdfFileReader(str(child))

        except (PyPDF2.utils.PdfReadError, IsADirectoryError):
            # Do nothing
            print("       ", str(child), "is not a PDF file.")
        else:
            print("       ", str(child), "is a PDF file.")
            pdfs_working_list.append(child)

    print("PDFs list compiled.")
    return pdfs_working_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts text from all PDFs in a directory.")
    parser.add_argument("input", metavar="Input directory path", type=str, help="Path of directory with PDFs to "
                                                                                "extract.")
    args = parser.parse_args()

    pdfs = determine_pdfs(Path(args.input))
