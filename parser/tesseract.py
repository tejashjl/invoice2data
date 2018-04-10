import io
import os
import cv2
import subprocess
from PIL import Image
from wand.image import Image as wi
from parser.utils import temporary_file_name, cleanup
from PyPDF2 import PdfFileMerger


class Tesseract:
    pdf_file_paths = []
    imageBlobs = []
    pdf_merger = PdfFileMerger()

    def __init__(self):
        self.pdf_file_paths = []
        self.pdf_merger = PdfFileMerger()
        self.imageBlobs = []

    def to_pdf(self, invoice_path, file_type):
        if file_type == 'PDF_WITH_IMAGE':
            self.pdf_to_image_blobs(invoice_path)
        if file_type == 'IMAGE':
            self.to_image_blobs(invoice_path)
        self.blobs_to_pdf()
        return self.merge_pdf()

    def merge_pdf(self):
        for pdf in self.pdf_file_paths:
            self.pdf_merger.append(pdf)
        invoice_pdf_file_path = '%s.pdf' % temporary_file_name(prefix="pdf_")
        self.pdf_merger.write(invoice_pdf_file_path)
        if os.path.exists(invoice_pdf_file_path):
            return invoice_pdf_file_path

    def to_image_blobs(self, invoice_path):
        invoice_path = self.pre_process_image(invoice_path)
        self.imageBlobs = []
        imgPage = wi(
            image=wi(filename=invoice_path, resolution=400, depth=8, background="white").convert('jpeg'))
        self.imageBlobs.append(imgPage.make_blob('jpeg'))

    @staticmethod
    def pre_process_image(invoice_path):
        image = cv2.imread(invoice_path)
        image = cv2.resize(image, (0, 0), fx=4, fy=4)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if True:
            gray = cv2.threshold(gray, 0, 255,
                                 cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        if False:
            gray = cv2.medianBlur(gray, 3)
        filename = "{}.png".format(temporary_file_name())

        cv2.imwrite(filename, gray)
        return filename

    def pdf_to_image_blobs(self, invoice_path):
        self.imageBlobs = []
        with wi(filename=invoice_path, resolution=400, depth=8) as invoiceImg:
            with invoiceImg.convert('jpeg') as pdfImages:
                for pdfImage in pdfImages.sequence:
                    imgPage = wi(image=pdfImage)
                    self.imageBlobs.append(imgPage.make_blob('jpeg'))

    def blobs_to_pdf(self):
        for image_blob in self.imageBlobs:
            self.run_tesseract(Image.open(io.BytesIO(image_blob)))

    def run_tesseract(self, image):
        input_file_name = '%s.bmp' % temporary_file_name()
        output_file_name_base = '%s' % temporary_file_name()
        output_file_name = '%s.pdf' % output_file_name_base
        image.save(input_file_name)
        tesseract_command = ["tesseract", input_file_name, output_file_name_base, '--psm', '11', '-l', "eng+deu", "pdf"]
        tesseract_command_txt = ["tesseract", input_file_name, output_file_name_base, '-l', "eng+deu"]
        subprocess.Popen(tesseract_command, stderr=subprocess.PIPE).communicate()
        subprocess.Popen(tesseract_command_txt, stderr=subprocess.PIPE).communicate()
        # cleanup(input_file_name)
        if os.path.exists(output_file_name):
            self.pdf_file_paths.append(output_file_name)
