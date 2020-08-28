from pathlib import Path
import argparse
import textract
import PyPDF2
import signal
import nxttxt
import time


# "Procedural" functions(called once each)
def authenticate_instructional_validity(input_dir: str, output_dir: str) -> list:
    print("Authenticate validity of entered paths...")
    input_path = Path(input_dir)
    if nxttxt.is_valid_path(input_path, True) and output_dir and (not nxttxt.is_valid_path(output_dir,
                                                                                           True)):
        result = [False, "The specified output path is not valid.", nxttxt.exceptions.InvalidPath]
    elif not nxttxt.is_valid_path(input_path, False):
        result = [False, "The specified input path is not valid.", nxttxt.exceptions.InvalidPath]
    elif not nxttxt.is_valid_path(input_path, True):
        result = [False, "The specified input path is not a directory.", nxttxt.exceptions.PathIsNotADirectory]
    else:
        result = [True, None]
        print("Validity authenticated.")
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

    print("    PDFs list compiled.")
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


def create_output_directory(output_path: Path, input_str: str, pdfs_list: list, nd: bool):
    print("Creating output directory...")
    pdfs_list_count: int = len(pdfs_list)
    if pdfs_list_count > 0 and nd:
        output_path.mkdir()
        print("    Output directory created.")
    elif not (pdfs_list_count > 0):
        print("    No PDFs found in", input_str)
        raise nxttxt.exceptions.NoPDFsLocated


def create_path_objects(pdf_paths: list, final_output_file: Path) -> list:
    print("Compiling PDF and Txts paths")
    paths: list = []
    for pdf_path in pdf_paths:
        txt_path = nxttxt.enumerate_duplicate_paths(final_output_file / Path(pdf_path.stem).with_suffix(".txt"))
        paths.append({
            "pdf": pdf_path,
            "txt": txt_path
        })
    print("    Paths compiled.")
    return paths


def extract_text(paths: list, max_extraction_time: int) -> list:
    print("Extracting text...")
    extraction_list = []
    for path in paths:
        if max_extraction_time:
            signal.signal(signal.SIGALRM, nxttxt.alarm_handler)
            signal.alarm(max_extraction_time)
        start_time = time.time()
        try:
            extracted_text: str = textract.process(path["pdf"], method="pdfminer")
            completion_time = time.time() - start_time
        except nxttxt.exceptions.ExtractionTimeOut:
            incomplete_time = time.time() - start_time
            print("   ", path["pdf"], "timed out after", incomplete_time, "seconds.")
        except (textract.parsers.exceptions.ShellError, textract.parsers.exceptions.ExtensionNotSupported):
            print("    There was a error reading", path["pdf"], "the file may be corrupted so it will be skipped.")
        else:
            print("   ", path["pdf"], "extracted in", completion_time, "seconds.")
            path["extractions"] = str(extracted_text)
            extraction_list.append(path)
        signal.alarm(0)
    print("    All PDFs extracted.")
    return extraction_list


def touch_and_write_files(paths: list):
    print("Writing extractions to txts")
    for path in paths:
        path["txt"].touch()
        path["txt"].write_text(path["extractions"])
    print("    All PDFs extractions written to ", str(paths[0]["txt"].parent))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts text from all PDFs in a directory.")
    parser.add_argument("input", metavar="Input directory path", type=str, help="Path of directory with PDFs to "
                                                                                "extract.")
    parser.add_argument("-output", metavar="Output directory path", type=str, help="Path of directory to extract "
                                                                                   "files to (Defaults to same as "
                                                                                   "input).")
    parser.add_argument("-nd", action="store_true", help="Places extracted text files into new directory with same "
                                                         "name as pdf file(Defaults to false).")
    parser.add_argument("-timeout", metavar="Extraction time limit", type=int, help="Restricts the time for the "
                                                                                    "extractions of each PDF to the "
                                                                                    "inputted value in seconds.")
    args = parser.parse_args()

    auth = authenticate_instructional_validity(args.input, args.output)
    if auth[0]:
        pdfs = determine_pdfs(args.input)
        output_dir_path = generate_output_path(Path(args.input), args.output, args.nd)

        create_output_directory(output_dir_path, args.input, pdfs, args.nd)
        paths_list = create_path_objects(pdfs, output_dir_path)
        extractions_paths = extract_text(paths_list, args.timeout)
        touch_and_write_files(extractions_paths)
    else:
        print(auth[1])
        raise auth[2]
