import time
import argparse
import zipfile
from pathlib import Path
from colorama import Fore, Back, Style

startTime = time.time()


def generate_output_path(input_file: Path, manual_path: str):
    print("Generating Output Path...")
    print("    Checking if zipfile exists...")
    if not input_file.exists():
        print(Back.RED + Fore.BLACK + Style.BRIGHT + str(input_file), "is not a valid file path." + Style.RESET_ALL)
        exit(1)
    if manual_path and (not Path(manual_path).is_dir()):
        print(Back.RED + Fore.BLACK + Style.BRIGHT + manual_path, "is not a valid output directory." + Style.RESET_ALL)
        exit(1)

    final_path: Path
    if not new_dir:
        if manual_path:
            final_path = Path(manual_path)
        else:
            final_path = input_file.parent
    else:
        test_path: str
        if manual_path:
            print("    Generating path from manual input and zipfile name.")
            test_path = str(Path(manual_path).joinpath(input_file.stem))
        else:
            print("    Removing file extension...")
            test_path = str(input_file.with_suffix(''))

        ends_in_a_number: bool

        try:
            last_number = test_path.split()[-1]
            iteration_number = int(last_number)

        except (ValueError, IndexError):
            iteration_number = 1
            ends_in_a_number = False
        else:
            ends_in_a_number = True

        print("    Checking if there is already a directory by the same name as the zip file...")
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


# Create output folder
def create_output_directory(output_file: Path, mode: str):
    print("Creating output directory...")
    print("    Checking if mode preference was expressed...")

    if not mode:
        print("    Creating directory...")
        output_file.mkdir()

    else:
        try:
            mode_int = int(mode)

        except ValueError:
            print(Back.RED + Fore.BLACK + Style.BRIGHT + mode, "is not a valid unix permission level."
                  + Style.RESET_ALL)
            exit(1)
        else:
            print("    Creating directory...")
            output_file.mkdir(mode_int)
    print("Output directory created.")


# Unzip documents into folder
def unzip_file(input_file: str, output_file: Path):
    print("Unzipping files into output directory...")
    try:
        print("    Extracting...")
        zipfile.ZipFile(input_file, 'r').extractall(output_file)

    except (zipfile.BadZipFile, FileNotFoundError):
        print(Back.RED + Fore.BLACK + Style.BRIGHT + input_file,
              "does appear to be a valid zip file." + Style.RESET_ALL)
        if new_dir:
            output_file.rmdir()
        exit(1)

    except PermissionError:
        print(Back.RED + Fore.BLACK + Style.BRIGHT + "Permission level ", "makes the input file or output directory "
                                                                          "inaccessible to this script. Try running "
                                                                          "as root." + Style.RESET_ALL)

        output_file.rmdir()
        exit(1)

    print(Back.GREEN + Fore.BLACK + Style.BRIGHT + "    ", input_file, " unzipped to ", str(output_file), " in ",
          time.time() - startTime, "seconds (including user input)." + Style.RESET_ALL)


if __name__ == "__main__":

    # Process arguments from call
    parser = argparse.ArgumentParser(description="Unzips files.")
    parser.add_argument("input", metavar="Zip file path", type=str, help="Path of file to unzip")
    parser.add_argument("--output", metavar="Output directory path", type=str,
                        help="Path of directory to unzip files to (Defaults to same as input).")
    parser.add_argument("-nd", action="store_true",
                        help="Places unzipped files into new directory with same name as zip file(Defaults to false).")
    parser.add_argument("--mode", metavar="Permission", type=str, help="Unix permission level (Defaults to 777)")
    args = parser.parse_args()

    # Create input variables
    zip_file_path = args.input
    output_file_path = args.output
    new_dir = args.nd
    output_mode = args.mode

    # Use inputs to unzip file correctly
    output_path: Path = generate_output_path(Path(zip_file_path), output_file_path)
    if new_dir:
        create_output_directory(output_path, output_mode)
    elif output_mode:
        print(Back.YELLOW + Fore.BLACK + Style.BRIGHT + "Mode preference will be ignored, since a new directory was "
                                                        "not requested." + Style.RESET_ALL)
    unzip_file(zip_file_path, output_path)
