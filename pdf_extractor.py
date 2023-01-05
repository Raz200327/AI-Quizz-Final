import PyPDF2
import pypandoc
import docx2txt
import os


class DocExtract:
    def pdf_to_string(self, path):
        # Open the PDF file in read-binary mode
        with open(path, "rb") as file:
            # Create a PDF object
            pdf = PyPDF2.PdfReader(file)

            # Extract the text from each page of the PDF
            text = ""
            for page in range(len(pdf.pages)):
                print(pdf.pages[page])
                text += pdf.pages[page].extract_text()
            print(text)
            os.remove(path)
        return text


    def docx_to_string(self, path):
        # Extract text from docx file
        text = docx2txt.process(path).replace("\n", " ").strip()
        os.remove(path)
        return text

