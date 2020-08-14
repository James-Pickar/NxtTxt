from pathlib import Path
import textract
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
        if pdf_reader.isEncrypted:
            print("   ", path["pdf"], "is encrypted and cannot be extracted. If you would like this file to be "
                                      "extracted, please decrypt the file and run the extraction again.")
            path["txt"].unlink()
            continue
        try:
            page_max_index = pdf_reader.getNumPages() - 1
        except PyPDF2.utils.PdfReadError:
            print("    There was a error reading", path["pdf"], "the file may be corrupted so it will be skipped.")
            path["txt"].unlink()
        else:
            path["page max index"] = page_max_index
            updated_paths.append(path)
    return updated_paths


def extract_text(paths: list, max_extraction_time: float):
    print("Extracting text...")
    for path in paths:
        time_limit = time.time() + max_extraction_time
        extracted_text: str = textract.process(path["pdf"], method="tesseract")
        if time_limit < time.time():
            print(path["pdf"], "timed out. What was extracted will be written to", path["txt"], "To extract the full "
                                                                                                "document run the "
                                                                                                "command again with a "
                                                                                                "longer or "
                                                                                                "nonexistent time "
                                                                                                "limit.")
        path["txt"].write_text(extracted_text)
    print("PDFs extracted to", str(paths[0]["txt"].parent))
