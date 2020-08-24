import unzip
import extract
import poster
from pathlib import Path


def unzip_drive(unzip_input: str, output: str, nd: bool):
    auth = unzip.authenticate_instructional_validity(unzip_input, output)
    if auth[0]:
        output_path: Path = unzip.generate_output_path(unzip_input, output, nd)
        unzip.create_output_directory(output_path, output, nd)
        unzip.unzip_file(unzip_input, output_path, nd)
    else:
        print(auth[1])


def extract_drive(extract_input: str, output: str, nd: bool, timeout: int):
    auth = extract.authenticate_instructional_validity(extract_input, output)
    if auth[0]:
        pdfs = extract.determine_pdfs(extract_input)
        output_dir_path = extract.generate_output_path(Path(extract_input), output, nd)

        extract.create_output_directory(output_dir_path, pdfs)
        paths_list = extract.touch_files(pdfs, output_dir_path)
        extract.extract_text(paths_list, timeout)
    else:
        print(auth[1])


def poster_drive(poster_input: str, output: str, nd: bool, port: int, address: str):
    auth = poster.authenticate_instructional_validity(poster_input, output)
    if auth[0]:
        files = poster.determine_txts(poster_input)
        output_url = poster.determine_url(address, port)
        analysis = poster.analyze_txts(files, output_url)
        output_path = poster.determine_output_path(poster_input, output, nd)

        poster.create_output_dir(output_path)
        poster.create_files(analysis, output_path)
        print("Process complete.")
    else:
        print(auth[1])


if __name__ == "__main__":
    pass
