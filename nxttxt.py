from pathlib import Path


def is_valid_path(path: Path, should_be_dir: bool) -> bool:
    if not path.exists():
        return False
    if should_be_dir:
        if path.is_dir():
            return True
        return False
    return True


def enumerate_duplicate_paths(start_path: Path) -> Path:
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
            test_path = " ".join(test_path.split()[:-1])
        test_path += " " + str(iteration_number + 1)
        ends_in_a_number = True
        iteration_number += 1

    return (parent / test_path).with_suffix(suffix)


def authenticate_instructional_validity(input_file: str, manual_output: str) -> list:
    input_path = Path(input_file)
    if is_valid_path(input_path, False):
        if not manual_output:
            return [True, None]
        if is_valid_path(Path(manual_output), True):
            return [True, None]
        return [False, "The specified output path is not valid."]
    return [False, "The zipfile path entered is not valid."]