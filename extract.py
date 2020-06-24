import argparse
import PyPDF2
import pdfminer
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
        test_path = test_path + " extracted pdfs"

        ends_in_a_number: bool

        try:
            last_number = test_path.split()[-1]
            iteration_number = int(last_number)

        except (ValueError, IndexError):
            iteration_number = 1
            ends_in_a_number = False
        else:
            ends_in_a_number = True

        print("    Checking if there is already a directory by the same name as the new directory...")
        print("    Generating name...")
        while Path(test_path).exists():
            if ends_in_a_number:
                test_path = test_path[:-1].strip()

            test_path = test_path + " " + str(iteration_number + 1)
            ends_in_a_number = True

            iteration_number += 1

        final_path = Path(test_path)
    print("    Output directory name generated as", str(final_path) + ".")
    return final_path


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


def create_output_directory(output_path: Path, mode: str):
    print("Creating output directory...")
    output_path.mkdir(get_mode(mode))


def extract_text(pdf_paths: [Path], output_path: Path, input_mode: int):
    for pdf_path in pdf_paths:
        txt_path = output_path.joinpath(pdf_path.stem + ".txt")
        txt_path.touch(get_mode(input_mode), False)

        pdf_reader = PyPDF2.PdfFileReader(str(pdf_path))
        page_max_index = pdf_reader.getNumPages() - 1
        page: int = 0
        extracted_text: str = ""
        while page <= page_max_index:
            extracted_text += "\n\n" + pdf_reader.getPage(page).extractText()
            page += 1
        txt_path.write_text(extracted_text)
    print("Done!")


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

    if len(pdfs) > 0 and args.nd:
        create_output_directory(output_dir_path, args.mode)
    elif not (len(pdfs) > 0):
        print(Back.GREEN + Fore.BLACK + Style.BRIGHT + "No PDFs found in", args.input + Style.RESET_ALL)
        exit(0)
    elif (not args.nd) and args.mode:
        print(
            Back.YELLOW + Fore.BLACK + Style.BRIGHT + "Mode preference will be ignored, since a new directory was not "
                                                      "requested." + Style.RESET_ALL)
    extract_text(pdfs, output_dir_path, args.mode)
