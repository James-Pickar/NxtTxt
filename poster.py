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


def analyze_txts(txt_file_paths: list, address: str, port: int, final_format: str):
    url: str
    if not port:
        url = "http://" + address + ":8080/api/v1/articles/analyzeText"
    else:
        url = "http://" + address + ":" + str(port) + "/api/v1/articles/analyzeText"

    server_active = server_is_active(url)
    if not server_active[0]:
        print(server_active[1])
        exit(1)
    analyzed_txts: dir = {}
    headers = {
        "Content-type": "text/plain",
        "Accept": final_format,
    }
    for txt_file_path in txt_file_paths:
        data = open(str(txt_file_path), "rb").read()
        response = requests.post(url, headers=headers, data=data)
        analyzed_txts.update([(txt_file_path, response)])
    return analyzed_txts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sends all .txt files trough the sa-engine.")
    parser.add_argument("input", metavar="Input directory path", type=str, help="Path of directory with .TXTs to "
                                                                                "extract.")
    parser.add_argument("address", metavar="Server address", type=str, help="Address of server on which the sa-engine "
                                                                            "is running.")
    parser.add_argument("-p", metavar="Server port", type=int, help="Port of server on which the sa-engine "
                                                                    "is running. Defaults to 8080.")
    parser.add_argument("-f", metavar="Output format", type=str, help="The output type of the request, either xml or "
                                                                      "json. Defaults to xml")
    args = parser.parse_args()

    files = determine_txts(args.input)
    output_format = determine_format(args.f)
    analysis = analyze_txts(files, args.address, args.p, output_format)
