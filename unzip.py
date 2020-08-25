import time
import nxttxt_module
import zipfile
import argparse
from pathlib import Path

startTime = time.time()


def authenticate_instructional_validity(input_file: str, manual_output: str) -> list:
    input_path = Path(input_file)
    if not nxttxt_module.is_valid_path(input_path, False):
        return [False, "The input path entered is not valid."]
    elif nxttxt_module.is_valid_path(input_path, True):
        return [False, "The input path entered is a directory not a file."]
    elif not nxttxt_module.is_valid_path(Path(manual_output), True):
        return [False, "The specified output path is not valid."]
    else:
        return [True, None]


def generate_output_path(input_file: str, manual_path: str, nd: bool) -> Path:
    print("Generating Output Path...")
    input_path = Path(input_file)
    if manual_path:
        if nd:
            print("New directory request will be ignored since an output path was chosen manually.")
        return Path(manual_path)
    if nd:
        return nxttxt_module.enumerate_duplicate_paths(input_path.with_suffix(''))
    return input_path.parent


# Create output folder
def create_output_directory(output_file: Path, manual_dir: str, nd: bool):
    if nd and (not manual_dir):
        print("Creating output directory...")
        output_file.mkdir()
        print("    Output directory created.")


# Unzip documents into folder
def unzip_file(input_file: str, output_file: Path, nd: bool):
    print("Unzipping files into output directory...")
    try:
        print("    Extracting...")
        zipfile.ZipFile(input_file, 'r').extractall(output_file)

    except (zipfile.BadZipFile, FileNotFoundError):
        print(input_file, "does appear to be a valid zip file.")
        if nd:
            output_file.rmdir()
        exit(1)
    print("    ", input_file, " unzipped to ", str(output_file), " in ", time.time() - startTime, "seconds (including "
                                                                                                  "user input).")


if __name__ == "__main__":
    # Process arguments from call
    parser = argparse.ArgumentParser(description="Unzips files.")
    parser.add_argument("input", metavar="Zip file path", type=str, help="Path of file to unzip")
    parser.add_argument("--output", metavar="Output directory path", type=str,
                        help="Path of directory to unzip files to (Defaults to same as input).")
    parser.add_argument("-nd", action="store_true",
                        help="Places unzipped files into new directory with same name as zip file(Defaults to false).")

    args = parser.parse_args()

    # Create input variables
    zip_file_path = args.input
    output_file_path = args.output
    new_dir = args.nd
    auth = authenticate_instructional_validity(zip_file_path, output_file_path)

    # Use inputs to unzip file correctly
    if auth[0]:
        output_path = generate_output_path(zip_file_path, output_file_path, new_dir)
        create_output_directory(output_path, output_file_path, new_dir)
        unzip_file(zip_file_path, output_path, new_dir)
    else:
        print(auth[1])
