import json
import nxttxt
import requests
import argparse
from pathlib import Path


# "Modular" functions
def server_is_active(url: str) -> list:
    state_of_the_server: list
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError:
        state_of_the_server = [False, "Connection to server failed. Please check that your instance is active.", nxttxt.exceptions.ConnectionRejected]
    except requests.exceptions.Timeout:
        state_of_the_server = [False, "Connection Timed Out.", nxttxt.exceptions.ConnectionTimeout]
    except requests.exceptions.TooManyRedirects:
        state_of_the_server = [False, "The address entered causes too many redirects.", nxttxt.exceptions.TooManyRedirects]
    except requests.exceptions.RequestException:
        state_of_the_server = [False, "There was an unknown issue with the server. Please check that engine is "
                                      "working properly.", nxttxt.exceptions.UnknownConnectionError]
    else:
        state_of_the_server = [True, "Success!"]
    return state_of_the_server


# "Procedural" functions
def authenticate_instructional_validity(input_dir: str, output_dir: str) -> list:
    print("Authenticate validity of entered paths...")
    input_path = Path(input_dir)
    if nxttxt.is_valid_path(input_path, True) and output_dir and \
            (not nxttxt.is_valid_path(Path(output_dir), True)):
        result = [False, "The specified output path is not valid.", nxttxt.exceptions.InvalidPath]
    elif not nxttxt.is_valid_path(input_path, False):
        result = [False, "The specified output path is not valid.", nxttxt.exceptions.InvalidPath]
    elif not nxttxt.is_valid_path(input_path, True):
        result = [False, "The specified input path is not a directory.", nxttxt.exceptions.PathIsNotADirectory]
    else:
        result = [True, None]
    return result


def determine_txts(input_dir: str) -> list:
    print("Identifying TXT files... ")
    input_path = Path(input_dir)
    txt_working_list: list = []
    print("    TXTs in", input_dir + ":")
    for child in input_path.iterdir():
        if child.suffix == ".txt":
            txt_working_list.append(child)
            print("       ", child)
    return txt_working_list


def determine_url(address: str, port: int) -> str:
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
        raise server_active[2]
    print("    Connection successful.")
    return url + "/api/v1/articles/analyzeText"


def read_txts(txt_file_paths: list) -> list:
    txts = []
    for txt_file_path in txt_file_paths:
        data = open(str(txt_file_path), "rb").read()
        txts.append({
            "txt_path": Path(txt_file_path.name),
            "data": data
        })
    return txts


def analyze_txts(txts: list, url: str) -> list:
    print("Requesting analysis...")
    analyzed_txts = []
    headers = {
        "Content-type": "text/plain",
        "Accept": "application/json"
    }
    for txt in txts:
        print("    Analyzing", str(txt["txt_path"]) + "...")
        response = requests.post(url, headers=headers, data=txt["data"])
        if response.status_code == requests.codes.ok:
            txt.update({
                "analysis": response,
                "analysis_path": txt["txt_path"].with_suffix(".json")
            })
            analyzed_txts.append(txt)
        else:
            print("    Request for analysis of", str(txt["txt_path"]), "failed with error code:", response.status_code)

    return analyzed_txts


def determine_output_path(input_dir: str, output_dir: str, new_dir: bool) -> Path:
    print("Identifying output directory...")
    final_output_path: Path
    if output_dir:
        final_output_path = Path(output_dir)
    elif new_dir:
        final_output_path = nxttxt.enumerate_duplicate_paths(Path(input_dir).parent / "sa-engine analysis")
    else:
        final_output_path = Path(input_dir).parent
    print("    Output directory will be", str(final_output_path) + ".")
    return final_output_path


def create_output_dir(output_dir: Path):
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        print("    Output directory created.")


def create_files(analysis_list: list, output_dir: Path):
    print("Creating analyzed files...")
    for analysis_dict in analysis_list:
        created_path = nxttxt.enumerate_duplicate_paths(output_dir.joinpath(analysis_dict["analysis_path"]))
        print("    Creating", str(created_path) + "...")
        created_path.touch()
        print("    Writing analysis...")
        created_path.write_text(json.dumps(analysis_dict["analysis"].json()))
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
    auth = authenticate_instructional_validity(args.input, args.output)
    if auth[0]:
        files = determine_txts(args.input)
        output_url = determine_url(args.address, args.p)
        text = read_txts(files)
        print(text)
        analysis = analyze_txts(text, output_url)
        output_path = determine_output_path(args.input, args.output, args.nd)

        create_output_dir(output_path)
        create_files(analysis, output_path)
        print("Process complete.")
    else:
        print(auth[1])
        raise auth[2]
