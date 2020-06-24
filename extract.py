import argparse
import PyPDF2
from pathlib import Path
from colorama import Fore, Back, Style


# "Modular" functions (used multiple times each)
def get_mode(input_mode: str):
    output_mode: int = 0o777
    if input_mode:
        try:
            int(input_mode)
        except ValueError:
            print(Back.RED + Fore.BLACK + Style.BRIGHT + input_mode,
                  "is not a valid unix permission level." + Style.RESET_ALL)
            exit(1)
        else:
            output_mode = int("0o" + input_mode)
    return output_mode


def enumerate_duplicate_path(start_path: str):
    test_path = str(Path(start_path).with_suffix(''))
    start_suffixes = Path(start_path).suffixes
    end_suffix = "".join(start_suffixes)

    ends_in_a_number: bool

    try:
        last_number = test_path.split()[-1]
        iteration_number = int(last_number)

    except (ValueError, IndexError):
        iteration_number = 1
        ends_in_a_number = False
    else:
        ends_in_a_number = True

    print("    Generating name...")
    while (Path(test_path).with_suffix(end_suffix)).exists():
        if ends_in_a_number:
            test_path = test_path[:-1].strip()
        test_path += " " + str(iteration_number + 1)
        ends_in_a_number = True
        iteration_number += 1
    end_path = Path(test_path).with_suffix(end_suffix)
    return end_path


# Procedure functions(called once each)
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
            pdfs_working_list.append(child.absolute())

    print("PDFs list compiled.")
    return pdfs_working_list


def generate_output_path(input_path: Path, manual_path: str, new_dir: bool):
    print("Generating Output Path...")

    if manual_path and (not Path(manual_path).is_dir()):
        print(Back.RED + Fore.BLACK + Style.BRIGHT + manual_path, "is not a valid output directory." + Style.RESET_ALL)
        exit(1)

    final_path: Path
    if not new_dir:
        if manual_path:
            final_path = Path(manual_path)
        else:
            final_path = input_path
    else:
        parent_path: Path
        if manual_path:
            print("    Generating path from manual input and directory name.")
            parent_path = Path(manual_path)
        else:
            parent_path = input_path
        test_path = str(parent_path.joinpath(input_path.stem))
        test_path += " extracted pdfs"

        final_path = enumerate_duplicate_path(test_path)
    print("    Output directory name generated as", str(final_path) + ".")
    return final_path


def create_output_directory(output_path: Path, mode: str, pdfs_list: list, new_dir: bool):
    print("Creating output directory...")
    if len(pdfs_list) > 0 and args.nd:
        output_path.mkdir(get_mode(mode))
        print("Output directory created.")
    elif not (len(pdfs_list) > 0):
        print(Back.GREEN + Fore.BLACK + Style.BRIGHT + "No PDFs found in", args.input + Style.RESET_ALL)
        exit(0)
    elif (not new_dir) and mode:
        print(
            Back.YELLOW + Fore.BLACK + Style.BRIGHT + "Mode preference will be ignored, since a new directory was not "
                                                      "requested." + Style.RESET_ALL)


def extract_text(pdf_paths: [Path], output_path: Path, input_path: str, input_mode: str):
    print("Extracting text...")
    for pdf_path in pdf_paths:
        txt_path = enumerate_duplicate_path(str(output_path.joinpath(Path(pdf_path.stem).with_suffix(".txt"))))
        txt_path.touch(get_mode(input_mode), False)
        print("   ", pdf_path, "->", txt_path)

        pdf_reader = PyPDF2.PdfFileReader(str(pdf_path))
        try:
            page_max_index = pdf_reader.getNumPages() - 1
        except PyPDF2.PdfReadError:
            print(Back.YELLOW + Fore.BLACK + Style.BRIGHT + "    There was a error reading", pdf_path, "so it will be "
                                                                                                       "skipped.",
                  " Check if the file is encrypted." + Style.RESET_ALL)
            txt_path.rmdir()
        else:
            page: int = 0
            extracted_text: str = ""
            while page <= page_max_index:
                extracted_text += "\n\n" + pdf_reader.getPage(page).extractText()
                page += 1
            txt_path.write_text(extracted_text)

    print(Back.GREEN + Fore.BLACK + Style.BRIGHT + "All pdfs in", input_path, "extracted to", str(output_path) + Style.RESET_ALL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts text from all PDFs in a directory.")
    parser.add_argument("input", metavar="Input directory path", type=str, help="Path of directory with PDFs to "
                                                                                "extract.")
    parser.add_argument("--output", metavar="Output directory path", type=str, help="Path of directory to extract "
                                                                                    "files to (Defaults to same as "
                                                                                    "input).")
    parser.add_argument("-nd", action="store_true", help="Places extracted text files into new directory with same "
                                                         "name as pdf file(Defaults to false).")
    parser.add_argument("--mode", metavar="Permission", type=str, help="Unix permission level for new directory ("
                                                                       "Defaults to 777)")
    args = parser.parse_args()

    pdfs = determine_pdfs(Path(args.input))
    output_dir_path = generate_output_path(Path(args.input), args.output, args.nd)

    create_output_directory(output_dir_path, args.mode, pdfs, args.nd)

    extract_text(pdfs, output_dir_path, args.input, args.mode)
