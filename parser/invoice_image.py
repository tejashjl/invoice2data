import cv2


class InvoiceImage:
    raw_image = ""

    def __init__(self, invoice_path, page_number):
        self.raw_image = cv2.imread(invoice_path)
        self.page_number = page_number

    def gray_image(self):
        return cv2.cvtColor(self.raw_image, cv2.COLOR_BGR2GRAY)

    def resize_image(self, fx=4, fy=4):
        return cv2.resize(self.raw_image, (0, 0), fx=fx, fy=fy)
