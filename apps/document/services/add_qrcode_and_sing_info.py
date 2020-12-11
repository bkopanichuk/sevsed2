import os
import PyPDF2
import tempfile
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab_qrcode import QRCodeImage


class AddQRCode2PDF():
    def __init__(self, input_file, qrcode_data, add_new_page=True):
        self.input_file = input_file
        self.output_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
        self.qrcode_data = qrcode_data
        self.add_new_page = add_new_page

    def run(self):
        qrcode_path = self.generate_qrcode()
        self.add_qrcode(qrcode_path)
        self.replace_docs()
        os.unlink(qrcode_path)

    def replace_docs(self):
        os.unlink(self.input_file)
        os.rename(self.output_file, self.input_file)
        os.chmod(self.input_file, 0o444)

    def generate_qrcode(self):
        qrcode_path = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
        doc = Canvas(qrcode_path)
        qr = QRCodeImage(fill_color='black', back_color='white', size=25 * mm)
        qr.add_data(self.qrcode_data)
        qr.drawOn(doc, 10 * mm, 10 * mm)
        textobject = doc.beginText()
        textobject.setTextOrigin(55* mm, 25*mm)
        textobject.setFont("Times-Roman", 12)
        textobject.textLine("SPUMONI")
        textobject.textLine("asdadad 54646 dsaa ")
        textobject.textLine("dsadadadadsadadadadad вфіфвіфвфі")
        doc.drawText(textobject)

        doc.showPage()
        doc.save()
        return qrcode_path

    def add_qrcode(self, qrcode_path):
        with open(self.input_file, "rb") as filehandle_input:
            pdf = PyPDF2.PdfFileReader(filehandle_input)
            with open(qrcode_path, "rb") as filehandle_watermark:
                watermark = PyPDF2.PdfFileReader(filehandle_watermark)
                pdf_writer = PyPDF2.PdfFileWriter()
                first_page_watermark = watermark.getPage(0)
                first_page = pdf.getPage(0)
                if not self.add_new_page:
                    first_page.mergePage(first_page_watermark)
                pdf_writer.addPage(first_page)
                for page_n in range(1, pdf.getNumPages()):
                    page = pdf.getPage(page_n)
                    pdf_writer.addPage(page)
                if self.add_new_page:
                    pdf_writer.addPage(first_page_watermark)
                with open(self.output_file, "wb") as filehandle_output:
                    pdf_writer.write(filehandle_output)
