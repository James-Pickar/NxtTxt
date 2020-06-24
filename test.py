import PyPDF2

pdf_reader = PyPDF2.PdfFileReader("/Users/jamiepickar/Downloads/pdfs/Aluminum_Corp_of_China.pdf")
page_max_index = pdf_reader.getNumPages() - 1
page: int = 0
extracted_text: str = ""
while page <= page_max_index:
    extracted_text += "\n\n" + pdf_reader.getPage(page).extractText()
    #print("\n\n" + pdf_reader.getPage(page).extractText())
    page += 1
print(extracted_text)
