import logging
import os
import tempfile

import PyPDF2
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab_qrcode import QRCodeImage

pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))

logger = logging.getLogger(__name__)

class AddQRCode2PDF():
    def __init__(self, input_file, qrcode_data, add_new_page=True, signers_data=None):
        if signers_data is None:
            signers_data = []

        self.signers_data = signers_data
        self.input_file = input_file
        self.output_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
        self.qrcode_data = qrcode_data
        self.add_new_page = add_new_page

    def run(self):
        qrcode_path = self.generate_register_page()
        self.add_qrcode(qrcode_path)
        self.replace_docs()
        os.unlink(qrcode_path)

    def replace_docs(self):
        os.unlink(self.input_file)
        os.rename(self.output_file, self.input_file)
        os.chmod(self.input_file, 0o444)

    def generate_register_page(self):
        qrcode_path = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
        doc = Canvas(qrcode_path)
        self.generate_qrcode(doc)
        self.set_sign_text(doc)
        ##doc.showPage()
        doc.save()
        return qrcode_path

    def generate_qrcode(self, doc):
        qr = QRCodeImage(fill_color='black', back_color='white', size=25 * mm)
        qr.add_data(self.qrcode_data)
        qr.drawOn(doc, 10 * mm, 10 * mm)

    def set_sign_text(self, doc):
        textobject = doc.beginText()
        _upper_pending = len(self.signers_data) or 1
        textobject.setTextOrigin(40 * mm, _upper_pending * 25 * mm)
        textobject.setFont('FreeSans', 8)
        textobject.textLine("СЕВ СЕД 2.0")
        logger.warning(self.signers_data)
        for sign in self.signers_data:
            textobject.textLine(f'Підписант: {sign.get("pszSubjFullName")}')
            textobject.textLine(f'Серійний номер: {sign.get("pszSerial")}')
            textobject.textLine(f'Дата підписання: {sign.get("Time")}')
        doc.drawText(textobject)

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
