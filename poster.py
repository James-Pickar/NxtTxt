import json
import requests
import argparse
from pathlib import Path


# "Modular" functions
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
        print("iteration_number", iteration_number)

    except (ValueError, IndexError):
        iteration_number = 1
        ends_in_a_number = False

    print("    Generating name...")
    while ((parent / test_path).with_suffix(suffix)).exists():
        if ends_in_a_number:
            test_path = " ".join(test_path.split()[:-1])
        test_path += " " + str(iteration_number + 1)
        ends_in_a_number = True
        iteration_number += 1

    return (parent / test_path).with_suffix(suffix)


def retrieve_path_without_manual_output(input_dir: str, new_dir: bool):
    if new_dir:
        final_output_path = enumerate_duplicate_paths(Path(input_dir) / "sa-engine analysis")
    else:
        final_output_path = Path(input_dir)
    return final_output_path


# "Procedural" functions
def determine_txts(input_dir: str):
    print("Identifying TXT files... ")
    input_path = Path(input_dir)
    if not input_path.exists():
        print(input_dir, "is not a valid path.")
        exit(1)
    elif not input_path.is_dir():
        print(input_dir, "is not a directory, it is either a file, or it is a broken symbolic link.")
        exit(1)

    txt_working_list: list = []
    print("    TXTs in", input_dir + ":")
    for child in input_path.iterdir():
        if child.suffix == ".txt":
            txt_working_list.append(child)
            print("       ", child)
    return txt_working_list


def determine_url(address: str, port: int):
    print("Identifying server...")
    url: str
    if not port:
        url = "http://" + address + ":8080"
    else:
        url = "http://" + address + ":" + str(port)
    print("    Attempting to connect to", url + "...")
    server_active = server_is_active(url + "/management/health")
    if not server_active[0]:
        print(server_active[1])
        exit(1)
    print("    Connection successful.")
    return url + "/api/v1/articles/analyzeText"


def analyze_txts(txt_file_paths: list, url: str):
    print("Requesting analysis...")
    analyzed_txts: dir = {}
    headers = {
        "Content-type": "text/plain",
        "Accept": "application/json"
    }
    for txt_file_path in txt_file_paths:
        data = open(str(txt_file_path), "rb").read()
        print("    Analyzing", str(txt_file_path) + "...")
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == requests.codes.ok:
            analyzed_txts.update([(txt_file_path.with_suffix(".json").name, response)])
        else:
            print("    Request for analysis of", str(txt_file_path), "failed with error code:", response.status_code)

    return analyzed_txts


def determine_output_path(input_dir: str, output_dir: str, new_dir: bool):
    print("Identifying output directory...")
    final_output_path: Path
    if output_dir:
        if not Path(output_dir).exists():
            print(output_dir, "does not exist. Please enter an exist output directory if you wish to manually select "
                              "one.")
            exit(1)
        final_output_path = Path(output_dir)
    else:
        final_output_path = retrieve_path_without_manual_output(input_dir, new_dir)
    print("    Output directory will be", str(final_output_path) + ".")
    return final_output_path


def create_output_dir(output_dir: Path):
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        print("    Output directory created.")


def create_files(analysis_list: dir, output_dir: Path):
    print("Creating analyzed files...")
    for analysis_path in analysis_list:
        created_path = enumerate_duplicate_paths(output_dir.joinpath(analysis_path))
        print("    Creating", str(created_path) + "...")
        created_path.touch()
        print("    Writing analysis...")
        created_path.write_text(json.dumps(analysis_list[analysis_path].json()))
    print("    Analysis complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sends all .txt files trough the sa-engine and writes the analysis "
                                                 "to a new set of txts.")
    parser.add_argument("input", metavar="Input directory path", type=str, help="Path of directory with .TXTs to "
                                                                                "extract.")
    parser.add_argument("address", metavar="Server address", type=str, help="Address of server on which the sa-engine "
                                                                            "is running.")
    parser.add_argument("-p", metavar="Server port", type=int, help="Port of server on which the sa-engine "
                                                                    "is running. Defaults to 8080.")
    parser.add_argument("-nd", action="store_true", help="Places analyzed text files into new directory with same "
                                                         "name as original directory but with 'analyzed txts' on the "
                                                         "end(Defaults to false).")
    parser.add_argument("-output", metavar="Output directory path", type=str, help="Path of directory to place "
                                                                                   "analyzed txts into files to ("
                                                                                   "Defaults to same as input).")

    args = parser.parse_args()
    files = determine_txts(args.input)
    output_url = determine_url(args.address, args.p)
    analysis = analyze_txts(files, output_url)
    output_path = determine_output_path(args.input, args.output, args.nd)
    create_output_dir(output_path)
    create_files(analysis, output_path)
    print("Process complete.")
