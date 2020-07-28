import os

print("Start!")
methods = ["tesseract", "pdftotext", "pdfminer"]


time_per_byte = os.path.getsize("/Users/jamiepickar/Downloads/pdfs/Alcoa.pdf")
print(time_per_byte, "bytes.")

print("Finished!")
exit(0)
