import time
import argparse
import zipfile
import nxttxt
from pathlib import Path

startTime = time.time()


def generate_output_path(input_file: str, manual_path: str) -> Path:
    print("Generating Output Path...")
    input_path = Path(input_file)
    print("    Checking if zipfile exists...")
    if not input_path.exists():
        print(input_file, "is not a valid file path.")
        exit(1)
    if manual_path and (not Path(manual_path).is_dir()):
        print(manual_path, "is not a valid output directory.")
        exit(1)

    final_path: Path
    if not new_dir:
        if manual_path:
            final_path = Path(manual_path)
        else:
            final_path = input_path.parent
    else:
        test_path: Path
        if manual_path:
            print("    Generating path from manual input and zipfile name.")
            test_path = Path(manual_path).joinpath(input_path.stem)
        else:
            print("    Removing file extension...")
            test_path = input_path.with_suffix('')
        final_path = nxttxt.enumerate_duplicate_paths(test_path)
    return final_path


# Create output folder
def create_output_directory(output_file: Path):
    if new_dir:
        print("Creating output directory...")
        output_file.mkdir()
        print("    Output directory created.")


# Unzip documents into folder
def unzip_file(input_file: str, output_file: Path):
    print("Unzipping files into output directory...")
    try:
        print("    Extracting...")
        zipfile.ZipFile(input_file, 'r').extractall(output_file)

    except (zipfile.BadZipFile, FileNotFoundError):
        print(input_file, "does appear to be a valid zip file.")
        if new_dir:
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

    # Use inputs to unzip file correctly
    output_path: Path = generate_output_path(Path(zip_file_path), output_file_path)
    create_output_directory(output_path)
    unzip_file(zip_file_path, output_path)
