import time
import textract
import statistics
from pathlib import Path
import functools


def timer(func):
    """Prints the runtime of the decorated function."""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer


@timer
def extract(pdf_name, method_name):
    text_extracted = textract.process(pdf_name, method=method_name)
    return text_extracted


methods = ["tesseract", "pdftotext", "pdfminer"]
file: Path = Path("/Users/jamiepickar/Downloads/pdfs")

for method in methods:
    rates: [int] = []
    for pdf in file.iterdir():
        start_time = time.time()
        text = extract(pdf, method)
        time_per_byte = pdf.stat().st_size / (time.time() - start_time)
        rates.append(time_per_byte)
        #print("   ", method, ":", time_per_byte, "bytes per second.")
    mean: float = statistics.mean(rates)
    stdev: float = statistics.stdev(rates)
    print(method, "had an average rate of", mean, "bytes per second with a standard deviation of", stdev, ".")
print("Done!")
