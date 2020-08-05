from pathlib import Path
import PyPDF2
import nxttxt
import time


def touch_files(pdf_paths: list, output_path: Path) -> list:
    paths: list = []
    for pdf_path in pdf_paths:
        txt_path = nxttxt.enumerate_duplicate_paths(output_path / Path(pdf_path.stem).with_suffix(".txt"))
        txt_path.touch()
        paths.append({
            "pdf": pdf_path,
            "txt": txt_path
        })
    return paths


def verify_pdfs(paths: list) -> list:
    updated_paths: list = []
    for path in paths:
        pdf_reader = PyPDF2.PdfFileReader(str(path["pdf"]))
        try:
            page_max_index = pdf_reader.getNumPages() - 1
        except PyPDF2.utils.PdfReadError:
            if pdf_reader.isEncrypted:
                print("   ", path["pdf"], "is encrypted and cannot be extracted. If you would like this file to be "
                                          "extracted, please decrypt the file and run the extraction again.")
            else:
                print("    There was a error reading", path["pdf"], "the file may be corrupted so it will be skipped.")
            path["txt"].unlink()
        else:
            path["page max index"] = page_max_index
            updated_paths.append(path)
    return updated_paths


def extract_text(paths: list, max_extraction_time: float):
    print("Extracting text...")
    for path in paths:
        pdf_reader = PyPDF2.PdfFileReader(str(path["pdf"]))
        page: int = 0
        extracted_text: str = ""
        start_time = time.time()
        while page <= path["page max index"]:
            if max_extraction_time and (start_time + max_extraction_time) < time.time():
                print(path["pdf"], "timed out after extracting", page, "/", (path["page max index"] + 1), "pages. To "
                                                                                                          "extract "
                                                                                                          "the full "
                                                                                                          "document "
                                                                                                          "run the "
                                                                                                          "command "
                                                                                                          "again with "
                                                                                                          "a longer "
                                                                                                          "or "
                                                                                                          "nonexistent "
                                                                                                          "time limit.")
                break
            extracted_text += "\n\n" + pdf_reader.getPage(page).extractText()
            page += 1
        path["txt"].write_text(extracted_text)
    print("PDFs extracted to", str(paths[0]["txt"].parent))
