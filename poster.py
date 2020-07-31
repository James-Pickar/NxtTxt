import requests
import argparse
from pathlib import Path


# "Modular" functions
def get_mode(input_mode: str):
    output_mode: int = 0o777
    if not input_mode:
        return output_mode
    try:
        int(input_mode)
    except ValueError:
        print(input_mode, "is not a valid unix permission level.")
        exit(1)
    else:
        output_mode = int("0o" + input_mode)
    return output_mode


def server_is_active(url: str):
    state_of_the_server: list
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError:
        state_of_the_server = [False, "Connection to server failed. Please check that your instance is active."]
    except requests.exceptions.Timeout:
        state_of_the_server = [False, "Connection Timed Out."]
    except requests.exceptions.TooManyRedirects:
        state_of_the_server = [False, "The address entered causes too many redirects."]
    except requests.exceptions.RequestException:
        state_of_the_server = [False, "There was an unknown issue with the server. Please check that engine is "
                                      "working properly."]
    else:
        state_of_the_server = [True, "Success!"]
    return state_of_the_server


def enumerate_duplicate_paths(start_path: Path):
    parent = start_path.parent
    suffix = "".join(start_path.suffixes)
    test_path = start_path.with_suffix('').name

    ends_in_a_number: bool = True

    try:
        iteration_number = int(test_path.split()[-1])

    except (ValueError, IndexError):
        iteration_number = 1
        ends_in_a_number = False

    print("    Generating name...")
    while ((parent / test_path).with_suffix(suffix)).exists():
        if ends_in_a_number:
            test_path = test_path.split()[:-1][0]
        test_path += " " + str(iteration_number + 1)
        ends_in_a_number = True
        iteration_number += 1

    return (parent / test_path).with_suffix(suffix)


# "Procedural" functions
def determine_txts(input_dir):
    input_path = Path(input_dir)
    if not input_path.exists():
        print(input_dir, "is not a valid path.")
        exit(1)
    elif not input_path.is_dir():
        print(input_dir, "is not a directory, it is either a file, or it is a broken symbolic link.")
        exit(1)

    txt_working_list: list = []
    for child in input_path.iterdir():
        if child.suffix == ".txt":
            txt_working_list.append(child)
    return txt_working_list


def determine_format(requested_format: str):
    input_format = "application/xml"
    if requested_format:
        if (requested_format == "xml") or (requested_format == "json"):
            input_format = "application/" + requested_format
        else:
            print(requested_format, "is not a valid format. Please enter either xml or json.")
            exit(1)
    return input_format


def determine_url(address: str, port: int):
    url: str
    if not port:
        url = "http://" + address + ":8080/api/v1/articles/analyzeText"
    else:
        url = "http://" + address + ":" + str(port) + "/api/v1/articles/analyzeText"

    server_active = server_is_active(url)
    if not server_active[0]:
        print(server_active[1])
        exit(1)
    return url


def analyze_txts(txt_file_paths: list, url: str, final_format: str):
    analyzed_txts: dir = {}
    headers = {
        "Content-type": "text/plain",
        "Accept": final_format,
    }
    for txt_file_path in txt_file_paths:
        data = open(str(txt_file_path), "rb").read()
        response = requests.post(url, headers=headers, data=data)
        analyzed_txts.update([(txt_file_path.name, response)])
    return analyzed_txts


def determine_output_path(input_dir: str, output_dir: str, new_dir: bool):
    final_output_path: Path
    if output_dir:
        preliminary_output_path = Path(output_dir)
        if not preliminary_output_path.exists():
            print(output_dir, "does not exist. Please enter an exist output directory if you wish to manually select "
                              "one.")
            exit(1)
        if new_dir:
            # do enumeration
            final_output_path = Path("")
        else:
            final_output_path = preliminary_output_path
    else:
        if new_dir:
            # do enumeration
            final_output_path = Path("")
        else:
            final_output_path = Path(input_dir)
    return final_output_path


def touch_files(analysis_list: list, directory_path: Path, mode: int):
    for analysis_path in analysis_list:
        created_path = directory_path.joinpath(analysis_path)
        created_path.touch(mode)
        # analysis_list[analysis_path].key


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sends all .txt files trough the sa-engine and writes the analysis "
                                                 "to a new set of txts.")
    parser.add_argument("input", metavar="Input directory path", type=str, help="Path of directory with .TXTs to "
                                                                                "extract.")
    parser.add_argument("address", metavar="Server address", type=str, help="Address of server on which the sa-engine "
                                                                            "is running.")
    parser.add_argument("-p", metavar="Server port", type=int, help="Port of server on which the sa-engine "
                                                                    "is running. Defaults to 8080.")
    parser.add_argument("-f", metavar="Output format", type=str, help="The output type of the request, either xml or "
                                                                      "json. Defaults to xml")
    parser.add_argument("-nd", action="store_true", help="Places analyzed text files into new directory with same "
                                                         "name as original directory but with 'analyzed txts' on the "
                                                         "end(Defaults to false).")
    parser.add_argument("--output", metavar="Output directory path", type=str, help="Path of directory to place "
                                                                                    "analyzed txts into files to ("
                                                                                    "Defaults to same as input).")
    args = parser.parse_args()

    files = determine_txts(args.input)
    output_format = determine_format(args.f)
    output_url = determine_url(args.address, args.p)
    analysis = analyze_txts(files, output_url, output_format)
    output_path = determine_output_path(args.input, args.output, args.nd)
